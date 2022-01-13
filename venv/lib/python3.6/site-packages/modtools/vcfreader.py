'''
The new module of reading vcf files

Created on Sep 9, 2013

@author: Shunping Huang
'''

import os
import pysam
import gzip
import collections

CHR = 0
POS = 1
REF = 3
ALT = 4
FMT = 8

GT        = 'GT'
REF_ALIAS = '.'
ALT_FS    = ','
FS        = '\t'
FMT_FS    = ':'
FILTER    = 'FI'


__all__ = ['parseFormat', 'getGenotype', 'parseGenotype', 'VCFIterator',
           'VCFReader']

VERBOSE = 1


def parseFormat(fmt, data):
    '''
    Parse the data for based on the format field

    e.g. GT:FI  0/0:1  => {'GT':'0/0', 'FI':'1'}
    '''

    formatFields = fmt.split(FMT_FS)
    dataFields = data.split(FMT_FS)
    ret = dict()
    for i in range(min(len(formatFields), len(dataFields))):
        ret[formatFields[i]] = dataFields[i]
    return ret


def getGenotype(genotypeStr):
    '''
    Return genotype index array from genotype string.
    Indices are separated by / or |

    e.g. '0/1' => ['0','1']
    '''

    if '/' in genotypeStr:  # Unphased
        return genotypeStr.split('/')
    if '|' in genotypeStr:  # Phased
        return genotypeStr.split('|')
    return [genotypeStr]


def parseGenotype(ref, alt, genotype):
    '''Given the genotype index, return the genotype bases'''

    altFields = alt.split(ALT_FS)
    if genotype == '0':
        return ref
    else:
        return altFields[int(genotype) - 1]


class VCFIterator:
    '''Return iterator of tuples (chrom, pos, ref, sample_alt, ...)'''

    def __init__(self, parent, fetched, use_filter):
        self.parent = parent
        self.fetched = fetched
        self.use_filter = use_filter  # high confidence calls only

    def __iter__(self):
        return self

    def next(self):
        for line in self.fetched:
            line = line.rstrip()
            fields = line.split(FS)
            if len(fields) != self.parent.nColumns:
                raise ValueError("Number of columns not matched at line: %s" %
                                 line)

            genotypes = []
            for i in self.parent.sampleIndexes:
                fmtFields = parseFormat(fields[FMT], fields[i])

                if self.use_filter and FILTER in fmtFields:
                    # FI flag: 0 (low confidence), 1 (high confidence)
                    pass_filter = True if fmtFields[FILTER] == '1' else False
                else:
                    # Assume it is a pass if high confidence is not required
                    # or FILTER field is not found
                    pass_filter = True

                if pass_filter:
                    #print("passed")
                    genotype = getGenotype(fmtFields[GT])
                else:
                    #print("failed")
                    genotype = ['.']  # replaced with ref allele if not passed

                if len(set(genotype)) > 1:
                    if VERBOSE:
                        #print(i)
                        #print(self.parent.all_samples)
                        print("Hets found in %s:%s of sample %s (%s). " %
                              (fields[CHR], fields[POS],
                               self.parent.all_samples[i - FMT - 1],
                               fmtFields[GT]) +
                              "Use the first allele.")
                genotype = genotype[0]
                if genotype == REF_ALIAS:
                    genotype = '0'
                genotypes.append(genotype)

            #print(genotypes)

            # For only one sample, append a dummy ref genotype to compare
            if len(self.parent.sampleIndexes) == 1:
                genotypes.append('0')

            # Check whether this is a variant:
            # If only one sample is requested, it will be a variant if the
            # sample genotype is different from the reference genotype (0).
            # If more than one sample are requested, it will be a variant if
            # the samples have different genotype. In this case, if all samples
            # have the same genotype but different from the reference, it does
            # NOT count as a variant.
            for i in range(len(genotypes) - 1):
                if genotypes[i] != genotypes[i + 1]:
                    break  # this is a variant
            else:
                continue   # this is not a variant

            # Remove the dummy ref genotype
            if len(self.parent.sampleIndexes) == 1:
                del genotypes[-1]

            ret = []
            ret.append(fields[CHR])
            ret.append(int(fields[POS]) - 1)  # convert from 1-based to 0-based
            ret.append(fields[REF])
            ret.extend([parseGenotype(fields[REF], fields[ALT], genotype)
                        for genotype in genotypes])
            return ret
        else:
            raise StopIteration()

    __next__ = next  # for Python 3 compat


class VCFReader():
    '''
    Reader class for VCF format
    '''
    def __init__(self, fileName, samples):
        '''
        Initialize the reader.

        If only one sample is requested, it will be a variant if the
        sample allele is different from the reference allele (0).

        If more than one sample are requested, it will be a variant if
        genotypes from samples are not the same. In other words, if all
        samples have the same genotype but different from the reference,
        it will still NOT count as a variant.
        '''

        self.samples = samples
        self.sampleIndexes = []
        self.nColumns = 0

        if fileName.endswith('.vcf'):
            # Compress with bgzip
            if not os.path.isfile(fileName + '.gz'):
                pysam.tabix_compress(fileName, fileName + '.gz')
            fileName += '.gz'
        elif fileName.endswith('.vcf.gz'):
            pass
        else:
            raise ValueError("Wrong suffix of file '%s'", fileName)

        # Build tabix index
        if not os.path.isfile(fileName + '.tbi'):
            pysam.tabix_index(fileName, preset='vcf')

        nLines = 0
        fp = gzip.open(fileName, 'r')
        line = fp.readline()
        line = line.decode('utf-8')

        while line:
            nLines += 1
            if line.startswith('##'):
                line = fp.readline()
                line = line.decode('utf-8')
            elif line.startswith('#'):  # Header line
                break
            else:
                line = None        # Content line, no header line found
        else:
            raise ValueError("Header line (starting with a '#') not found.")

        # Get the column index of selected samples
        headers = line[1:].rstrip().split(FS)
        self.nColumns = len(headers)
        if self.nColumns <= 9:
            raise ValueError("Not enough columns in header.")

        for name in self.samples:
            if name in headers[9:]:
                self.sampleIndexes.append(headers.index(name))
            else:
                raise ValueError("Sample '%s' not found in header. " % name +
                                 "Expected sample name(s): %s." %
                                 ', '.join(headers[9:]))

        self.all_samples = headers[9:]
        self.tabix = pysam.Tabixfile(fileName)
        self.tabix_chroms = set([c.decode('utf-8')
                                 for c in self.tabix.contigs])
        self.fileName = fileName

    def fetch(self, region, use_filter=True):
        region = str(region)
        return VCFIterator(self, self.tabix.fetch(region=region), use_filter)


# if __name__ == '__main__':
#     vcf = VCFReader('./tests/test.vcf', ['129S1'])
#     n = 0
#     for line in vcf.fetch('1'):
#         n += 1
#         print(line)

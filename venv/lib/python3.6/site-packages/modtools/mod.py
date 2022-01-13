'''
The new module for MOD files.

Created on Aug 30, 2013

@author: Shunping Huang
'''

from __future__ import print_function

import os
import gc
import gzip
import subprocess  # for Popen
import pysam

from modtools.alias import Alias
from modtools.refmeta import RefMeta
from modtools.posmap import PosMap
from modtools.fareader import FaReader
from modtools.utils import *

VERSION = '0.2.0'
VERBOSE = 0

__all__ = ['Mod', 'VERSION']


class Mod:
    '''The class for parsing a piece of a mod file from the same chromosome.'''

    def __init__(self, fileName, checkMode=True):
        self.fileName = fileName
        if checkMode:
            self.check_and_fix()
            self.build_index(force=True)

        self.load_meta()

        #Initialize tabix engine
        self.tabix = pysam.Tabixfile(self.fileName)
        self.tabix_chroms = set([c.decode('utf-8')
                                 for c in self.tabix.contigs])
        #self.tabix_chroms = set([c for c in self.tabix.contigs])
        self.fetch = self.tabix.fetch

        #print(self.tabix_chroms)
        #for line in self.tabix.fetch('chr1'):
        #    print(line)

        self.chrom = None
        self.data = None
        self.posmap = None
        self.seq = None

    def check_and_fix(self):
        '''Check file existence, permission, and suffix.'''
        '''Try to fix it if necessary'''

        is_file_readable(self.fileName)
        fp = open(self.fileName, 'rb')
        magic = fp.read(2)
        fp.close()

        # check magic chars of a bgzipped file
        is_gzipped = True if magic == b'\x1f\x8b' else False

        if is_gzipped:
            #print("Gzipped format found.")
            assert self.fileName.endswith('.mod') or \
                self.fileName.endswith('.mod.gz'), "Wrong file extension "\
                "for gzipped MOD format. Expected '.mod' or '.mod.gz'."

            tmp_name = self.fileName
            if tmp_name.endswith('.gz'):
                tmp_name = tmp_name[:-3]

            if self.fileName != tmp_name:
                os.rename(self.fileName, tmp_name)
                self.fileName = tmp_name

        else:  # Convert text MOD format (old) to bgzipped MOD format (new)
            #print("Non-gzipped format found.")
            assert self.fileName.endswith('.mod'), "Wrong file extension "\
                "for text MOD format. Expected '.mod'."

            tmp_name = self.fileName + '.gz'
            pysam.tabix_compress(self.fileName, tmp_name, force=True)

            is_file_readable(tmp_name)
            os.rename(tmp_name, self.fileName)

    def build_index(self, force=False):
        '''Build index of MOD format'''

        assert self.fileName.endswith('.mod'), "Wrong file extension. "\
            "Call check_and_fix() first."

        # Here we assume the MOD file is in bgzipped MOD format.
        # pysam.tabix_index() can make index on bgzipped MOD format,
        # it needs the '.gz' suffix to recognize it is gzipped.
        tmp_name = self.fileName[:-4] + '.gz'
        try:
            os.rename(self.fileName, tmp_name)
            pysam.tabix_index(tmp_name, force=True, seq_col=1, start_col=2,
                              end_col=2, meta_char='#', zerobased=True)
            if os.path.getsize(tmp_name + '.tbi') < 100: #something wrong with indexing
                print("Warning: abnormal index size. Rebuilding index ...")
                fp = self.bgz_open(tmp_name)
                with open(self.fileName[:-4], 'w') as txt_fp:
                    for line in fp:
                        txt_fp.write(line)
                self.bgz_close(fp)
                pysam.tabix_compress(self.fileName[:-4], tmp_name, force=True)
                pysam.tabix_index(tmp_name, force=True, seq_col=1, start_col=2,
                                  end_col=2, meta_char='#', zerobased=True)
                os.remove(self.fileName[:-4])
            is_file_writable(self.fileName + '.tbi', force)
            os.rename(tmp_name + '.tbi', self.fileName + '.tbi')
        finally:
            os.rename(tmp_name, self.fileName)

    def bgz_open(self, fn):
        '''Open a file in BGZF format'''
        try:
            fp = gzip.open(fn, 'r')
            init_pos = fp.tell()
            fp.readline()
            fp.seek(init_pos)
        except TypeError:
            # A bug reported in Python 2.7.4 and 3.3.1
            # http://bugs.python.org/issue17666

            # Use zcat to work around in *nix environment
            #print("Fallback to zcat")
            self._proc = {}
            tmp = subprocess.Popen(['zcat', fn], stdout=subprocess.PIPE)
            fp = tmp.stdout
            self._proc[fp] = tmp
        return fp

    def bgz_close(self, fp):
        '''Close a file in BGZF format'''
        try:
            self._proc[fp].kill()
        except AttributeError:
            pass
        except NameError:
            pass
        except KeyError:
            pass
        fp.close()

    def parse_meta_line(self, line):
        '''
        Parse the right side of '='
        Return a list of string if part is like '[xxxx,xxxx,xxxx]'.
        Otherwise, return a string.
        '''

        # Ignore the first '#' of each meta line
        parts = line[1:].split('=', 1)
        assert len(parts) > 1, "Missing '=' in meta line '%s'" % line

        key = parts[0].split('.', 1)  # a key has at most two levels
        if key[0] not in self.meta and len(key) > 1:
            self.meta[key[0]] = dict()

        if parts[1].startswith('[') and parts[1].endswith(']'):
            val = None
            if key[0] == 'refmeta':  # specify level fo reference
                val = RefMeta.parse(parts[1][1:-1])
            else:
                val = parts[1][1:-1].split(',') if len(parts[1]) > 2 else []
        else:
            val = parts[1]

        if len(key) > 1:
            self.meta[key[0]][key[1]] = val
        else:
            self.meta[key[0]] = val

    def load_meta(self):
        '''Load meta data (headers).'''

        assert self.fileName.endswith('.mod'), "Wrong file extension. "\
            "Call check_and_fix() first."
        assert os.path.isfile(self.fileName + '.tbi'), "Index not found. "\
            "Call build_index() first."

        # Load meta data
        bgz_fp = self.bgz_open(self.fileName)
        self.meta = dict()
        for line in bgz_fp:
            line = line.decode('utf-8').strip()
            if not line.startswith('#'):
                break
            if len(line) == 0:
                continue
            self.parse_meta_line(line)

        #print(self.meta)
        self.bgz_close(bgz_fp)

        #assert 'refmeta' in self.meta, "Required 'refmeta' field not found."
        # for backward compatibility, if no refmeta, assume it is mm9 reference
        if 'refmeta' not in self.meta:
            print("Warning: Required 'refmeta' field not found. Using mm9 genome as reference")
            mm9_meta = dict()
            mm9_meta['1']  = RefMeta('chr1', '197195432', 'f05d753079c455c0e57af88eeda24493')
            mm9_meta['2']  = RefMeta('chr2', '181748087', '9b9d64dc89ecc73d3288eb38af3f94bd')
            mm9_meta['3']  = RefMeta('chr3', '159599783', '0a692666a1b8526e1d1e799beb71b6d0')
            mm9_meta['4']  = RefMeta('chr4', '155630120', 'f5993a04396a06ed6b28fa42b2429be0')
            mm9_meta['5']  = RefMeta('chr5', '152537259', 'f90804fb8fe9cb06076d51a710fb4563')
            mm9_meta['6']  = RefMeta('chr6', '149517037', '258a37e20815bb7e3f2e974b9d4dd295')
            mm9_meta['7']  = RefMeta('chr7', '152524553', 'e0d6cea6f72cb4d9f8d0efc1d29dd180')
            mm9_meta['8']  = RefMeta('chr8', '131738871', '5f217cb8a9685b9879add3ae110cabd7')
            mm9_meta['9']  = RefMeta('chr9', '124076172', 'dde08574942fc18050195618cc3f35af')
            mm9_meta['10'] = RefMeta('chr10', '129993255', 'be7e6a13cc6b9da7c1da7b7fc32c5506')
            mm9_meta['11'] = RefMeta('chr11', '121843856', 'e0099550b3d3943fb9bb7af6fa6952c1')
            mm9_meta['12'] = RefMeta('chr12', '121257530', '1f9c11dc6f288f93e9fab56772a36e85')
            mm9_meta['13'] = RefMeta('chr13', '120284312', 'a7b4bb418aa21e0ec59d9e2a1fe1810b')
            mm9_meta['14'] = RefMeta('chr14', '125194864', '09d1c8449706a17d40934302a0a3b671')
            mm9_meta['15'] = RefMeta('chr15', '103494974', 'e41c8b42b0921378b1fdd5172f6be067')
            mm9_meta['16'] = RefMeta('chr16', '98319150', 'e051b3930c2557ade21d67db41f3a518')
            mm9_meta['17'] = RefMeta('chr17', '95272651', '47eede15e5761fb9c2267627f18211e7')
            mm9_meta['18'] = RefMeta('chr18', '90772031', '9f9d41cfdb9d91b62b928a3eb4eb6928')
            mm9_meta['19'] = RefMeta('chr19', '61342430', '591f8486f82c22442bb8463595a18e0a')
            mm9_meta['X']  = RefMeta('chrX', '166650296', '3d0d9df898d2c830b858f91255d8a1eb')
            mm9_meta['Y']  = RefMeta('chrY', '15902555', '5ff564f9fbc8cb87bcad6cfa6874902b')
            mm9_meta['M']  = RefMeta('chrM', '16299', '11c8af2a2528b25f2c080ab7da42edda')
            self.meta['refmeta'] = mm9_meta

        self.refmeta = self.meta['refmeta']
        self.all_chroms = set(self.refmeta.keys())
        #print(self.refmeta)

    def load(self, chrom):
        '''
        Load instructions of a given chromsome.
        Set self.chrom and self.data if it is loaded sucessfully.
        Otherwise, reset self.chrom, self.data, self.posmap, and self.seq,
        and raise exception.
        '''

        assert chrom is not None and chrom != "", "Null chrom parameter."

        if self.chrom != chrom:  # chrom not currently loaded
            if chrom not in self.all_chroms:
                # reset posmap, seq, and data
                self.chrom = None
                self.data = None
                self.posmap = None
                self.seq = None
                #self.logger.warning("chromosome '%s' not found in MOD", chrom)
                raise ValueError("Chromosome '%s' not found." % chrom)

            gc.disable()
            n = 0
            self.data = []
            append = self.data.append

            #print(self.tabix_chroms)
            if chrom in self.tabix_chroms:
                for line in self.tabix.fetch(reference=str(chrom)):
                    try:
                        n += 1
                        cols = line.split('\t')
                        assert len(cols) == 4, "Wrong number of columns."
                        cols[2] = int(cols[2])  # convert positions to integers
                        cols[-1] = cols[-1].rstrip()  # remove the line breaks
                        append(cols)
                    except Exception as e:
                        print("Error occured while parsing line:")
                        print(line)
                        self.chrom = None
                        self.data = None
                        self.posmap = None
                        self.seq = None
                        raise e

            self.posmap = None
            self.seq = None
            gc.enable()

            self.chrom = chrom
            if VERBOSE:
                print("%d lines from '%s' loaded" % (n, self.chrom))

    def build_posmap(self):
        '''Build position mapping based on the current chromosome'''

        assert self.chrom is not None and self.data is not None,\
            "No chromosome is loaded."

        chrom = self.chrom
        chromLen = self.refmeta[chrom].length
        data = self.data  # (op, ref_chrom, ref_pos, seq)
        n = len(data)

        #self.logger.info("[%s]: building position map ...", chrom)

        maps = []  # ((ref_chrom,ref_pos), (new_chrom,new_pos), len, direction)
        madd = maps.append

        rpos = 0   # position in the reference
        npos = 0   # position in the new genome (pseudogenome)

        gc.disable()
        if len(data) > 0:
            ipos = data[0][2]  # position of the instruction

            # Make sure rows in data[startIdx:endIdx] have the same position
            startIdx = 0
            endIdx = 0
            for i in range(n + 1):
                if i < n and data[i][2] == ipos:
                    endIdx += 1
                    continue

                #assert rpos <= ipos
                if (rpos > ipos):
                    raise ValueError("Position not ordered at line %d" %
                                     (i + 1))

                # fill 'M's in the gap between current position and
                # the next instruction position
                if rpos < ipos:
                    madd(((chrom, rpos), (chrom, npos), ipos - rpos, '+'))
                    npos += ipos - rpos
                    rpos = ipos

                # handle different instructions on the same positions
                instructions = [(1, 'm')]  # (length, op)
                for j in range(startIdx, endIdx):
                    tup = data[j]
                    if tup[0] == 's':
                        # s-instruction has lower priority than d-instruction
                        if instructions[0][1] != 'd':
                            instructions[0] = (1, 's')

                    elif tup[0] == 'i':
                        # i-instruction is appended in order
                        instructions.append((len(tup[3]), 'i'))

                    elif tup[0] == 'd':
                        instructions[0] = (1, 'd')

                    else:
                        raise ValueError("Unknown operation '%s'" % tup[0])

                for length, op in instructions:
                    if op == 'm':
                        madd(((chrom, rpos), (chrom, npos), length, '+'))
                        rpos += length
                        npos += length
                    elif op == 's':
                        # For substitutions
                        # Treat them as matches since no coordinate shift
                        madd(((chrom, rpos), (chrom, npos), length, '+'))
                        rpos += length
                        npos += length
                    elif op == 'i':
                        # For insertions
                        # Set the ref position to -(the previous ref position)
                        madd(((chrom, -rpos + 1), (chrom, npos), length, '+'))
                        npos += length
                    elif op == 'd':
                        # For deletions
                        # Set the new position to -(the previous new position)
                        madd(((chrom, rpos), (chrom, -npos + 1), length, '+'))
                        rpos += length
                    else:
                        raise ValueError("Unknown operation '%s'" % op)

                startIdx = endIdx
                endIdx += 1

                ipos = data[i][2] if i < n else ipos

        #assert rpos <= refLens[chrom]
        if rpos > chromLen:
            raise ValueError("Position '%d' out of reference boundary" %
                             rpos)

        # append the remaining region as a match
        #print(rpos)
        #print(chromLen)
        if rpos < chromLen:
            madd(((chrom, rpos), (chrom, npos), chromLen - rpos, '+'))

        assert len(maps) > 0

        #for l in maps:
        #    print(l)

        # compress adjacent matches/substitutions or deletions.
        compressed = []
        buf = maps[0]
        for cur in maps[1:]:
            # 0: (ref_chrom, ref_pos), 1: (new_chrom, new_pos)
            # 2: length, 3: direction

            # matching ref_chrom, new_chrom, and direction
            if (buf[0][0] == cur[0][0] and buf[1][0] == cur[1][0] and
                buf[3] == cur[3] and
                # adjacent matches/substitutions
                ((buf[0][1] >= 0 and cur[0][1] >= 0 and
                  buf[1][1] >= 0 and cur[1][1] >= 0 and
                  cur[1][1] - buf[1][1] == cur[0][1] - buf[0][1]) or
                 # adjacent deletions: new_pos < 0 and they are the same
                 (buf[1][1] < 0 and buf[1][1] == cur[1][1]))):
                buf = (buf[0], buf[1], buf[2] + cur[2], buf[3])
            else:
                compressed.append(buf)
                buf = cur
        compressed.append(buf)
        gc.enable()

        #for l in compressed:
        #    print(l)
        self.posmap = PosMap()
        self.posmap.load(compressed)

    def get_posmap(self, chrom):
        '''Return a position map object'''

        try:
            if self.chrom != chrom:
                self.load(chrom)
            if self.posmap is None:
                self.build_posmap()
        except Exception as e:
            self.posmap = None
            raise e
        return self.posmap

    def build_seq(self, fasta, alias=None):
        '''Build the sequence based on MOD data and reference sequences.'''

        if alias is None:
            alias = Alias()

        for fa_chrom in alias.getAliases(self.chrom):
            if fa_chrom in fasta.chrom_names:
                break
        else:
            raise ValueError("Chromosome '%s' not found in fasta" %
                             self.chrom +
                             "Possible chromosomes: %s" %
                             str(fasta.chrom_names))

        chromLen = self.refmeta[self.chrom].length
        data = self.data
        n = len(data)

        # if no instructions in MOD for the given chromosome

        if len(data) == 0:
            self.seq = fasta.fetch(chrom=fa_chrom, start=0)
            return

        rpos = 0
        npos = 0
        ipos = data[0][2]
        gc.disable()
        seqs = []
        sadd = seqs.append

        # Make sure rows in data[startIdx:endIdx] have the same position
        startIdx = 0
        endIdx = 0
        for i in range(n + 1):
            if i < n and data[i][2] == ipos:
                endIdx += 1
                continue

            #assert rpos <= ipos
            if (rpos > ipos):
                raise ValueError("Position not in order at line %d" % (i + 1))

            # fill reference sequence in the gap between current position and
            # the next instruction position
            if rpos < ipos:
                sadd(fasta.fetch(chrom=fa_chrom, start=rpos, end=ipos))
                npos += ipos - rpos
                rpos = ipos

            # handle different instructions on the same positions
            instructions = [(1, 'm')]  # (length, op, seq), seq is optional
            for j in range(startIdx, endIdx):
                tup = data[j]
                if tup[0] == 's':
                    if instructions[0][1] != 'd':  # 'd' overrides 's'.
                        instructions[0] = (1, 's', tup[3])

                elif tup[0] == 'i':
                    instructions.append((len(tup[3]), 'i', tup[3]))

                elif tup[0] == 'd':
                    instructions[0] = (1, 'd')
                else:
                    raise ValueError("Unknown operation '%s'" % tup[0])

            for inst in instructions:
                length = inst[0]
                op = inst[1]
                #seq = inst[2]
                if op == 'm':
                    sadd(fasta.fetch(chrom=fa_chrom, start=rpos,
                                     end=rpos + length))
                    rpos += length
                    npos += length
                elif op == 's':
                    # For substitutions
                    # Put the last character in the seq field
                    # TODO: make sure the substituted base matches reference
                    sadd(inst[2][-1])
                    rpos += length
                    npos += length
                elif op == 'i':
                    # For insertions
                    # Append the newly-inserted sequence
                    sadd(inst[2])
                    npos += length
                elif op == 'd':
                    # For deletions
                    # Increase reference position and do nothing to sequence
                    # TODO: make sure the deleted sequence matches reference
                    rpos += length
                else:
                    raise ValueError("Unknown operation '%s'" % op)

            startIdx = endIdx
            endIdx += 1

            ipos = data[i][2] if i < n else ipos

        #assert rpos <= refLens[chrom]
        if rpos > chromLen:
            raise ValueError("Position '%d' out of reference boundary" %
                             rpos)

        # append the remaining reference sequence
        if rpos < chromLen:
            sadd(fasta.fetch(chrom=fa_chrom, start=rpos))

        self.seq = ''.join(seqs)
        gc.enable()

    def get_seq(self, chrom, fastafn=None, fastaobj=None, alias=None):
        '''Return a position map object'''

        assert fastafn is not None or fastaobj is not None
        try:
            if fastaobj is None:
                fastaobj = FaReader(fastafn)

            if self.chrom != chrom:
                self.load(chrom)

            if self.seq is None:
                self.build_seq(fastaobj, alias)

        except Exception as e:
            self.seq = None
            raise e

        return self.seq

# if __name__ == '__main__':
#     mod = Mod('./tests/mod1.mod')
#     #print(mod.ref.keys())
#     print(mod.ref['chr1'].length)
#     print(mod.ref['chr1'].url)
#     print(mod.ref['chr1'].md5sum)
#     mod.get_posmap('chr1')
#     print(mod.posmap.fmap(('chr1', 4)))
#     print(mod.posmap.fmap(('chr1', 15)))
#     print(mod.posmap.bmap(('chr1', 6)))
#     print(mod.posmap.bmap(('chr1', 13)))

#     print(mod.get_seq('chr1', './tests/fasta1.fa'))

#     print(mod.ref['chr2'].length)
#     print(mod.ref['chr2'].url)
#     print(mod.ref['chr2'].md5sum)
#     mod.get_posmap('chr2')
#     print(mod.posmap.fmap(('chr2', 4)))
#     print(mod.posmap.fmap(('chr2', 15)))
#     print(mod.posmap.bmap(('chr2', 6)))
#     print(mod.posmap.bmap(('chr2', 13)))
#     fasta = FaReader('./tests/fasta1.fa')
#     print(mod.get_seq('chr2', fastaobj=fasta))

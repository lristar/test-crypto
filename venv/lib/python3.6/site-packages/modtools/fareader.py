'''
A module for fasta reader

Created on Aug 26, 2013

@author: Shunping Huang
'''
from __future__ import print_function

import csv
import os.path
import hashlib
import pysam  # for faidx


class FaReader:
    def prepare_faidx(self):
        idx_fn = self.fasta_fn + '.fai'
        if os.path.isfile(idx_fn):
            print("Fasta index '%s' found" % idx_fn)
            return idx_fn
        else:
            print("Fasta index not found")
            print("Create fasta index '%s' ... " % self.fasta_fn, end='')
            pysam.faidx(self.fasta_fn)

            if os.path.isfile(idx_fn):
                print("OK")
                return idx_fn
            else:
                print("Failed")
                raise RuntimeError("Cannot create fasta index")

    def load_idx(self):
        if self.idx_fn is None:
            raise ValueError("Null idx file")

        # chromosome => (seq length, offset, base per line, char per line)
        self.data = {}
        with open(self.idx_fn, 'r') as fp:
            csvfile = csv.reader(fp, delimiter='\t')
            for row in csvfile:
                if row[0] in self.data:
                    print("Duplicated chromosome '%s', skipped" % row[0])
                else:
                    self.data[row[0]] = (int(row[1]), int(row[2]),
                                         int(row[3]), int(row[4]))

    def fetch(self, chrom, start=0, end=None):
        '''
        Fetch sequence in [start, end). End base not included.
        Start and end are 0-based.
        '''
        with open(self.fasta_fn, 'r') as fp:
            if chrom not in self.data:
                raise ValueError("Chromosome '%s' not in fasta" % chrom)

            seq_len = self.data[chrom][0]
            offset = self.data[chrom][1]
            base_per_line = self.data[chrom][2]
            char_per_line = self.data[chrom][3]

            end = seq_len if end is None else end

            #print('offset: %d' % offset)
            #print('fetch: %d-%d' % (start, end))

            pool = []
            if (start < end and start >= 0 and end >= 0 and end <= seq_len):
                n_requested = end - start
                #print(start)
                start_pos = (offset +
                             int(start / base_per_line) * char_per_line +
                             int(start % base_per_line))
                #print(start_pos)
                fp.seek(start_pos)

                n_current = 0
                line = fp.readline()
                while (line):
                    #print(line)
                    # Convert all char to uppercase and strip '\n' or '\r\n'
                    stripped = line.upper().rstrip()
                    n_current += len(stripped)
                    pool.append(stripped)
                    line = None if n_current >= n_requested else fp.readline()
                assert len(pool) > 0, "Sequence not found, problems in index"
                if n_current > n_requested:
                    pool[-1] = pool[-1][0:(n_requested - n_current)]
                return ''.join(str(v) for v in pool)
            else:
                raise ValueError("Start '%d' or end '%d' error" % (start, end))

    def chrom_len(self, chrom):
        if chrom not in self.data:
            raise ValueError("Chromosome '%s' not in fasta" % chrom)
        return self.data[chrom][0]

    def chrom_md5(self, chrom):
        '''MD5 sum of a sequence'''
        if chrom not in self.data:
            raise ValueError("Chromosome '%s' not in fasta" % chrom)

        md5 = hashlib.md5()
        seq_len = self.chrom_len(chrom)
        block_start = 0
        block_end = block_start + 100000
        block_end = block_end if block_end < seq_len else seq_len
        while block_start < seq_len:
            md5.update(self.fetch(chrom, block_start, block_end).
                       encode('utf-8'))
            block_start += 100000
            block_end = block_start + 100000
            block_end = block_end if block_end < seq_len else seq_len
        return md5.hexdigest()

    def chrom_offset(self, chrom):
        if chrom not in self.data:
            raise ValueError("Chromosome '%s' not in fasta" % chrom)
        return self.data[chrom][1]

    def __init__(self, fasta_fn):
        if fasta_fn is None:
            raise ValueError("Null fasta file")

        if os.path.isfile(fasta_fn):
            self.fasta_fn = fasta_fn
        else:
            self.fasta_fn = None
            raise RuntimeError("File '%s' not found" % fasta_fn)

        self.idx_fn = self.prepare_faidx()
        self.load_idx()
        self.chrom_names = self.data.keys()


if __name__ == '__main__':
    a = FaReader('a.fa')
    print(a.fetch("chrY", 0, 5))
    print(a.fetch("chrY", 0, 50))
    print(a.fetch("chrY", 0, 51))
    print(a.fetch("chrY", 0, 52))
    print(a.fetch("chrY", 1, 50))
    print(a.fetch("chrY", 1, 51))
    print(a.fetch("chrY", 1, 52))
    print(a.chrom_len("chrM"))
    print(a.fetch("chrM", 16297))
    print(a.fetch("chrY", end=10))
    print(a.chrom_hash("chrY"))
    print(a.chrom_hash("chrM"))

'''
The new module for reference metadata.

Created on Sep 7, 2013

@author: Shunping Huang
'''


class RefMeta:
    def __init__(self, chrom, length, md5sum):
        self.chrom = chrom
        try:
            self.length = int(length)
        except Exception:
            raise ValueError("Error occured when parsing length '%s'", length)
        self.md5sum = md5sum

    @staticmethod
    def parse(line):
        cols = line.strip().split(',')   # chrom,length,md5sum
        if len(cols) != 3:
            raise ValueError("Number of columns should be three.")
        meta = RefMeta(cols[0], cols[1], cols[2])
        return meta

    def __str__(self):
        return ', '.join(['chrom=' + self.chrom,
                          'length=' + str(self.length),
                          'md5sum=' + self.md5sum])

    def __repr__(self):
        return self.__str__()

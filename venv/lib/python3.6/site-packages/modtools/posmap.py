'''
The new module of position mapping

Created on Sep 7, 2013

@author: Shunping Huang
'''

import bisect
import gc

__all__ = ['PosMap']


class PosMap:
    '''
    Position Mapping
    forward: reference -> pseudogenome
    backward: pseudogenome -> reference

    *Assuming that one reference position maps to at most one pseudogenome
    position, and vice versa.
    '''

    def __init__(self):
        '''
        Initialize a position map.
        data
            an list of tuples that have 4 elements:
            ((ref_chrom, ref_pos), (new_chrom, new_pos), length, direction)
        '''

        self.data = None
        self.fsorted = None  # sorted data by forward mapping key
        self.bsorted = None  # sorted data by backward mapping key
        self.fkeys = []
        self.bkeys = []

    def load(self, data):
        '''Load and pre-process mappings'''

        assert data is not None

        gc.disable()
        self.data = data

        #self.fsorted = sorted(self.data, key=lambda tup: tup[0])
        self.fsorted = sorted([tup for tup in self.data if tup[0][1] >= 0],
                              key=lambda tup: tup[0])
        self.fkeys   = [tup[0] for tup in self.fsorted]

        #self.bsorted = sorted(self.data, key=lambda tup: tup[1])
        self.bsorted = sorted([tup for tup in self.data if tup[1][1] >= 0],
                              key=lambda tup: tup[1])
        self.bkeys   = [tup[1] for tup in self.bsorted]
        gc.enable()

        #print(self.fsorted)
        #print(self.bsorted)

    def fmap(self, pos):
        '''Mapping a position from reference to pseudogenome.'''

        # Find the bucket index where the start position is the max position
        # that smaller than the given position.
        i = bisect.bisect_right(self.fkeys, pos) - 1
        if i < 0:
            raise ValueError("Error: reference position '%d' underflow" %
                             pos[1])

        #print(self.fsorted[i])
        rpos = self.fsorted[i][0]
        npos = self.fsorted[i][1]
        length = self.fsorted[i][2]
        direction = self.fsorted[i][3][0]

        if pos[0] == rpos[0]:
            # TODO: May need to change for negative direction.
            if pos[1] >= rpos[1] and pos[1] < rpos[1] + length:
                if npos[1] < 0:  # for deletions
                    # npos is the inverse of previously nearest position.
                    return npos

                if direction == '+':
                    #d = npos[1] - rpos[1]
                    #return (npos[0], pos[1] + d)
                    return (npos[0], pos[1] + npos[1] - rpos[1])
                else:  # inverted region
                    raise NotImplementedError("Error: negative direction")
                    #s = npos[1] + rpos[1] + length - 1
                    #return (npos[0], s - pos[1])
            else:
                raise ValueError("Error: reference position '%d' overflow" %
                                 pos[1])
        else:
            raise ValueError("Error: reference chromosome '%s' not found" %
                             pos[0])

    def bmap(self, pos):
        '''Mapping a position from pseudogenome genome to reference'''

        # Find the bucket index where the start position is the max position
        # that smaller than the given position.
        i = bisect.bisect_right(self.bkeys, pos) - 1
        if i < 0:
            raise ValueError("Error: pseudogenome position %d underflows" %
                             pos[1])

        #print(self.bsorted[i])
        rpos = self.bsorted[i][0]
        npos = self.bsorted[i][1]
        length = self.bsorted[i][2]
        direction = self.bsorted[i][3][0]

        if pos[0] == npos[0]:
            # TODO: May need to change for negative direction.
            if pos[1] >= npos[1] and pos[1] < npos[1] + length:
                ## May need to consider direction!!!
                ## Insertion, return the inverse of newest preceding position.
                if rpos[1] < 0:
                    return rpos

                if direction == '+':
                    #d = rpos[1] - npos[1]
                    #return (rpos[0], pos[1] + d)
                    return (rpos[0], pos[1] + rpos[1] - npos[1])
                else:  # inverted region
                    raise NotImplementedError("Error: negative direction")
                    #s = rpos[1] + npos[1] + length - 1
                    #return (rpos[0], s - pos[1])
            else:
                raise ValueError("Error: pseudogenome position '%d' overflow" %
                                 pos[1])
        else:
            raise ValueError("Error: pseudogenome chromosome '%s' not found." %
                             pos[0])

    # def toCSV(self):
    #     out = []
    #     append = out.append
    #     join = '\t'.join
    #     for row in self.data:
    #         append(join((row[0][0], str(row[0][1]),
    #                      row[1][0], str(row[1][1]),
    #                      str(row[2]), row[3])))
    #     return '\n'.join(out)

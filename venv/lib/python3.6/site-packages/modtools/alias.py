'''
A module for handling aliases of a name.

Alias classes are stored in a csv format file.
The first name on each row is the basic name of the class, while the other
names are considered aliases.

#### Below is an example csv file for chromosome 1 and mitochondrial ####
chr1,1
chrM,M,MT,chrMT
#### End of file ####

Created on Nov 4, 2012

@author: Shunping Huang
'''

from __future__ import print_function

import logging

VERBOSE = 1
DEBUG = 0
logger = None


class Alias:
    def __init__(self):
        global logger
        logger = logging.getLogger()
        self._reset()

    def _reset(self):
        self.names = None
        self.nameAliasMap = None
        self.aliasNameMap = None

    def _loadClasses(self, classes):
        '''Load alias from the equivalence class of alias'''

        if DEBUG:
            print("Loading classes into alias ...")
            print(classes)

        # The first one in a class is considered the basic name of this class
        self.names = [tup[0] for tup in classes]

        s = set()
        for name in self.names:
            if name in s:
                raise ValueError("Duplicated definitions of name '%s'."
                                 % name)
            else:
                s.add(name)
        s.clear()

        # A dict that maps a basic name to an alias arrays (including basic).
        self.nameAliasMap = dict([(tup[0], tup) for tup in classes])

        # A dict that maps an alias to a basic name
        self.aliasNameMap = {}
        for name in self.names:
            for alias in self.nameAliasMap[name]:
                if alias in self.aliasNameMap.keys():
                    raise ValueError("Duplicated definitions of alias '%s'."
                                     % alias)
                self.aliasNameMap[alias] = name

    def load(self, fileName):
        '''Load from a file of which lines are comma-separated'''

        if fileName is None:
            if VERBOSE:
                try:
                    logger.info("Using fallback alias settings.")
                except Exception:
                    print("Using fallback alias settings.")
            return

        try:
            if VERBOSE:
                try:
                    logger.info("Loading alias file '%s'." % fileName)
                except Exception:
                    print("Loading alias file '%s'. " % fileName)

            with open(fileName, 'r') as fp:
                classes = []
                nLines = 0
                for line in fp:
                    nLines += 1
                    stripped = line.strip()
                    # Skip any line with only whitespace characters
                    if stripped == "":
                        continue
                    parts = stripped.split(',')
                    assert len(parts) >= 1, "Internal Error."
                    assert all([p != "" for p in parts]), \
                        "Empty field on Line %d" % nLines
                    classes.append(parts)
                self._loadClasses(classes)

            if VERBOSE:
                try:
                    logger.info("Loading completed.")
                except Exception:
                    print("Loading completed.")

        except Exception as e:
            self._reset()

            if VERBOSE:
                try:
                    logger.info("Failed to load.")
                    logger.info("Using fallback alias settings.")
                except Exception:
                    print("Failed to load.")
                    print("Using fallback alias settings.")
            if DEBUG:
                #import traceback
                #traceback.print_last()
                print(e)

            raise(e)

    #def hasName(self, name):
    #    '''Test whether it is among the list of names'''
    #    if self.names is None:
    #        return True
    #    return name in self.names

    def getAliases(self, name):
        '''Return a list of aliases of the given name'''

        if self.names is None:
            return [name]
        return self.nameAliasMap.get(name, [])

    def getName(self, alias):
        '''Return the basic name of a given alias'''

        if self.names is None:
            return alias
        return self.aliasNameMap.get(alias, None)

    def setVerbose(self, v):
        '''Set Verbose variable'''

        global VERBOSE
        VERBOSE = v

'''
The new utility module

Created on Sep 9, 2013

@author: Shunping Huang
'''

import os

__all__ = ['is_file_readable', 'is_file_writable', 'is_dir_writable']


def is_file_readable(fileName):
    '''Check if a file is readable'''

    if os.path.isfile(fileName) and os.access(fileName, os.R_OK):
        return True
    else:
        raise IOError("Cannot read file '%s'." % fileName)


def is_file_writable(fileName, force):
    '''Check if a file is writable. Do not overwrite unless force is True'''

    if os.path.isfile(fileName):
        if not force:
            raise IOError("File '%s' exists. Use -f to overwrite." %
                          fileName)
        if not os.access(fileName, os.W_OK):
            raise IOError("Cannot write file '%s'." % fileName)
    else:
        try:
            open(fileName, 'w').close()
            os.remove(fileName)
        except IOError as e:
            raise IOError("Cannot write file '%s'." % fileName)
    return True


def is_dir_writable(directory, force):
    '''Check if a path is writable. Do not create it unless force is True'''

    while directory.endswith('/'):
        directory = directory[:-1]

    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise IOError("File '%s' exists. Not a directory." % directory)
    else:
        if force:
            print("Creating directory '%s' ..." % directory)
            os.makedirs(directory)
        else:
            raise IOError("Directory '%s' not found. Use -f to create." %
                          directory)

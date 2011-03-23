import glob
from inspect import getargspec, formatargspec
import time
import os
import os.path
from findfiles import find_files_iter as find_files
import logging

def smart_error(error_string=None):
    # TODO: get the smart error to raise up missing args to method
    def deco(f):
        def wrapper(*args,**kwargs):
            # we want to raise through BlipErrors.
            # we want to wrap all other errors in BlipErrors
            #print "smart error Entering", f.__name__
            return f(*args,**kwargs)
            try:
                return f(*args,**kwargs)
            except Exception, ex:
                if isinstance(ex,BlipError):
                    raise ex
                else:
                    raise BlipError(error_string % {'err':str(ex)})
        return wrapper
    return deco

# we are going to make sure either the object
# or the args contain the specified attribute
def require_attribute(atts):
    atts = atts if isinstance(atts,list) else [atts]
    def deco(f):
        def wrapper(*args,**kwargs):
            #print "require attribute Entering", f.__name__
            for att in atts:
                has_attribute = False

                if args and hasattr(args[0],att):
                    # the first place to look is on the object
                    if getattr(args[0],att) is not None:
                        has_attribute = True

                    # next, we need to look in the normal args
                    arg_spec = formatargspec(getargspec(f))
                    if att in arg_spec[0] and args[arg_spec[0].index(att)] is not None:
                        has_attribute = True

                    # and lastly in the named args
                    if att in kwargs and kwargs.get(att) is not None:
                        has_attribute = True

                if not has_attribute:
                    # TODO: raise missing method arg error
                    raise KeyError(att)

            return f(*args,**kwargs)
        return wrapper
    return deco


def auto_flush(f):
    def deco(*args,**kwargs):
        # for now we are just going to flush each time
        #print "auto flush Entering", f.__name__
        result = f(*args,**kwargs)
        # flush'm
        args[0].flush()
        return result
    return deco


class KeyManager(object):
    def __init__(self,root_dir,value_prefix='_value',
                      file_extension='.txt'):
        self.root_dir = root_dir
        self.value_prefix = value_prefix
        self.file_extension = file_extension

        #print 'KeyManager: root: %s; prefix: %s; ext: %s' % (
        #                                        self.root_dir,
        #                                        self.value_prefix,
        #                                        self.file_extension )

    def clean_key(self,key):
        # we can't let keys w/ bad chars through
        to_replace = [
            ('/','__'),('\\','___')
        ]
        for s,r in to_replace:
            key = key.replace(s,r)
        return key

    def next_key_path(self,key):
        if not key:
            raise KeyError('key')

        # clean the key value
        key = self.clean_key(key)

        # we are going to return the absolute system path to the next
        # version of the key's file

        # we are going to do /<storage_dir>/<key[:150]/<timestamp>.txt
        # there will be a file named key in the directory, so that keys
        # which are 150 > chars can be sure they are in the right place

        path = '%s/%s/%s%s%s' % (self.root_dir,
                                 key[:150],
                                 self.value_prefix,
                                 time.time(),
                                 self.file_extension)

        return path

    def last_key_path(self,key):
        #print "getting last key path for %s" % key

        if not key:
            raise KeyError('key')

        # make sure the key is clean
        key = self.clean_key(key)

        # we want to get a list of the dirs which are they key
        search = os.path.join(self.root_dir,key+'*' if len(key) > 150 else key)
        dirs = glob.glob(search)
        key_dir = None # where they key's folder is

        # now that we have all the dirs which match, lets see if
        # we got back, if anything
        if len(dirs) is 0:
            return None

        elif len(dirs) > 1:
            # should only happen if the key is 150+ chars long
            if len(key) < 150:
                logging.debug('dirs: %s' % dirs)
                raise Exception('Found more than one dir for key: %s' % key)

            # we need to enter the dirs and figure out which one actually
            # has our key
            for d in dirs:
                if key_dir: break
                with file('%s/%s' % (d,'key.txt'),'r') as fh:
                    _k = fh.readline().rstrip()
                    if _k == key:
                        key_dir = d

        else:
            key_dir = dirs[0]

        if not key_dir:
            raise Exception('Could not find key directory')

        #print 'key_dir: ',key_dir

        # now we need to find the most recent value file
        files = glob.glob('%s*'%os.path.join(key_dir,self.value_prefix))


        #print files

        # get rid of the prefix and extension for sorting
        foffset = len(self.value_prefix)
        roffset = -len(self.file_extension)
        _files = []
        for path in files:
            _files.append(float(os.path.basename(path)[foffset:roffset]))
        files = _files
        files.sort() # now it's the last one (aka highest #)

        # if there are more than 100 files, clean up leaving only 10
        if len(files) > 100:
            for f in files[:-10]:
                p = os.path.join(key_dir,'%s%s%s' % (self.value_prefix,
                                                     f,
                                                     self.file_extension))
                os.unlink(p)

        # grab the most recent and add the rest of the path / extenion
        file_name = ''.join((self.value_prefix,
                             str(files[-1]),
                             self.file_extension))
        file_path = os.path.abspath(os.path.join(key_dir,file_name))

        return file_path

    @staticmethod
    def find_keys(path):
        path = os.path.abspath(path)
        paths = find_files(path,file_name='key.txt')
        keys = []
        for path in paths:
            with file(path,'r') as fh:
                key = fh.read().strip()
                keys.append(key)

        return keys

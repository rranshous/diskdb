import glob
from inspect import getargspec, formatargspec
import time

def smart_error(error_string=None):
    # TODO: get the smart error to raise up missing args to method
    def deco(f):
        def wrapper(*args,**kwargs):
            # we want to raise through BlipErrors.
            # we want to wrap all other errors in BlipErrors
            print "smart error Entering", f.__name__
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
            print "require attribute Entering", f.__name__
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
        print "auto flush Entering", f.__name__
        result = f(*args,**kwargs)
        # flush'm
        args[0].flush()
        return result
    return deco


class KeyManager(object):
    def __init__(self,root_dir=None,value_prefix='_value',file_extension='.txt'):
        self.root_dir = root_dir
        self.value_prefix = value_prefix
        self.file_extension = file_extension

    def next_key_path(self,key):
        if not key:
            raise KeyError('key')

        # we are going to return the absolute system path to the next
        # version of the key's file

        # we are going to do /<storage_dir>/<key[:150]/<timestamp>.txt
        # there will be a file named key in the directory, so that keys
        # which are 150 > chars can be sure they are in the right place

        path = '%s/%s/%s%s%s' % (self.root_dir,
                                 key[:150],
                                 value_refix,
                                 time.time(),
                                 self.file_extension)
                                    
        print 'path:',path

        return path

    def last_key_path(self,key):
        print "getting last key path for %s" % key

        if not key:
            raise KeyError('key')

        # we want to get a list of the dirs which are they key
        dirs = glob.glob('%s/%s' % (self.root_dir,key))
        key_dir = None # where they key's folder is

        # now that we have all the dirs which match, lets see if
        # we got back, if anything
        if len(dirs) is 0:
            return None

        # more than one
        elif len(dirs) > 1:
            # should only happen if the key is 150+ chars long
            if len(key) is not 150:
                raise Exception('Found more than one dir for key')

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

        print 'key_dir: ',key_dir

        # now we need to find the most recent value file
        files = glob.glob('%s/%s*' % (key_dir,self.value_prefix))
        # get rid of the prefix for sorting
        files = sorted(( float(x[len(key_dir)+len(self.value_prefix)+1 : -4] )
                         for x in files ))

        print files

        # grab the most recent
        file_name = '%s%s' % (self.value_prefix,files[0])

        print file_name
        
        file_path = '%s/%s%s' % (key_dir,file_name,self.file_extension)
        
        print file_path

        return file_path

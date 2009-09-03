# going to be the class we use to manipulate the key/value pairs

FILE_PATH = '/tmp/hd'

from utils import KeyManager
key_manager = KeyManager(FILE_PATH)

import decorator

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
            from inspect import getargspec, formatargspec
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


class BlipError(Exception):
    pass

class Blip(object):
    def __init__(self,**kwargs):
        self._key = None
        self._value = None
        self.location = None
        self.auto_flush = True
        for k,v in kwargs.iteritems():
            if not hasattr(self,k):
                raise KeyError(k)
            setattr(self,k,v)


    @smart_error('Error while getting key: %(err)s')
    def get_key(self):
        print 'get_key'
        return self._key

    @smart_error('Error while setting key: %(err)s')
    def set_key(self,key):
        print 'set_key'
        okey = self._key
        self._key = key
        if okey != key and okey is not None:
            self.flush()
        elif okey != key and okey is None:
            self.update_value()

    # lame, we have to do lambda thing so we hit the decorators
    key = property(fget=lambda s: s.get_key(),
                   fset=lambda s,v: s.set_key(v))

    @smart_error('Error while getting value: %(err)s')
    @require_attribute('_key')
    def get_value(self,key=None):
        print 'get_value'
        if key: self.key = key
        if not self._value:
            self.update_value()
        return self._value

    @auto_flush
    @smart_error('Error while setting value: %(err)s')
    @require_attribute('_key')
    def set_value(self,value):
        print 'set_value'
        self._value = value

    value = property(fget=lambda s: s.get_value(),
                     fset=lambda s,v: s.set_value(v))

    @auto_flush
    @smart_error('Error while incrementing value: %(err)s')
    @require_attribute('_value')
    def increment(self,to_add):
        try:
            self._value += to_add
        except TypeError:
            raise BlipError('Can not increment a %s value' % type(self.value))


    @require_attribute('_key')
    def flush(self):
        # write our value out
        flusher.flush(self)

    @require_attribute('_key')
    def update_value(self):
        # read in the newest value
        self._value = reader.read_for_key(self.key)


class Flusher(object):
    def __init__(self,storage_dir):
        self.storage_dir = storage_dir

    def flush(self,to_flush):
        import os
        # the to_flush doesn't really matter,
        # it just needs to have a key and a vlaue
        print "trying to flush %s" % to_flush
        file_path = key_manager.next_key_path(to_flush.key)
        file_path_dir = os.path.dirname(file_path)

        # if the key's dir doesn't exist, create it
        if not os.path.exists(file_path_dir):
            os.makedirs(file_path_dir)

        # if the key is 150+ chars, than also
        # write a key.txt to the dir
        if len(to_flush.key) >= 150:
            print 'key path:','%s/key.txt' % file_path_dir
            with file('%s/key.txt' % file_path_dir,'w') as fh:
                fh.write(to_flush.key)

        with file(file_path,'w') as fh:
            fh.write(to_flush.value)

flusher = Flusher(FILE_PATH)


class Reader(object):
    def __init__(self,storage_dir):
        self.storage_dir = storage_dir

    def read_for_key(self,key):
        print 'reading: %s' % key

        key_path = key_manager.last_key_path(key)
        if key_path:
            try:
                with file(key_manager.last_key_path(key),'r') as fh:
                    value = fh.readline().rstrip()
            except IOError:
                print "file not found"
                value = None
        else:
            value = None

        print "got value: %s" % value
        return value

reader = Reader(FILE_PATH)

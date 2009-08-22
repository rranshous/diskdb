# this is going to be the class we use to manipulate the key/value pairs
from utils import ToolBelt
import decorator

utils = ToolBelt('/tmp/hd/')

def smart_error(error_string=None):
    def deco(f):
        def wrapper(*args,**kwargs):
            # we want to raise through BlipErrors.
            # we want to wrap all other errors in BlipErrors
            print "smart error Entering", f.__name__
            try:
                return f(*args,**kwargs)
            except Exception, ex:
                if isinstance(ex,BlipError):
                    raise ex
                else:
                    raise BlipError(self.error_string % {'err':str(ex)})
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
                    raise KeyError(att)
            
            return f(*args,**kwargs)
        return wrapper
    return deco


def auto_flush(f):
    def deco(*args,**kwargs):
        # for now we are just going to flush each time
        print "auto flush Entering", f.__name__
        result = self.f(*args,**kwargs)
        if args and hasattr(args,'flush'):
            args[0].flush() # we are assuming the first arg is self
        return result
    return deco

class Blip():
    def __init__(self,**kwargs):
        self.key = None
        self.value = None
        self.location = None
        self.auto_flush = True
        for k,v in kwargs.iteritems():
            if not hasattr(self,k):
                raise KeyError(k)
            setattr(self,k,v)

    @smart_error('Error while getting value: %(err)s')
    @auto_flush
    @require_attribute('key')
    def get_value(self,key=None):
        if key: self.key = key
        if not self.value:
            self.update_value()
        return self.value

    @smart_error('Error while setting value: %(err)s')
    @auto_flush
    @require_attribute('value')
    def set_value(self,value):
        self.value = value

    @smart_error('Error while incrementing value: %(err)s')
    @auto_flush
    @require_attribute('value')
    def increment(self,to_add):
        try:
            self.value += to_add
        except TypeError:
            raise BlipError('Can not increment a %s value' % type(self.value))

    @smart_error('Error while flushing: %s(err)s')
    @require_attribute(['key','value'])
    def flush(self):
        # flushing is going to populate if we have a key
        # and no value
        fh = open(utils.next_key_path(self.key),'w')
        fh.write(self.value)
        fh.close()

# going to be the class we use to manipulate the key/value pairs

import decorator

from ConfigParser import SafeConfigParser
config = SafeConfigParser()
config.read('dev_config.ini')

from utils import smart_error, require_attribute, auto_flush, key_manager

from data_handler import EasyHandler


class BlipError(Exception):
    pass

class Blip(object):
    def __init__(self,*args,**kwargs):
        self._key = None
        self._value = None
        self.location = None
        self.auto_flush = True
        self.handler = None
        for k,v in kwargs.iteritems():
            if not hasattr(self,k):
                raise KeyError(k)
            setattr(self,k,v)
        
        # we give u the option of loading ur own handler, how nice
        if not self.handler:
            handler = EasyHandler


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
        self.handler.flush(self)

    @require_attribute('_key')
    def update_value(self):
        # read in the newest value
        self._value = self.handler.read(self)






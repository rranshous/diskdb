# going to be the class we use to manipulate the key/value pairs

#import decorator

from ConfigParser import SafeConfigParser
config = SafeConfigParser()
config.read('dev_config.ini')

from utils import smart_error, require_attribute, auto_flush, key_manager

from data_handler import EasyHandler, EasyPickler

# simple strait up k/v
class SimpleBlip(object):
    def __init__(self,key=None,value=None):
        self.key = key
        self.value = value
        self.handler = EasyHandler()
        self.location = None

    def increment(self,to_add):
        try:
            self._value += to_add
        except TypeError:
            raise

    @require_attribute('key')
    def flush(self):
        # write our value out
        self.handler.flush(self)

    @require_attribute('key')
    def update_value(self):
        # read in the newest value
        self.value = self.handler.read(self)

# almost as simple but value's can be simple objects
class PickleBlip(object):
    def __init__(self,key=None,value=None):
        self.key = key
        self.value = value
        self.handler = EasyPickler
        self.location = None



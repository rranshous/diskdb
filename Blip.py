# going to be the class we use to manipulate the key/value pairs

from utils import require_attribute, KeyManager
from data_handler import EasyHandler, EasyPickler

# simple strait up k/v
class SimpleBlip(object):
    def __init__(self,key=None,value=None,data_root=None):
        self.key = key
        self.value = value
        self.location = None
        self.data_root = data_root
        self.handler = EasyHandler()
        self.key_manager = KeyManager(data_root)

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
    def __init__(self,key=None,value=None,data_root=None):
        self.handler = EasyPickler()
        Super(PickleBlip,self).__init__(key,value,data_root)




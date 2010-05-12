# going to be the class we use to manipulate the key/value pairs

from utils import require_attribute, KeyManager
from data_handler import EasyHandler, EasyPickler
# simple strait up k/v
class SimpleBlip(object):
    def __init__(self,data_root,key=None,value=None):
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
        print 'flushing'
        # write our value out
        self.handler.flush(self)
        return True

    @require_attribute('key')
    def update_value(self):
        # read in the newest value
        self.value = self.handler.read(self)
        return True

    @require_attribute('key')
    def get_value(self,key=None):
        """ convenience function for updating value
            and returning it, optionally setting key """
        if key:
            self.key = key
        self.update_value()
        return self.value

    @require_attribute('key')
    def set_value(self,v,key=None):
        """ convenience function for setting value
            and than flushing, optionally setting key """
        if key:
            self.key = key
        self.value = v
        self.flush()
        return True

    @require_attribute('key')
    def delete(self):
        """ deletes the key's directory off the drive """
        self.handler.delete(self)

# almost as simple but value's can be simple objects
class PickleBlip(SimpleBlip):
    def __init__(self,data_root,key=None,value=None):
        super(PickleBlip,self).__init__(data_root,key,value)
        self.handler = EasyPickler()




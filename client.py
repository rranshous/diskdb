

# simple client sitting in front of the Blip obj
# for simple k/v setting / getting

from Blip import SimpleBlip # default blip type

class Client(object):
    def __init__(self,storage_root,blip_cls=None):
        # they can provide their own blip class, else simple
        self.Blip = blip_cls or SimpleBlip

        # where is all this data going
        self.storage_root = storage_root

    def get(self,k):
        blip = Blip(self.storage_root,k)
        return blip.get_value()

    def set(self,k,v):
        blip = Blip(self.storage_root,k,v)
        blip.flush()
        return True
        

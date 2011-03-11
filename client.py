

# simple client sitting in front of the Blip obj
# for simple k/v setting / getting

class Client(object):
    def __init__(self,storage_root):
        self.storage_root = storage_root

    def get(self,k):
        blip = Blip(self.storage_root,k)
        return blip.get_value()

    def set(self,k,v):
        blip = Blip(self.storage_root,k,v)
        blip.flush()
        return True
        

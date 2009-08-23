class KeyManager(object):

    def __init__(self,storage_dir):
        self.storage_dir = storage_dir

    def next_key_path(self,key):
        if not key:
            raise KeyError('key')

        import time

        # we are going to return the absolute system path to the next
        # version of the key's file

        # we are going to do /<storage_dir>/<key[:150]/<timestamp>.txt
        # there will be a file named key in the directory, so that keys which
        # are 150 > chars can be sure they are in the right place

        path = '%s/%s/value_%s.txt' % ( self.storage_dir,
                                        key[:150],
                                        time.time() )

        return path

    def last_key_path(self,key):
        print "getting last key path"

        if not key:
            raise KeyError('key')

        import glob

        # we want to get a list of the dirs which are they key
        dirs = glob.glob('%s/%s' % (self.storage_dir,key))
        key_dir = None # where they key's folder is

        # now that we have all the dirs which match, lets see if we got back
        # more than one
        if len(dirs) > 1:
            # this should only happen if the key is 150+ chars long
            if len(key) is not 150:
                raise Exception('Found more than one dir for key')

            # we need to enter the dirs and figure out which one actually has
            # our key
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

        print key_dir

        # now we need to find the most recent value file
        files = glob.glob('%s/value_*' % key_dir)
        # get rid of the prefix for sorting
        files = sorted(( int(x[len(key_dir) + 6:-4]) for x in files ))

        print files

        # grab the most recent
        file_name = 'value_%s' % files[0]

        print file_name

        return '%s/%s' % key_dir/file_name

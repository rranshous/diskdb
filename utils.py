class ToolBelt(object):

    def __init__(self,config=None,config_file=None):
        self.config = config
        self.config_file = config_file


    def next_key_path(self,key):
        if not key:
            raise KeyError('key')

        # we are going to return the absolute system path to the next
        # version of the key's file

        # we are going to do /<storage_dir>/<key[:150]/<timestamp>.txt
        # there will be a file named key in the directory, so that keys which
        # are 150 > chars can be sure they are in the right place

        path = '%s/%s/%s.txt' % ( self.storage_dir or '/tmp',
                                  key[:150],
                                  time.time() )

        return path

    def last_key_path(self,key):
        if not key:
            raise KeyError('key')

        # we want to get a list of the dirs which are they key
        dirs = glob.glob('%s/%s' % (this.storage_dir or '/tmp',key)
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
                with fh as open('%s/%s' % (d,'key.txt'),'r'):
                    _k = fh.readline().rstrip()
                    if _k == key:
                        key_dir = d

        else:
            key_dir = dirs[0]

        if not key_dir:
            raise Exception('Could not find key directory')

        # now we need to find the most recent value file
        files = glob.glob('%s/value_*' % key_dir)
        # get rid of the prefix for sorting
        files = sorted(( int(x[len(key_dir) + 6:]) for x in files ))
        # grab the most recent
        file_name = 'value_%s' % files[0]

        return '%s/%s' % key_dir/file_name
        

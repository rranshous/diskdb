import pickle, os, shutil

class Handler(object):
    def _get_info(self,to_handle):
        # we want to return the key and the value
        return (to_handle.key,to_handle.value)
    def _get_value(self,to_handle):
        return to_handle.value
    def _get_key(self,to_handle):
        return to_handle.key
    def _get_next_path(self,to_handle,key):
        return to_handle.key_manager.next_key_path(key)
    def _get_last_path(self,to_handle,key):
        return to_handle.key_manager.last_key_path(key)

class Flusher(Handler):
    def flush(self,to_flush):
        # get the key / value from the object
        key, value = self._get_info(to_flush)

        # get the next key's path
        file_path = self._get_next_path(to_flush,key)
        file_path_dir = os.path.dirname(file_path)

        # if the path doesn't exist we need to create it
        self._if_create_path(file_path_dir)

        # write out the key
        self._write_key(file_path_dir,key)

        # actually write the data out
        self._write_data(file_path,value)

    def _if_create_path(self,file_path_dir):
        # if the path doesn't exist than we need to create it
        # if the key's dir doesn't exist, create it
        if not os.path.exists(file_path_dir):
            os.makedirs(file_path_dir)

    def _write_key(self,file_path_dir,key):
        # we need to write the key to a txt file w/in the dir
        with file('%s/key.txt' % file_path_dir,'w') as fh:
            fh.write(key)

    def _write_data(self,file_path,value):
        # lay the data down
        with file(file_path,'w') as fh:
            print 'writing: %s' % (file_path)
            fh.write(value)

class Reader(Handler):
    def read(self,to_read):
        # get our key / value
        key = self._get_key(to_read)
        key_path = self._get_last_path(to_read,key)

        # read in our value, None means there is no value
        value = self._read_value(key_path)

        return value

    def _read_value(self,key_path):
        # if we didn't get a path, no point on continuing
        if not key_path:
            return None

        try:
            with file(key_path,'r') as fh:
                value = ''.join(fh.readlines())
                print 'reading: %s %s' % (key_path,len(value))
        except IOError:
            value = None

        return value

class Deleter(Handler):
    def delete(self,to_handle):
        # delete the key's root
        key = super(Deleter,self)._get_key(to_handle)
        if key:
            key_path = self._get_last_path(to_handle,key)
            if key_path:
                key_root = os.path.dirname(key_path)
                shutil.rmtree(key_root)

class PicklyFlusher(Flusher):
    def _get_info(self,to_handle):
        # we are going to pickle the value
        key, value = super(PicklyFlusher,self)._get_info(to_handle)
        return (key,pickle.dumps(value))

class PicklyReader(Reader):
    def read(self,to_read):
        # we want to unpickle the value as it comes out
        value = super(PicklyReader,self).read(to_read)
        if value:
            value = pickle.loads(value)
        return value

class EasyHandler(Flusher,Reader,Deleter):
    pass

class EasyPickler(PicklyFlusher,PicklyReader,Deleter):
    pass

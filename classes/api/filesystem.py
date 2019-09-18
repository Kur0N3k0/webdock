from classes.api.api import API
import os
import glob

class FilesystemAPI(API):
    def __init__(self, base):
        super()
        self.base = base

    def listing(self, username, path):
        result = { "is_base": True, "path": "/file/{}".format(path), "dir": [], "file": [] }
        for f in glob.glob(self.base + username + "/" + path + "/*"):
            if os.path.isdir(f):
                result["dir"] += [ os.path.basename(f) ]
            else:
                result["file"] += [ os.path.basename(f) ]
        return result

    def mkdir(self, path):
        pass

    def rmdir(self, path):
        pass
    
    def write(self, file):
        pass
    
    def read(self, file):
        pass
    
    def logging(self):
        pass
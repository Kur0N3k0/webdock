from classes.api.api import API
import os
import glob

class FilesystemAPI(API):
    def __init__(self, base):
        super()
        self.base = base

    def listing(self, username, path):
        result = { "is_base": True, "path": "/file/" + path, "dir": [], "file": [] }
        for f in glob.glob(self.base + username + "/" + path + "/*"):
            if os.path.isdir(f):
                result["dir"] += [ os.path.basename(f) ]
            else:
                result["file"] += [ os.path.basename(f) ]
        return result

    def mkdir(self, username, path):
        rpath = self.base + username + "/" + path
        if not os.path.exists(rpath):
            os.mkdir(rpath)
            return True
        return False

    def rmdir(self, username, path):
        rpath = self.base + username + "/" + path
        if not os.path.exists(rpath):
            return False
        os.rmdir(rpath)
        return True
    
    def write(self, username, path, data):
        rpath = self.base + username + "/" + path
        if not os.path.exists(rpath):
            return False
        f = open(rpath, "wb")
        f.write(data)
        f.close()
        return True
    
    def read(self, username, path):
        rpath = self.base + username + "/" + path
        if not os.path.exists(rpath):
            return False
        with open(rpath, "wb") as f:
            result = f.read()
        return result
    
    def logging(self):
        pass
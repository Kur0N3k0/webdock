from classes.api.api import API
import os
import glob
import shutil
from util import json_result

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
        return json_result(0, result)

    def mkdir(self, username, path):
        rpath = self.base + username + "/" + path
        if not os.path.exists(rpath):
            os.mkdir(rpath)
            return json_result(0, "success")
        return json_result(-1, "path not exist")

    def rmdir(self, username, path):
        path = self.base + username + "/" + path
        if "../" in path:
            return json_result(-1, "invalid path")
        if not os.path.exists(path):
            return json_result(-1, "path not exist")

        os.removedirs(path)
        return json_result(0, "success")
    
    def rm(self, path):
        if "../" in path:
            return json_result(-1, "invalid path")
        if not os.path.exists(path):
            return json_result(-1, "file not exist")
        if not os.path.isfile(path):
            return json_result(-1, "invalid type")

        os.remove(path)
        return json_result(0, "success")

    def mv(self, src, dst):
        if "../" in src or "../" in dst:
            return json_result(-1, "invalid path")
        if not os.path.exists(src) or not os.path.exists(dst):
            return json_result(-1, "invalid path")
        
        shutil.move(src, dst)
        return json_result(0, "success")

    def cp(self, src, dst):
        if "../" in src or "../" in dst:
            return json_result(-1, "invalid path")
        if not os.path.exists(src):
            return json_result(-1, "invalid path")
        
        shutil.copy(src, dst)
        return json_result(0, "success")

    def write(self, username, path, data):
        rpath = self.base + username + "/" + path
        if not os.path.exists(rpath):
            return False
        f = open(rpath, "wb")
        f.write(data)
        f.close()
        return json_result(0, "success")
    
    def read(self, username, path):
        rpath = self.base + username + "/" + path
        if not os.path.exists(rpath):
            return False
        with open(rpath, "rb") as f:
            result = f.read()
        return json_result(0, result)
    
    def logging(self):
        pass
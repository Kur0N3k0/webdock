from classes.api.api import API
import glob

class FilesystemAPI(API):
    def listing(self, tenant, path):
        return glob.iglob("upload/{}/{}".format(tenant, path), recursive=True)

    def mkdir(self, path):
        pass

    def rmdir(self, path):
        pass
    
    def write(self, file):
        pass
    
    def read(self, file):
        pass
from classes.daemon.daemon import Daemon
import threading

def docker_worker(daemon):
    while daemon.running:
        pass

class DockerDaemon(Daemon):
    def __init__(self):
        super()
        self.running = False
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=docker_worker, args=(self, ))
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()
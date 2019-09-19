import queue

class Daemon(object):
    def __init__(self):
        self.queue = []
    
    def start(self):
        raise "Daemon::start not implemented"
    
    def stop(self):
        raise "Daemon::start not implemented"
    
    def notify(self):
        raise "Daemon::notify not implemented"
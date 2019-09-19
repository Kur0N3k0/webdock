from classes.daemon.daemon import Daemon
import threading

class PaymentDaemon(Daemon):
    def __init__(self):
        super()
        self.running = False
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=payment_worker, args=(self, ))
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()
    
    def notify(self, payment):
        self.queue.put(payment)
        return True

def payment_worker(daemon: PaymentDaemon):
    while daemon.running:
        if daemon.queue.qsize() < 0:
            continue
        
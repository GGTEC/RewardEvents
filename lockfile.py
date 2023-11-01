import psutil

class LockManager:

    def __init__(self):
        self.already_running = False
        self.process = 0
        self.process_name = None
        self.process_actual = psutil.Process()

    def check(self):


        self.process_name = self.process_actual.name()


        for process in psutil.process_iter(attrs=['name']):
            if process.info['name'] == self.process_name:
                self.process += 1

        if self.process > 3:

            self.already_running = True

        else:
                
            self.already_running = False

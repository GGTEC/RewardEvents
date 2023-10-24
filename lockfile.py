import utils
import os
import pathlib

class LockManager:
    def __init__(self, label):
        self.lock_file_path = f"{utils.local_work('tempdir')}/instance_{label}.lock"
        self.already_running = False
        self.fd = None


    def lock(self):

        try:

            self.fd = os.open(self.lock_file_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)

            self.already_running = False

        except IOError:

            self.already_running = True

    def unlock(self):

        if self.fd is not None:
            os.close(self.fd)
            file_to_rem = pathlib.Path(self.lock_file_path)
            file_to_rem.unlink()
            self.fd = None

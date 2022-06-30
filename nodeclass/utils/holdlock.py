from __future__ import annotations

import errno
import fcntl
import time

class HoldLock:
    def __init__(self, file: str, timeout: int = 120):
        self.file = file
        self.timeout = timeout

    def __enter__(self):
        self.fd = open(self.file, 'w+')
        start = time.time()
        while True:
            if (time.time() - start) > self.timeout:
                raise IOError('Timeout waiting to lock file: {0}'.format(self.file))
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except IOError as e:
                # raise on unrelated IOErrors
                if e.errno != errno.EAGAIN:
                    raise
                else:
                    time.sleep(0.1)

    def __exit__(self, type, value, traceback):
        self.fd.close()

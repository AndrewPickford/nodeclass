import os
import pytest
import tempfile
import threading
import time
from reclass.utils.holdlock import HoldLock

lock_file_dir = tempfile.mkdtemp(prefix='reclass_tests')
lock_file_name = os.path.join(lock_file_dir, 'holdlock')

def teardown_module(module):
    if os.path.exists(lock_file_name):
        os.remove(lock_file_name)
    if os.path.exists(lock_file_dir):
        os.rmdir(lock_file_dir)

def test_holdlock_getlock():
    # No competing threads, should lock immediately
    start = time.time()
    with HoldLock(lock_file_name):
        locked = time.time()
    delay = locked-start
    assert (delay < 1)

def test_holdlock_timeout():
    with pytest.raises(IOError):
        with HoldLock(lock_file_name):
            with HoldLock(lock_file_name, timeout=2):
                pass

def test_holdlock_threading():
    def inner(label):
        with HoldLock(lock_file_name):
            time.sleep(0.1)
            with open(write_file_name, 'a+') as file:
                for i in range(0, 3):
                    file.write('{0}/{1} '.format(label, i))
                    time.sleep(0.05)

    write_file_name = os.path.join(lock_file_dir, 'write_file')
    a = threading.Thread(target=inner, args=('A',))
    b = threading.Thread(target=inner, args=('B',))
    c = threading.Thread(target=inner, args=('C',))
    a.start()
    b.start()
    c.start()
    a.join()
    b.join()
    c.join()
    with open(write_file_name, 'r') as file:
        contents = file.read()
    if os.path.exists(write_file_name):
        os.remove(write_file_name)
    order = [ 'ABC', 'ACB', 'BAC', 'BCA', 'CAB', 'CBA' ]
    expected = [ ''.join([ '{0}/{1} '.format(l, n) for l in letters for n in [ 0, 1, 2 ] ]) for letters in order ]
    assert (contents in expected)

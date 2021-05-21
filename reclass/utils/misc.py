import os

def ensure_directory_present(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

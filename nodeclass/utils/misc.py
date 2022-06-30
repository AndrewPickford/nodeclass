from __future__ import annotations

import os

def ensure_directory_present(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)

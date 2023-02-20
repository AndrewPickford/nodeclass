#!/usr/bin/python3

import os
import sys

# path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, os.path.join(os.path.dirname(__file__),'src'))

from nodeclass.cli.main import main

if __name__ == "__main__":
    main()

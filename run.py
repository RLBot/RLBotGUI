import os
import sys

from rlbot_gui import gui

# Insert the pkgs directory into the python path. This is necessary when
# running the pynsist installed version.
scriptdir, script = os.path.split(__file__)
pkgdir = os.path.join(scriptdir, 'pkgs')
sys.path.insert(0, pkgdir)

if __name__ == '__main__':
    gui.start()

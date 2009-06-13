#! /usr/bin/env python

import sys
import subprocess

print "python:", sys.version.replace("\n", " ")

try:
    out = subprocess.Popen(["buildbot", "--version"],
                           stdout=subprocess.PIPE).communicate()[0]
    print "buildbot:", out.replace("\n", " ")
except OSError:
    pass

try:
    out = subprocess.Popen(["darcs", "--version"],
                           stdout=subprocess.PIPE).communicate()[0]
    full = subprocess.Popen(["darcs", "--exact-version"],
                            stdout=subprocess.PIPE).communicate()[0]
    print
    print "darcs:", out.replace("\n", " ")
    print full.rstrip()
except OSError:
    pass

try:
    import platform
    out = platform.platform()
    print
    print "platform:", out.replace("\n", " ")
    print full.rstrip()
except OSError:
    pass

#!/usr/bin/env python

# Simple Binary Description (SBuD)
# Dis(-sector/-assembler)

# Ange Albertini, 2010 - 2019 MIT license

__version__ = "0.0.1" # https://semver.org/
__progname__ = "Dis.py" # SBuD's DisPy
__date__ = "2019-03-04"

import json
import struct
import argparse
from utils import *
from datatypes import *
import os.path
from os import system
import datatypes
import urllib

from parsers import *


def section(s):
  return [("; %s " % s) .ljust(80, "="), ""]


class sbudEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, (FileInfo, datatypes.BaseType, Structure)) and \
    "jsonFilter" in obj.__dict__:
      return {k: self.default(obj.__dict__[k]) for k in (obj.jsonFilter) if k in obj.__dict__}
    elif isinstance(obj, (str, int, dict, bool)):
      return obj
    elif isinstance(obj, (list)):
      return [self.default(k) for k in obj]
    else:
      return obj.__dict__


if __name__ == "__main__":
  # Newline char
  NL = "\n"

  parser = argparse.ArgumentParser(
    prog=__progname__,
    description="a dis-sector/-assembler")
  parser.add_argument('input', metavar='input', type=str) #, dest='inputName')
  parser.add_argument("-v", "--version", action="version", version="SBuD's DisPy %s by Ange Albertini (%s)" % (__version__, __date__))
  parser.add_argument("-j", "--json", metavar='output.json', help="define JSON output file")
  parser.add_argument("-a", "--asm", metavar='output.asm', help="define NASM output file")
  args = parser.parse_args()

  fn = args.input

  with open(fn, "rb") as f:
    contents = f.read()

  fileName = os.path.basename(fn)
  fileInfo = FileInfo(contents, fileName)

  parsers = [
    png.PNGparser,
    gif.GIFparser
  ]

  for parser in parsers:
    p = parser()
    if p.is_file(contents):
      [defs, source], fileInfo.struc = p.run(contents, fileName)
      text = []
      text += fileInfo.src
      text += [""]
      text += section("directives")
      text += asmDir()
      text += section("definitions")
      for def_ in defs:
        text += defs[def_]
        text += [""]

      text += section("code")

      # No bytes / Same line / new line
      NoSameNew = 1

      if NoSameNew == 1:
        showBytes(source, contents, sameLine=True, preLines=0, postLines=0, row=80)
      elif NoSameNew == 2:
        showBytes(source, contents, sameLine=False, preLines=1, postLines=0, row=0)


      offsets = sorted(source.d.keys())
      for offset in offsets:
        d = source.d[offset]
        text += d["preComs"] + d["src"] + d["postComs"]
        # separate basic blocks
        text += [""]

      text += [""]
      text = NL.join(text)


      if args.asm is None:
        print text
      else:
        with open(args.asm, "wb") as asmFile:
          asmFile.write(text)

      if args.json is not None:
        with open(args.json, "wb") as jsonFile:
          json.dump(fileInfo, jsonFile, sort_keys=True, indent=1, cls=sbudEncoder)

        # haven't found yet a better way to launch a local file
        # no matter the browser settings with hash parameters :(
        with open("launch.htm", "wb") as dummy:
         dummy.write("""<html>
            <title>DatJS launcher</title>
            <script type='text/javascript'>location='../datjs/dat.html#{json}'</script>
            <script type='text/javascript'>location='../../datjs/dat.html#{json}'</script>
          </html>
          """ .format (json=
            urllib.quote(json.dumps(fileInfo,cls=sbudEncoder)))
          )
            
        system("launch.htm")
      break
  else:
    print "no format recognized"

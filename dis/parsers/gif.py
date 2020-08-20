#!/usr/bin/env python

from parsers import Parser

import struct
import hashlib
from utils import *
from datatypes import *

#TODO: move to utils
def readFlags(ll, f):
  flags = {}
  for l in ll:
    flags[l[0]] = f & (2**(l[1]+1)-1)
    f >>= l[1]
  return flags


def skipSubBlocks(contents, offset):
  length = U8("SubBlockLength", "length")
  length.read(contents, offset)
  offset += 1
  while (length.raw != 0):
    offset += length.raw
    length.read(contents, offset)
    offset += 1
  return offset


class GIFparser(Parser):

  def is_file(self, contents):
    return contents.startswith(b"GIF") and (contents[3:6] in [b"87a", b"89a"])

  def run(self, contents, fn):
    defs = {}
    source = Source()
    offset = 0
    fileStruc = Structure("Type:GIF", offset, "file")

    depth = 0

    offset += process(contents, String("signature", 6, "magic"), offset, fileStruc, source, depth)
    depth += 1
    lsd = Structure("Logical Screen Descriptor", offset, "lsd")

    offset += process(contents, U16("Width", "dimension"), offset, lsd, source, depth)
    offset += process(contents, U16("Height", "dimension"), offset, lsd, source, depth)
    lsFlags = Hex8("Flags", "flags")
    offset += process(contents, lsFlags, offset, lsd, source, depth)
    flags = readFlags([
      ["GlobalColorTable",1],
      ["ColorResolution", 3],
      ["Sort", 1],
      ["GCTSize", 3],
    ][::-1],
      lsFlags.raw
    )

    offset += process(contents, Hex8("bgIndex", "index"), offset, lsd, source, depth)
    offset += process(contents, Hex8("ratio", "flags"), offset, lsd, source, depth)
    if flags["GlobalColorTable"] == 1:
      paletteSize = 3*(2<<(flags["GCTSize"]))
      offset += paletteSize # process(contents, Blob("GlobalPalette", paletteSize, "palette"), offset, fileStruc, source, depth)
      #TODO: incbin

    fileStruc.subEls.append(lsd)

    while (True):
      depth += 1
      separator = String("Separator", 1, "separator")
      separator.read(contents, offset)
      if (separator.raw == b"!"): # extension
        extension = Structure("Extension", offset, "extension")
        offset += 1
        extension.subEls.append(separator)
        offset += process(contents, Hex8("Function", "funccode"), offset, extension, source, depth)
        offset = skipSubBlocks(contents, offset)
        #TODO: incbin
        fileStruc.subEls.append(extension)
        depth -= 1
      elif (separator.raw == b","):
        lsd = Structure("Image Descriptor", offset, "Isd")
        offset += 1
        lsd.subEls.append(separator)
        offset += process(contents, U16("leftPos", "dimension"), offset, lsd, source, depth)
        offset += process(contents, U16("TopPos", "dimension"), offset, lsd, source, depth)
        offset += process(contents, U16("Width", "dimension"), offset, lsd, source, depth)
        offset += process(contents, U16("Height", "dimension"), offset, lsd, source, depth)
        offset += process(contents, Hex8("lsFlags", "flags"), offset, lsd, source, depth)
        flagsBits = [
          ["LocalColorTable", 1],
          ["Interlace", 1],
          ["Sort", 1],
          ["Reserved", 2],
          ["LCTSize", 3]
        ]
        # lctPalette?
        offset += process(contents, U8("LZWSize", "size"), offset, lsd, source, depth)
        offset = skipSubBlocks(contents, offset)
        #TODO: incbin
        fileStruc.subEls.append(lsd)
        depth -= 1
      elif (separator.raw == b";"):
        term = Structure("Terminator", offset, "separator")
        offset += 1
        term.subEls.append(separator)
        fileStruc.subEls.append(term)
        break

    return [defs, source], fileStruc

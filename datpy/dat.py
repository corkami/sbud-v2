#!/usr/bin/env python

# Simple Binary Description (SBuD)
# Dat(-a visualiser)

# Ange Albertini, 2010 - 2019 MIT license

__version__ = "0.0.1" # https://semver.org/
__progname__ = "Dat.py" # SBuD's DatPy
__date__ = "2019-03-04"

import json
import sys
import base64
import hashlib
import pprint
import re
import datutils
from ansi import *


def Hexii(v):
  """returns a string definition handling all escapes and octal/hex characters
  from a byte"""
  ESCAPE = {
    b"\\"  :"\\\\",
    b"`"   :"\\`",
    # b"'" :"\\'"  # not needed since we use backquote to enable escaping
    # b'"' :'\\"',
    # b"?" :"\\?",
    b"\x07":"\\a", # BEL
    b"\x08":"\\b", # BS
    b"\x09":"\\t", # TAB
    b"\x0A":"\\n", # LF
    b"\x0B":"\\v", # VT
    b"\x0C":"\\f", # FF
    b"\x0D":"\\r", # CR

#    b"\x1A":"^Z", # Ctrl-Z
    b"\x1B":"\\e", # ESC
  }
  c = bytes([v])
  if c in ESCAPE:
    return (ESCAPE[c])

  # printable ASCII
  if v >= ord(' ') and v <= ord('~'):
    return "." + chr(v)

  # octal short
  if v < 8:
    return "\\%x" % v

  return "%02x" % v


def mixedHex(content, strucOffset, lineOffset, lineLength, indexes):
  l = []
  _content = content[lineOffset: lineOffset + lineLength]
  for i, c in enumerate(_content):
    if i+lineOffset-strucOffset in indexes:
      l.append(Hexii(c))
    else:
      l.append("%02X" % c)
  r = " ".join(l)
  return r


def getSizeIdx(struc, subEls, offset):
  indexes = set()
  if "size" not in struc:
    size = 0
    for el in subEls:
      if el["offset"] < offset:
        print("OMG, wrong offset", el)
      # are empty leaves OK ?
      if el["size"] == 0:
        print("OMG, empty offset", el)

      # collect nibbles to be printed as HexII
      size = max(size, el["offset"] - offset + el["size"])
      if "ASCII" in el and el["ASCII"] == True:
        for i in range(el["size"]):
          indexes.add(el["offset"] - offset + i)
  return size, indexes


def mergeBlocks(left, right, spacing=3, width=None):
  if width is None:
    width = max(rawLen(_) for _ in left)
  out = []
  for i, _ in enumerate(left):
    if i < len(right):
      out.append(rawljust(left[i], width) + spacing*" " + right[i])
    else:
      out.append(left[i])
  if len(right) > len(left):
    for i in range(len(left), len(right)):
      out.append((width + spacing)*" " + right[i])
  return out


def outputEls(content, theme, struc, leaves, depth):
  name, type_, offset = struc["name"], struc["type"], struc["offset"]
  offsetLen = len("%X" % len(content)) + 1
  mask = "%%0%iX" % offsetLen
 
  # no size specified? compute it
  size, indexesASCII = getSizeIdx(struc, leaves, offset)  

  sStructure = AnsiStr()
  sStructure.underlineText(name.title())
  sStructure.text += " [{type}]".format(type=type_)
  sStructure.openTag(0, theme.bg) # will be closed at EOL on rendering
  sStructure.openTag(0, theme.font) # will be closed at EOL on rendering

  lines = {}
  delta = offset%16
  startOffset = offset - delta
  endOffset = offset+size - (offset+size)%16

  for i in range(startOffset, offset + size, 16):
    lines[i] = AnsiStr(mixedHex(content, offset, i, 16, indexesASCII))
  lines[startOffset].text = delta * "   " + lines[startOffset].text[delta*3:]
  lines[endOffset].text = lines[endOffset].text[:((offset + size) % 16) * 3 - 1] + "   " * (16-((offset + size) % 16))


  fieldVals = []
  for i, el in enumerate(sorted(leaves, key=lambda x:int(x["offset"]))):
    color = theme.highlights[i % len(theme.highlights)]
    fieldVals.append([
      fg("+%02x" % (el["offset"] - offset), theme.hex),
      fg(el["name"], color),
      fg(repr(el["value"])[1:-1].replace("\\\\", "\\"), # FIXME - used to keep correct escaping?
        color)
      ])

    lineOffset = el["offset"] - el["offset"] % 16
    lines[lineOffset].fg((el["offset"] - lineOffset)*3, (el["offset"]+el["size"] - lineOffset)*3 - 1, color, default=theme.dimmed)
    lines[lineOffset].openTag(0, theme.dimmed)
    if (el["offset"] % 16)+el["size"] > 16:
      lines[lineOffset+16].fg(
        0,
        (el["offset"]+el["size"]-16 - lineOffset)*3 - 2,
        color
      )

  width = max(rawLen(x[1]) for x in fieldVals)

  lFieldVals = []
  # hack to turn change color of undefined nibbles
  
  for fieldVal in fieldVals:
    loffset, field, value = fieldVal
    lFieldVals.append(loffset + " " + rawljust(field, width + 1) + " " + value)

  HexBlock = []
  for i in range(startOffset, offset + size, 16):
    l = theme.bg+"  {offset}{col} ".format(
      offset = fg(mask % i, theme.hex),
      col= fg(":", bBlack),
      depth = fg(" / ", bBlack).join(depth)
      ) + " "

    l += repr(lines[i])
    HexBlock.append(l)

  
  #bottom lowNibbles line
  #TODO? optionally outside of the recursive display
  lowNibbles = (offsetLen + 2+4)*" " + fg("  ".join("%x".ljust(2) % i for i in range(16)), theme.hex)

  #OPTIONAL - low nibbles lines below hex values
  HexBlock.append(lowNibbles)
  
  print(repr(sStructure) + " (%X+%X)" % (offset, size))
  #OPTIONAL: low nibbles line above hex values
  #print lowNibbles

  bVertical = True
  bVertical = False
  if bVertical:
    print("\n".join(HexBlock))
    print()
    print("\n".join(mergeBlocks([" "], lFieldVals, spacing=offsetLen)))
    print()
  else:
    # Horizontal
    print("\n".join(mergeBlocks(HexBlock, lFieldVals, spacing=4)))


def outputStruc(content, theme, struc, depth=[]):
  leaves = []
  substrucs = []
  for el in sorted(struc["subEls"], key=lambda x:int(x["offset"])):
    # collect leaves or process all sub-structures later
    if "subEls" in el:
      substrucs.append(el)
    else:
      leaves.append(el)
  if leaves:
    outputEls(content, theme, struc, leaves, depth)
  print()
  for substruc in substrucs:
    outputStruc(content, theme, substruc, depth + [struc["type"]])


if __name__ == "__main__":
  with open(sys.argv[1], "rb") as jsonFile:
    myJson = json.load(jsonFile)
  theme = sys.argv[2].lower() if len(sys.argv) >= 3 else "dark"
  contents = base64.b64decode(myJson["b64contents"])
  fileLen = myJson["length"]
  assert len(contents) == fileLen
  hash_ = hashlib.sha256(contents).hexdigest().lower()
  assert hash_ == myJson["SHA256"].lower()
  header = [
    "length: {len:d} (0x{len:x})".format(len=fileLen),
    "MD5:    %s" % hashlib.md5(contents).hexdigest().lower(),
    "SHA1:   " + hashlib.sha1(contents).hexdigest().lower(),
    "SHA256: " + hashlib.sha256(contents).hexdigest().lower(), # Pfeww, just below 80 columns :p
  ]
  print("\n".join(header))
  print()
  struc = myJson["struc"]
  outputStruc(contents, datutils.THEMES[theme], struc, [])

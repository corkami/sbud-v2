#!/usr/bin/env python

__all__ = [
  "FileInfo",
  "asmDir",
  "strToASM",
  "intToASM",
  "makeASMstruc",
  "declareStruc",
  "parse_struct",
  "parse_structs",
  "status",
  "lineStd",
  "lineStruc",
  "lineEndStruc",
  "Source",
  "Structure",
  "ROWNAMES",
  "process",
  "showBytes"
]

import struct
import base64
import hashlib

ROWNAMES = 50


class FileInfo:
  def __init__(self, contents, fileName):
    self.fileName = fileName
    self.length =  len(contents)
    self.b64contents = base64.b64encode(contents)
    self.MD5 = hashlib.md5(contents).hexdigest()
    self.SHA1 = hashlib.sha1(contents).hexdigest()
    self.SHA256 = hashlib.sha256(contents).hexdigest()
    self.struc = None
    self.jsonFilter = ("fileName", "length", "b64contents", "MD5", "SHA1", "SHA256", "struc")
    self.src = [
      "; '%s' (%i bytes)" % (self.fileName, self.length),
      "; MD5:    %s" % self.MD5,
      "; SHA1:   %s" % self.SHA1,
      "; SHA256: %s" % self.SHA256,
    ]


def asmDir(symbols="symbols.map"):
  return [
    "[map symbols %s]" % symbols,
   #"CPU 8086  ; to disable instructions",
   #"[warning -orphan-labels] ; pretty labels without semicolons",
    "",
  ]


def strToASM(s):
  """returns a string definition handling all escapes and octal/hex characters"""
  ESCAPE = {
    b"\\":b"\\\\",
    b"`" :b"\\`",
    # b"'":"\\'"  # not needed since we use backquote to enable escaping
    # b'"':'\\"',
    # b"?":"\\?",
    b"\x07":b"\a", # BEL
    b"\x08":b"\b", # BS
    b"\x09":b"\t", # TAB
    b"\x0A":b"\n", # LF
    b"\x0B":b"\v", # VT
    b"\x0C":b"\f", # FF
    b"\x0D":b"\r", # CR
    # no Ctrl-Z / \x1A :(
    b"\x1B":b"\e", # ESC
  }

  l = []
  for v in s:
    c = bytes([v])
    if c in ESCAPE:
      l.append(ESCAPE[c])
      continue

    if v >= ord(' ') and v <= ord('~'):
      l.append(c)
      continue

    if v < 8:
      l.append(b"\\%x" % v)
      continue

    l.append(b"\\x%02x" % v)
  r = b"".join(l)
  return r




def intToASM(i):
  """[0-FF] -> 0, 1... 9.. 0ah,... 0fh, 10h ... 9fh, 0ah"""
  if i < 10:
    return "%i" % i
  hex = "%xh" % i
  if hex[0] in "abcdef":
    hex = "0" + hex
  return hex



def parse_struct(data, struct_, index):
  size = struct.calcsize(struct_)
  return struct.unpack(struct_, data[index: index + size])[0], index + size

def parse_structs(data, structs_, index):
  size = struct.calcsize(structs_)
  return struct.unpack(structs_, data[index: index + size]), index + size


STRUC_SIZES = {1:"B", 2:"H", 4:"L"}
ASM_SIZES = {1:"b", 2:"w", 4:"d"}



def makeASMstruc(struc_):
  name, members = struc_
  sMembers = ["  .%s res%s 1" % (mName, ASM_SIZES[mSize]) for mName, mSize in members]
  return "\n".join(["", "struc %s" % name] + sMembers + ["endstruc"])


def declareStruc(struc_, values):
  name, members = struc_
  sMembers = []
  for i, m in enumerate(members):
    mName, mSize = m
    if values[i] != "0":
      sMembers.append("  at %s.%s, _d%s %s" % (name, mName, ASM_SIZES[mSize], values[i]))
  return "\n".join(["", "istruc %s" % name] + sMembers + ["iend"])


def status(offset, var=None):
  info = ""
  if var is not None:
    info = "name: '%s', size: '%i', value: '%s'" % (var.name, var.size, repr(var))
    # TODO: TBC
    offset -= var.size

  return ";%08x:%s" % (offset, info)


#TODO? unify line generation
def lineStd(depth, var, NoneVarLoc=0):
  dec = depth*" " if NoneVarLoc != 2 else (depth-1)*" " + "."
  if NoneVarLoc >= 1:
    dec += var.name.translate(str.maketrans("", "", "\"'(){}<>-#_.")) + " "
  dec += var.src
  dec = dec.ljust(ROWNAMES, " ")
  
  comm = "{pad}{var}".format(pad=depth*" ", var=var.name)
  return "{src}; {comm}".format(src=dec, comm=comm)


def lineStruc(depth, name, NoneVarLoc=0, comm=None):
  varName = name.split(" ")
  varName[0] = varName[0].lower()
  varName = "".join(varName)

  pad = (depth-1)*" "

  if NoneVarLoc == 0:
    dec = ";{{".format(dec=varName)
  elif NoneVarLoc == 1:
    dec = "{dec}:".format(dec=varName)
  elif NoneVarLoc == 2:
    dec = ".{dec}:".format(dec=varName)
  if comm is not None:
    comm = "{pad}{var} {{ //{comm}".format(pad=pad, var=name, comm=comm)
  else:
    comm = "{pad}{var} {{".format(pad=pad, var=name)
  return "{src}; {comm}".format(src=(pad+dec).ljust(ROWNAMES, " "), comm=comm)


def lineEndStruc(depth, name):
  return "".join([
    (depth*" "+ ";}").ljust(ROWNAMES, " "),
    "; ",
    depth*" ",
    "} //",
    name
  ])



class Structure:
  def __init__(self, name, offset, type_):
    #TODO? depth
    self.name = name
    self.offset = offset # redundant?
    self.type=type_
    # sub-elements
    self.subEls = []
    self.jsonFilter = ["name", "offset", "subEls", "type", "size"]
  
  def __repr__(self):
    return "%s %s" % (self.name, repr(self.subEls))


#TODO: put in separate class
class Source:

  def __init__(self):
    # maps dicts to offset
    self.d = {}


  def initEntry(self, offset):
    if offset not in self.d:
      # length, preComs, src, postComs
      self.d[offset] = {
        "length":0,
        "src":[],
        "preComs":[],
        "postComs":[],
      }


  def setlength(self, offset, length):
    self.initEntry(offset)
    self.d[offset]["length"] = length


  def append(self, listName, offset, lineOrlist):
    # append lines (single string or list) of code to specified offset
    self.initEntry(offset)
    l = self.d[offset][listName]
    if isinstance(lineOrlist, str):
      l.append(lineOrlist)
    elif isinstance(lineOrlist, list):
      l.extend(lineOrlist)

  def prepend(self, listName, offset, lineOrlist):
    # prepend lines but keep marker at original position (assumed it's for a comment)
    self.initEntry(offset)
    l = self.d[offset][listName]
    if isinstance(lineOrlist, str):
      l.insert(0, lineOrlist)
    elif isinstance(lineOrlist, list):
      l[:0] = lineOrlist


  def postComBefore(self, offset, lineOrlist):
    self.prepend("postComs", offset, lineOrlist)
  def postComAfter(self, offset, lineOrlist):
    self.append("postComs", offset, lineOrlist)

  def preComBefore(self, offset, lineOrlist):
    self.prepend("preComs", offset, lineOrlist)
  def preComAfter(self, offset, lineOrlist):
    self.append("preComs", offset, lineOrlist)

  def srcBefore(self, offset, lineOrlist):
    self.prepend("src", offset, lineOrlist)
  def srcAfter(self, offset, lineOrlist):
    self.append("src", offset, lineOrlist)

  #TOCHECK: preComs always grow upward and postComs always grow downward?
  def postCom(self, offset, lineOrlist):
    self.postComAfter(offset, lineOrlist)
  def preCom(self, offset, lineOrlist):
    self.preComBefore(offset, lineOrlist)
  def src(self, offset, lineOrlist):
    self.srcAfter(offset, lineOrlist)


  def set(self, offset, length=0, post=[], pre=[], src=[]):
    self.initEntry(offset)
    if length:
      self.setlength(offset, length)
    if post:
      self.postCom(offset, post)
    if pre:
      self.preCom(offset, pre)
    if src:
      self.src(offset, src)


#TODO? merge that in a big class
def process(contents, v, offset, struc, source, depth, NoneVarLoc=0, post=[], pre=[]):
  v.read(contents, offset)
  size = v.size
  struc.subEls.append(v)
  source.set(offset,
    length=size,
    pre=pre,
    src=lineStd(depth, v, NoneVarLoc=NoneVarLoc),
    # depth is not taken into account
    post=post,
  )
  #TODO: return a fail with estimated size?
  return size


def showBytes(source, contents, sizeThreshold=2, sameLine=True, preLines=0, postLines=0, row=80, borders=2):
  #TODO? put offset at start of preComs? for structures
  offsets = sorted(source.d.keys())
  for offset in offsets:
    d = source.d[offset]
    s = ";{offset:04x}:".format(pad=80*" ", offset=offset)

    length = d["length"]
    if length > 0:
      if length <= (2*borders+2) :
        s += " %s" % (" ".join("{nibble:02x}".format(nibble=c) for c in contents[offset:offset + length]))
      else:
        s += " %s ..... %s" % (" ".join("{nibble:02x}".format(nibble=c) for c in contents[offset:offset + borders]),
          " ".join("{nibble:02x}".format(nibble=c) for c in contents[offset + length - borders:offset + length])
          )
    
    if length > sizeThreshold:
      s += " (+%i)" % (length)

    if preLines > 0:
      source.preComAfter(offset, preLines * [""])

    if sameLine == True:
      d["src"][0] = "{line} {status}".format(
        line=d["src"][0].ljust(row),
        status=s
        )
    else:
      source.preComAfter(offset, "{pad}{status}".format(
        pad="".ljust(row),
        status=s
        ))

      if postLines > 0:
        source.preComAfter(offset, postLines * [""])



def __test():
  assert strToASM("\x00\0\000") == 'db `\\0\\0\\0`'
  assert strToASM("\\\x07\x08\x09\x0a\x0b\x0c\x0d\x1b") == 'db `\\\\\\a\\b\\t\\n\\v\\f\\r\\e`'
  assert strToASM("\b\010\x08") == 'db `\\b\\b\\b`'
  assert strToASM("\x00\x06\x07\x89PN \r\n\t'\\\"?`") == 'db `\\0\\6\\a\\x89PN \\r\\n\\t\'\\\\"?\\``'

  assert intToASM(0) == "0"
  assert intToASM(9) == "9"
  assert intToASM(10) == "0ah"
  assert intToASM(16) == "10h"
  assert intToASM(0xffffffff) == "0ffffffffh"

  assert status(0) == ";00000000:"
  assert status(0x12345678) == ";12345678:"


if __name__ == "__main__":
  __test()

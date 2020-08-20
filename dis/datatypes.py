#!/usr/bin/env python

__all__ = [
  "Hex8",   # 0A          -> "0x0A"
  "Hex16",  # 01 02       -> "0x0201"
  "Hex32",  # 01 02 03 04 -> "0x04030201"
  "Hex32b", # 01 02 03 04 -> "0x01020304"
  "U8",     # 0A          -> "10"
  "U16",    # 01 02       -> "513"
  "U32",    # 01 02 03 04 -> "67305985"
  "U32b",   # 01 02 03 04 -> "16909060"
  "Bitmask8",
  "Enum8",
  "Enum32",
  "String", # 49 48 44 52 -> "IHDR"
  "Blob",   # 49 48 44 52 -> "0x49, 0x48, 0x44, 0x52"
]

import struct
from utils import *

# TODO: turn ASM and repr into attributes?
class BaseType:
  def __init__(self, name, type_):
    self.name = name
    self.offset = None
    self.size = None
    # what kind of value for the format.
    # should be format agnostic? segment, box -> chunk
    self.type = type_

    # the actual raw content value, after transformation # 1, CAFEBABE, ...
    # (not the raw bytes)
    self.raw = None

    self.value = "<undefined>" # representation of the content (maybe simplified)

    self.src = "" # source to declare the content. often keyword/macro + value
    self.ASCII = False # should its hex be displayed as '00 50 0A 1A' or as '00 .P \n ^Z' ?
    self.jsonFilter = ["name", "offset", "size", "value", "ASCII", "type"]

  def __repr__(self):
    #TODO: remove this?
    return self.value.decode()

  def read(self, contents, offset):
    pass

  def defs(self):
    #TODO self.defs
    pass


class Hex8(BaseType):
  """unsigned 8b number, as fixed hex: 0A -> "0A" """

  def read(self, contents, offset):
    self.offset = offset
    self.size = 1
    self.raw = struct.unpack("<B", contents[offset:offset + self.size])[0]

    self.value = "0x%02x" % self.raw
    self.src = "db %s" % self.value


class Hex32(BaseType):
  """unsigned 32b number, little endian, as fixed hex: 01 02 03 04 -> "0x04030201" """

  def read(self, contents, offset):
    self.offset = offset
    self.size = 4
    self.raw = struct.unpack("<L", contents[offset:offset + self.size])[0]

    self.value = "0x%08x" % self.raw
    self.src = "dd %s" % self.value



class Hex32b(BaseType):
  """unsigned 32b number, big endian, as fixed hex: 01 02 03 04 -> "0x01020304" """

  def read(self, contents, offset):
    self.offset = offset
    self.size = 4
    self.raw = struct.unpack(">L", contents[offset:offset + self.size])[0]
    self.value = "0x%08x" % self.raw
    self.src = "ddbe %s" % self.value


class Hex16(BaseType):
  """unsigned 16b number, little endian, as fixed hex: 01 02 -> "0x0201" """

  def read(self, contents, offset):
    self.offset = offset
    self.size = 2
    self.raw = struct.unpack("<H", contents[offset:offset + self.size])[0]

    self.value = "0x%04x" % self.raw
    self.src = "dd %s" % self.value


class U8(BaseType):
  """unsigned 8b number, as decimal: 0A -> "10" """

  def read(self, contents, offset):
    self.offset = offset
    self.size = 1
    self.raw = struct.unpack("<B", contents[offset:offset + self.size])[0]
    self.value = "%i" % self.raw
    self.src = "db %s" % self.value



class U32(BaseType):
  """unsigned 32b number, little endian, as decimal: 01 02 03 04 -> "67305985" """

  def read(self, contents, offset):
    self.offset = offset
    self.size = 4
    self.raw = struct.unpack("<L", contents[offset:offset + self.size])[0]
    self.value = "%i" % self.raw
    self.src = "dd %s" % self.value



class U32b(BaseType):
  """unsigned 32b number, big endian, as decimal: 01 02 03 04 -> "16909060" """

  def read(self, contents, offset):
    self.offset = offset
    self.size = 4
    self.raw = struct.unpack(">L", contents[offset:offset + self.size])[0]
    self.value = "%i" % self.raw
    self.src = "ddbe %s" % self.value



class U16(BaseType):
  """unsigned 16b number, little endian, as decimal: 01 02 -> "513" """

  def read(self, contents, offset):
    self.offset = offset
    self.size = 2
    self.raw = struct.unpack("<H", contents[offset:offset + self.size])[0]
    self.value = "%i" % self.raw
    self.src = "dw %s" % self.value



class Bitmask8(BaseType):
  """8bit OR bitmask. takes a dictionary as argument"""

  def __init__(self, name, prefix, members):
    BaseType.__init__(self, name)
    self.prefix = prefix
    self.members = members

  def read(self, contents, offset):
    self.offset = offset
    self.size = 1
    self.raw = struct.unpack(">B", contents[offset:offset + self.size])[0]

    leftover = self.raw
    lValue = []
    lSrc = []

    for value, name in self.members.items():
      if leftover & value:
        leftover ^= value
        lValue.append(name)
        lSrc.append("%s.%s" % (self.prefix, name))
    
    if leftover:
      # TODO: in binary ?
      lValue.append("0x%02X" % leftover)
      lSrc.append("0x%02X" % leftover)

    if not lValue:
      lValue.append("0")

    if not lSrc:
      lSrc.append("0")

    self.value = " | ".join(lValue)
    self.src = "db %s" % (" | ".join(lSrc))


  def defs(self):
    return "\n".join(
      ["; %s (bitmask definition)" % self.name] +
      ["%s.%s equ %i" % (self. prefix, self.members[c], c) for c in self.members] + [""])    



class Enum8(BaseType):
  """32bit enumbit OR bitmask. takes a dictionary as argument"""

  def __init__(self, name, prefix, members):
    BaseType.__init__(self, name)
    self.prefix = prefix
    self.members = members


  def read(self, contents, offset):
    self.offset = offset
    self.size = 1
    self.raw = struct.unpack(">B", contents[offset:offset + self.size])[0]

    if self.raw in self.members:
      self.value = self.members[self.raw]
      self.src = "db %s.%s" % (self.prefix, self.value)
    else:
      self.value = "%02X" % self.raw
      self.src = "db %s" % self.value


  def defs(self):
    return "\n".join(
      ["; %s (enum definition)" % self.name] +
      ["%s.%s equ 0x%02X" % (self.prefix,self.members[c], c) for c in self.members] + [""])



class Enum32(BaseType):
  """32bit enumbit OR bitmask. takes a dictionary as argument"""

  def __init__(self, name, prefix, members):
    BaseType.__init__(self, name)
    self.prefix = prefix
    self.members = members


  def read(self, contents, offset):
    self.offset = offset
    self.size = 4
    self.raw = struct.unpack(">L", contents[offset:offset + self.size])[0]

    if self.raw in self.members:
      self.value = self.members[self.raw]
      self.src = "dd %s.%s ; %08x" % (self.prefix, self.value, self.raw)
    else:
      self.value = "%08X" % self.raw 
      self.src = "dd %s" % self.value


  def defs(self):
    return "\n".join(
      ["; %s (enum definition)" % self.name] +
      ["%s.%s equ 0x%08X" % (self.prefix,self.members[c], c) for c in self.members] + [""])



#TODO? merge String and Blob?
class String(BaseType):
  """ 4 chars string: 49 48 44 52 -> "IHDR" """

  def __init__(self, name, size, type):
    BaseType.__init__(self, name, type)
    self.size = size
    self.ASCII = True

  def read(self, contents, offset):
    self.offset = offset
    self.raw = struct.unpack("%is" % self.size, contents[offset:offset + self.size])[0]
    self.value = strToASM(self.raw)
    # remove the b'' extra characters
    self.src = "db `%s`" % repr(self.value)[2:-1].replace("\\\\", "\\") # FIXME


class Blob(BaseType):
  def __init__(self, name, size, type_):
    BaseType.__init__(self, name, type_)
    self.size = size

  def read(self, contents, offset):
    self.offset = offset
    self.raw = contents[offset:offset + self.size]
    # incbin <file>, offset, length
    self.value = "%s" % (", ".join("0x%02x" % c for c in self.raw))
    self.src = "db %s" % self.value



#TODO: refresh tests
def test():
  def dump(l):
    print(l.raw)
    print(repr(l))
    print(repr(l.src))

  s = "\1\2\3\4\5\6\7\8"

  print("datatypes test succeeded :p")


if __name__ == "__main__":
  test()

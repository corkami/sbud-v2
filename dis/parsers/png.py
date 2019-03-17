#!/usr/bin/env python

from parsers import Parser

import struct
import hashlib
from utils import *
from datatypes import *

class PNGparser(Parser):

  def is_file(self, contents):
    return contents.startswith("\x89PNG\r\n\x1a\n")

  def run(self, contents, fn):
    defs = {}
    source = Source()
    # libpng/png.h
    
    #TODO: not enforce this?
    offset = 0
  
    header = [
      "; Type: PNG"
    ]

    defs["ddbe"] = [
      "%macro ddbe 1",
      "  db (%1>>8*3) & 0ffh",
      "  db (%1>>8*2) & 0ffh",
      "  db (%1>>8*1) & 0ffh",
      "  db (%1>>8*0) & 0ffh",
      "%endmacro"
    ]

    fileStruc = Structure("Type:PNG", offset, "file")

    #TODO: to make obsolete via structure
    depth = 0

    offset += process(contents, String("signature", 8, "magic"), offset, fileStruc, source, depth)
    idatCount = 0

    CHUNK_TYPES = {
      "IHDR":"Image Header",
      "IDAT":"Image Data",
      "PLTE":"Palette",
      "IEND":"Image End",
    }

    chunkCount = 0
    while (offset < len(contents)):
      chunk = Structure("Chunk", offset, "chunk")
      chunkOffset = offset
      chunkCount += 1
      # the chunk starts here but we'll display once we have its type

      depth += 1

      length = U32b("length", "chunk length")
      length.read(contents, offset)
      offset += process(contents, length, offset, chunk, source, depth,
        NoneVarLoc=0,
        # it's what it should be but there's no actual validation
        post=";ddbe (chunk{count:d}.crc32 - chunk{count:d}.data)".format(count=chunkCount)
        )

      type_ = String("type", 4, "chunk type")
      offset += process(contents, type_, offset, chunk, source, depth, NoneVarLoc=2)
      chunk.name = "Chunk: " + CHUNK_TYPES[type_.raw]
      # now we can document the chunk type
      source.preCom(
        chunkOffset,
        # depth-1 because we're already a depth lower
        lineStruc(depth-1, "chunk%i" % chunkCount, NoneVarLoc=1,
        comm=CHUNK_TYPES[type_.raw])
      )

      dataOffset = offset
      
      depth += 1

      if length.raw > 0: # bug with incbin if length is null
        source.preComBefore(dataOffset, lineStruc(depth-1, "Data", NoneVarLoc=2))

        data = Blob("data", length.raw, "chunk data")
        data.read(contents, offset)
        blobLen = length.raw
        source.set(offset,
          src=(depth * " " + "incbin {FileName}, 0x{offset:x}, 0x{length:x}".format(
            FileName=`fn`, 
            offset=data.offset,
            length=blobLen,
          )),
          length=blobLen
        )

        source.postComAfter(offset, lineEndStruc(depth, "Data"))
      else:
        source.preCom(offset, (depth-2) * " " + ".data:")

      offset += length.raw
      depth -= 1

      size = process(contents, Hex32b("crc-32", "chunk crc32"), offset, chunk, source, depth,
        post=" ;> chunk{count:d}.crc32=CRC32(chunk{count:d}.type,chunk{count:d}.crc32)".format(count=chunkCount),
        NoneVarLoc=2,
      )

      depth -= 1
      source.postComAfter(offset, lineEndStruc(depth, "chunk"))
      offset += size

      fileStruc.subEls.append(chunk)
      #TODO: better logic?
      if `type_` == "IEND":
        break
    # source.src(offset, ["; END ".ljust(ROWNAMES, '"'), "", ])

    return [defs, source], fileStruc

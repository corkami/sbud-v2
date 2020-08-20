#!/usr/bin/env python

#__all__ = [
#  "AnsiStr",
#]

import re

def Ansi(l):
  if isinstance(l, int):
    l = [l]
  return "{esc}[{params}m".format(esc="", params=";".join("%i" % c for c in l))

Reset  = Ansi(0)
Bold   = Ansi(1)  # unreliable
Italic = Ansi(3)  # unreliable
Under  = Ansi(4)
Invert = Ansi(7)  # unreliable

UnderNot = Ansi(24)

Black    = Ansi(30)
Red      = Ansi(31)
Green    = Ansi(32)
Yellow   = Ansi(33)
Blue     = Ansi(34)
Magenta  = Ansi(35)
Cyan     = Ansi(36)
White    = Ansi(37) # don't use unless you set background

ResetFG  = Ansi(39)

bBlack   = Ansi(90)
bRed     = Ansi(91)
bGreen   = Ansi(92)
bYellow  = Ansi(93)
bBlue    = Ansi(94)
bMagenta = Ansi(95)
bCyan    = Ansi(96)
bWhite   = Ansi(97) # don't use unless you set background

ResetBG    = Ansi(49)

BlackBG    = Ansi(40)
RedBG      = Ansi(41)
GreenBG    = Ansi(42)
YellowBG   = Ansi(43)
BlueBG     = Ansi(44)
MagentaBG  = Ansi(45)
CyanBG     = Ansi(46)
WhiteBG    = Ansi(47)
bBlackBG   = Ansi(100)
bRedBG     = Ansi(101)
bGreenBG   = Ansi(102)
bYellowBG  = Ansi(103)
bBlueBG    = Ansi(104)
bMagentaBG = Ansi(105)
bCyanBG    = Ansi(106)
bWhiteBG   = Ansi(107)

class AnsiStr:
  def __init__(self, text=""):
    self.text = text
    self.opening = {}
    self.closing = {}

  def openTag(self, offset, *attribs):
    if offset not in self.opening:
      self.opening[offset] = []
    self.opening[offset].insert(0, *attribs)

  def closeTag(self, offset, attribs):
    if offset not in self.closing:
      self.closing[offset] = []
    self.closing[offset].append(attribs)

  def fg(self, start, end, color, default=ResetFG):
    self.openTag(start, color)
    self.closeTag(end, default)

  def bg(self, start, end, color, default=ResetBG):
    self.openTag(start, color)
    self.closeTag(end, default)

  def underline(self, start, end):
    self.openTag(start, Under)
    self.closeTag(end, UnderNot)

  def underlineText(self, s):
    self.openTag(len(self.text), Under)
    self.text += s
    self.closeTag(len(self.text)-1, UnderNot)

  def __repr__(self):
    output = ""
    for i, c in enumerate(self.text):
      if i in self.opening:
        output += "".join(self.opening[i])
      output += c
      if i in self.closing:
        output += "".join(self.closing[i])
    return output

  def ljust(self, width):
    return repr(self) + (width - len(self.text)) * " "


def rawText(s):
  return re.sub("\x1b\[[0-9;]*m", "", s)

def rawLen(s):
  return len(rawText(s))

def rawljust(s, width):
  return s + (width - rawLen(s)) * " "

def fg(s,c, default=ResetFG):
  return c + s + default

def bg(s,c, default=ResetBG):
  return c + s + default

def under(s):
  return Under + s + UnderNot

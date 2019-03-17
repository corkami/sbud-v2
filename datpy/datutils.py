#!/usr/bin/env python

from ansi import *

__all__ = [
  "THEMES",
]

class Theme:
  def __init__(self, bg, hex_, font, dimmed, highlights):
    self.hex = hex_
    self.bg = bg
    self.font = font
    self.dimmed = dimmed
    self.highlights = highlights

THEMES = {
  "dark":Theme(
    "",
    Green,
    bWhite,
    bBlack,
    # ?Blue unreadable on dark
    [
      bCyan,
      bRed,
      bYellow,
      bMagenta,
      bWhite,
    ],
  ),
  "light":Theme(
    "",
    Green,
    Black,
    White,
    # ?Yellow unreadable on light
    [
      Blue,
      Red,
      Cyan,
      Magenta,
      Black,
    ],
  )
}

#!/bin/env python3
import scrollphathd as sphd
import urllib.request
import time
import datetime
import telnetlib
import os
import subprocess

class fritzWatch:
  def __init__(self):
    self.tn = None

  def handle_ring(self):
    onoff = 0
    while True:
      if onoff == 0:
        sphd.fill(brightness=1., x=0, y=0)
      else:
        sphd.clear()
      onoff = 1 - onoff
      sphd.show()
      out = self.tn.read_eager()
      print('handle_ring:', out)
      if len(out):
        # Be conservative - return on any new input.
        sphd.clear()
        sphd.show()
        return
      time.sleep(0.5)

  def run(self):
    self.tn = telnetlib.Telnet('fritz.zuhause', 1012)
    while True:
      out = self.tn.read_some() # blocks! (And that's a good thing.)
      print('run:', out)
      if b';RING;' in out:
        if not b'\n' in out:
          self.tn.read_until((b'\n'), timeout = 1)
        self.handle_ring()
    tn.close()


sphd.rotate(degrees=180)
watch = fritzWatch()
watch.run()

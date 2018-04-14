#!/bin/env python3
import scrollphathd as sphd
import urllib.request
import time
import datetime
import telnetlib
import os
import subprocess

sphd.rotate(degrees=180)

def check_voip():
  def check_one_voip(sipno):
    try:
      resp = urllib.request.urlopen(url = 'http://fritz.zuhause/query.lua?SIP1=sip:settings/sip' + str(sipno) + '/activated',
                                    timeout = 5)
      html = resp.read()
      if b'"SIP1": "1"' not in html:
        return False
      return True
    except:
      return False

  for sipno in [0, 1, 3, 4]:
    if not check_one_voip(sipno):
      return 'TEL '
  return ''


def check_vdr():
   try:
     tn = telnetlib.Telnet(host = 'vdr.zuhause', port = 6419, timeout = 3)
     tn.expect([ b'220 vdr SVDRP VideoDiskRecorder .*$' ], 3)
     tn.write(b'QUIT\n')
     tn.close()
     return ''
   except:
     pass
   return 'VDR '

def check_wlan():
  try:
    output = subprocess.check_output("iw wlan0 link", shell=True, timeout=3).split(b'\n')[0]
    if b'Connected to' in output:
      return ''
  except:
    pass

  return 'WLAN '

def ping(hostname):
  try:
    output = subprocess.check_output("ping -c 1 -W 1 -q " + hostname, shell=True, timeout=3).split(b'\n')[3]
    if b'0% packet loss' in output:
      return True
  except:
    pass

  return False

def check_diskstation():
  if ping('diskstation.zuhause'):
    return ''
  return 'DISK '

def check_knet():
  if ping('www.google.com'):
    return ''
  return 'KNET '

def check_all():
  ret = ''
  ret += check_voip()
  ret += check_vdr()
  ret += check_wlan()
  ret += check_diskstation()
  ret += check_knet()

  return ret


def run():
  while True:
    msg = check_all()
    errseconds = 10
    steptime = 0.1
    lenmsg = len(msg)
    if lenmsg:
      print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), msg)
      sphd.write_string(msg)
      sphd.show()
      # only 3 chars fit, but the last one is a space!
      if lenmsg > 4:
        # it takes about 0.05s to display stuff
        for l in range(int(errseconds / (steptime + 0.05))):
          sphd.scroll(1)
          time.sleep(steptime)
          sphd.show()
      else:
        time.sleep(errseconds)
      sphd.clear()
      sphd.show()
    else:
      time.sleep(errseconds * 6)

run()


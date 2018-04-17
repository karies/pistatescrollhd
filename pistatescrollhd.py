#!/bin/env python3
import scrollphathd as sphd
import urllib.request
import time
import datetime
import telnetlib
import os
import subprocess


# Re-check time in case of active issues
errseconds = 10

sphd.rotate(degrees=180)

def listen_to_incoming_calls():
  # telnet to fritzbox, listen in background?
  pass

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
      return 'TEL'
  return None


def check_vdr():
   try:
     tn = telnetlib.Telnet(host = 'vdr.zuhause', port = 6419, timeout = 3)
     tn.expect([ b'220 vdr SVDRP VideoDiskRecorder .*$' ], 3)
     tn.write(b'QUIT\n')
     tn.close()
     return None
   except:
     pass
   return 'VDR'

def check_wlan():
  try:
    output = subprocess.check_output("iw wlan0 link", shell=True, timeout=3).split(b'\n')[0]
    if b'Connected to' in output:
      return None
  except:
    pass

  return 'WLAN'

def ping(hostname):
  try:
    output = subprocess.check_output("ping -c 1 -W 1 -q " + hostname, shell=True, timeout=3).split(b'\n')[3]
    if b'100% packet loss' not in output:
      return True
  except:
    pass
  print('PING RESULT:', output)
  return False

def check_diskstation():
  if ping('diskstation.zuhause'):
    return None
  return 'DISK'

def check_knet():
  if ping('www.google.com'):
    return None
  return 'KNET'

def check_all():
  ret = []
  ret.append(check_voip())
  ret.append(check_vdr())
  ret.append(check_wlan())
  ret.append(check_diskstation())
  ret.append(check_knet())

  # clear None-s
  ret = [x for x in ret if x is not None]

  return ret


def report(oldones):
    steptime = 0.1
    msg = ' '.join(oldones)
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), msg)
    sphd.write_string(msg)
    sphd.show()
    if len(msg) > 3:
      # it takes about 0.05s to display stuff
      for l in range(int(errseconds / (steptime + 0.05))):
        sphd.scroll(1)
        time.sleep(steptime)
        sphd.show()
    else:
      time.sleep(errseconds)
    sphd.clear()
    sphd.show()

def run():
  prev = []
  while True:
    res = check_all()
    oldones = [x for x in res if x in prev]
    prev = res
    if len(oldones):
      report(oldones)
    else:
      if len(res):
        time.sleep(errseconds)
      else:
        time.sleep(60)

run()


#!/usr/bin/env python3
from subprocess import PIPE
from subprocess import Popen
import os
import sys
import io
import json
'''
subprocessやもろもろを使っている関係で、python3.7.0以上を要求する
'''
ver = sys.version_info
if not (ver.major >= 3 and ver.minor >= 7):
    raise Exception('python 3.7.0以上で動作させてください')

'''
もし、すでにイメージ "siomiz/softethervpn" が起動していたら終了する
'''
query = ['curl', '--unix-socket', '/var/run/docker.sock', 'http://localhost/containers/json']
with Popen(query, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
    proc.wait(timeout=8)
    reader = io.TextIOWrapper(proc.stdout) 
    rets = json.loads(reader.read())
    for ret in rets:
        if ret['Image'] == 'siomiz/softethervpn' and \
                ret['State'] == 'running':
            Id = ret['Id']
            with Popen(['docker', 'kill', Id], stdout=PIPE, stdin=PIPE) as proc:
                proc.wait(timeout=8)
                reader2 = io.TextIOWrapper(proc.stdout)
                print(f'container id = {reader2.read().strip()} is kielld')

USERNAME = input('USERNAMEを指定してください:')
PASSWORD = input('PASSWORDを指定してください:')
PSK = input('PSKのパスワードを指定してください:')

query = \
    ['docker',
     'run',
     '-d',
     '--cap-add',
     'NET_ADMIN',
     '-p',
     '500:500/udp',
     '-p',
     '4500:4500/udp',
     '-p',
     '1701:1701/tcp',
     '-p',
     '1194:1194/udp',
     '-p',
     '5555:5555/tcp',
     '-e',
     f'USERNAME={USERNAME}',
     '-e',
     f'PASSWORD={PASSWORD}',
     '-e',
     f'PSK={PSK}',
     'siomiz/softethervpn']

with Popen(query, stdout=PIPE, stdin=PIPE) as proc:
    proc.wait(timeout=60)
    reader = io.TextIOWrapper(proc.stdout)
    while True:
        r = reader.read(1)
        if not r:
            break
        print(r, end='', flush=True)

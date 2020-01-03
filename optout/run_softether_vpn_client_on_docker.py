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
もし、すでにイメージ "mitsutaka/softether-vpnclient" が起動していたら終了する
'''
query = ['curl', '--unix-socket', '/var/run/docker.sock', 'http://localhost/containers/json']
with Popen(query, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
    proc.wait(timeout=8)
    reader = io.TextIOWrapper(proc.stdout) 
    rets = json.loads(reader.read())
    for ret in rets:
        if ret['Image'] == 'mitsutaka/softether-vpnclient' and \
                ret['State'] == 'running':
            Id = ret['Id']
            with Popen(['docker', 'kill', Id], stdout=PIPE, stdin=PIPE) as proc:
                proc.wait(timeout=8)
                reader2 = io.TextIOWrapper(proc.stdout)
                print(f'container id = {reader2.read().strip()} is kielld')

'''
docker container pruneする必要がある
NOTE. yesと入力してpruneする
NOTE. dockerのIFが書き込みを認めないのでbashの引数で実行
'''
with Popen(['bash', '-c', 'echo y | docker container prune'], stdout=PIPE, stdin=PIPE) as proc:
    reader = io.TextIOWrapper(proc.stdout) 
    proc.wait(timeout=8)
    print(reader.read().strip())

HOSTNAME = input('VPN ServerをインストールしたIPアドレスまたは、ホストを入力してください')
USERNAME = input('USERNAMEを指定してください:')
PASSWORD = input('PASSWORDを指定してください(PSKのパスワードではありません):')
TAP_IPADDR = input('IPアドレスとサブネットを指定してください\n e.g. (192.168.30.12/24):')

query = \
    ['docker',
     'run',
     '-d',
     '--name=softether-vpnclient',
     '-e', f'VPN_SERVER={HOSTNAME}', 
     '-e', 'VPN_PORT=5555',
     '-e', f'ACCOUNT_USER={USERNAME}',
     '-e', f'ACCOUNT_PASS={PASSWORD}',
     #'-e', 'TAP_IPADDR={TAP_IPADDR}',
     'mitsutaka/softether-vpnclient']
print(' '.join(query))
exit()
with Popen(query, stdout=PIPE, stdin=PIPE) as proc:
    proc.wait(timeout=60)
    reader = io.TextIOWrapper(proc.stdout)
    while True:
        r = reader.read(1)
        if not r:
            break
        print(r, end='', flush=True)

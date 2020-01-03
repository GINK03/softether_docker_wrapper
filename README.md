# 45秒でdockerでvpnサーバを建てる

## Q. 45秒で何ができる？
<div align="center">
  <img width="400px" src="https://www.dropbox.com/s/u189sd4oc6v7tbg/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-04%202.44.36.png?raw=1">
  <div> 参考 YouTubeのみなみチャンネル </div>
</div>

## A. 45秒でvpnサーバを建てられる

## 引っ越しのたびに光回線を引き直しているんだけど...
　転職やライフステージの変化に応じて、アパートなどの家を変えているのだが、その度にnuro光などのその時の最速のインターネットに乗り換えているのですが、多くは工事が必要でそのためのNTTの手続きが遅い...。nuro光はNTT網の空きネットワークであるダークファイバを利用しているので、必ず工事が必要で、工事の一部をNTTに依頼しているのですが、2019年11月に引っ越し依頼をして、2020年1月まだ工事が開通していません。  

　GCPやAWSなどの予算が溢れないようにネットワークディスクやローカルで済む簡単な計算などは現在でも一部は家のオンプレのサーバでやっています。単純に自分の機械を触っている時間を除くとオンプレはコストはクラウドに比べてそんなに高くないのとネットワークの実験が色々できて遊びと勉強が両立できて良いです。  

　この人手不足とワークライフバランスが重要視される世の中なので、NTTの人を責める事はありませんが、水や電気やガスといった生命に関係するインフラは当日開くのに、ネット用な一部の人間には十分生命に関係するインフラがこんなに遅いのか解せません。  

## NTTの工事が終わるまでどうやり過ごすか
  [softbank air](https://www.softbank.jp/ybb/air/)という旧PHSの電波網を利用した4G(に近い通信方式)でアクセスすることができます。  
  ちなみにこのデバイス、価格コムでボロクソに叩かれており、とにかく遅いです。WiMaxよりマシなところは、３日で10G制限がないことでしょうか。こんな制限されたら死んでしまう。  

  ~~この遅さを何とかする方法も今回の方法で解決できたりします。~~ ←高速にはなりませんでした
  
<div align="center">
  <img width="400px" src="https://www.dropbox.com/s/t6fnql3jv8qzhe8/%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89.jpeg?raw=1">
  <div> 図1. </div>
</div>

　この手の工事が必要ないモバイル回線を転用した高速通信の常として、グローバルIPアドレスが外部からどうやってもアクセス不能になるというデメリットがあります。  

  私の使い方だと安価な計算や大容量の高頻度アクセスが必要なディスクはオンプレ、めちゃ重い計算はGCPに降っているという都合があって、どうしても普段使いでは家のサーバにアクセスしたいというモチベーションがあります。  

  こんなときにどこかのクラウドサービスでインスタンスを借りて、そこでVPNサーバを立ち上げれば、どこからでも家のパソコンにアクセスすることができます。  
  
  ユースケースとしては趣味や仕事のデータ（個人でデータを取り扱って良い）をカフェや会社の休み時間などからアクセスして操作したり、膨大な処理だった場合、進捗を確認したりすることができます。 

<div align="center">
  <img width="600px" src="https://www.dropbox.com/s/ezgirb2530cktan/IMG_2326.jpeg?raw=1">
  <div> 図2. 家のPC、この計算力やディスクを遊ばせておくのは損失 </div>
</div>

## イメージするネットワーク図

<div align="center">
  <img width="600px" src="https://www.dropbox.com/s/3tc3clma0jnwkux/%E5%9B%B31.png?raw=1">
  <div> 図3. こんな使い方をしたい </div>
</div>
conohaのVPSの激弱激安インスタンス上にVPNサーバをデプロイすることで、そこ経由で家のPCにアクセスしたいです。  

## VPNサーバの設定は難しい & 苦痛
  どうにもインフラが職人芸化する要因にソフトウェアのチューニングや設定がとても狭い知識で成立していて、かなりわかりにくく、一度なんとかしても、もう二度目は使えなかったりするなど結構苦しいです。  

  「dockerで簡単にサーバの設定を含めてデプロイできたらなぁー」とか言っていたら、[そのもの](https://github.com/siomiz/SoftEtherVPN)が存在しました。

  英語なのと、いくつか情報が多すぎるので簡単化のため、wrapperスクリプトを書いたのでご紹介します。  

## コード
最近知ったのですが、Pythonのsubprocess.Popenはかなりきれいなshell scriptの上位互換的なコードを書くことができ、stdin, stdoutを自在にコントールできるので、Linux, Unix的なシステムと非常に相性がいいです。  

docker-composeでもいいのですが、インタラクティブにユーザ名、パスワードを設定したいので、以下のようなコードを書きました。  

```python
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
```

## 使い方

### LinuxにVPNサーバをdockerでインストールする
サーバはDockerインストール済みのconohaのUbuntu 18.04を想定しています。  
```console
$ wget -q https://raw.githubusercontent.com/GINK03/softether_docker_wrapper/master/run_softether_vpn_server_on_docker.py -O /tmp/vpn.py && python3 /tmp/vpn.py
USERNAMEを指定してください:hogehoge
PASSWORDを指定してください:1223334444
PSKのパスワードを指定してください:vpn
3f98a1d924124c5fb1abd119d151bc2c95cb3fb76bdbfd64804e6c5ba42949b9
```
45秒もかからない？

### Macをクライアントとする
<div align="center">
  <img width="500px" src="https://www.dropbox.com/s/5ycsox0x1d5950d/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-04%201.30.01.png?raw=1">
</div>
例えばMacでセットアップする場合、設定のネットワークから、+からVPN(L2TP)を選択し、USERNAMEをterminalで入力したものと同一のものを入力します。
<div align="center">
  <img width="500px" src="https://www.dropbox.com/s/5ycsox0x1d5950d/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202020-01-04%201.30.01.png?raw=1">
</div>
PASSWORDはパスワードに、PSKのパスワードはMacでは共有シークレットの部分になります。

## 結局、OSXやiOSやAndroidで使うにはL2TSが使えれば良い
softetherのclientをdockerにラップアップしてinstallしようと試みましたが、再現性が謎のエラーが多く、不安定すぎてやめました。L2TSが使えれば結局VPNに入れるので、特別に用意する必要は私のスキルでは労力に見合わないのさそうです。

## 操作感
出先のカフェから家のiMacにsshをしてみました。iMacはsoftbank airのネットワークの内側なので、本来ならばアクセスできないはずですが、VPNサーバで同一のネットワークにいることになるので、通信ができるようになりました。

IPアドレスもGMOのconohaのものになっています。
![anime](https://www.dropbox.com/s/4tcqdrcp6e0kjoa/ezgif-6-6b89fe6a2013.gif?raw=1)

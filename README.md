# prefix2as
インターネット上に流れているフルルートを用いて、 IP アドレスと AS 番号を相互変換する Web API システムです。  
自宅 Threat Intelligence プロジェクト「斥候」の一機能として、Threat Intelligence に活用するために作りました。

## 特徴
* RADBなど IRR を使わず実際に流れているフルルートを用いるので、より正確な実態を掴めます。
* Route Views Archive Project が提供するフルルートをインポートする仕組みを備えているので、自前でフルルートを用意できない人でも使えます。
* フルルートを自前で用意できる人のためにも、 quagga で 出力した MRT ファイルのインポートに対応しています。(strftime format 対応) 
* 外部 API を使わないので外部に調査対象情報が漏れず、BAN もされず、費用もかかりません。

## Demo
* IP アドレス指定時
```
http://localhost:8001/prefix2as/search?ip4=203.178.137.58

{
  "header": {
    "errorCode": 0, 
    "status": "success"
  }, 
  "response": [
    {
      "as": 2500, 
      "date": 1526299202, 
      "prefix": "203.178.128.0/17"
    }
  ]
}
```

* AS 番号指定時
```
http://localhost:8001/prefix2as/search?as=2500

{
  "header": {
    "errorCode": 0, 
    "status": "success"
  }, 
  "response": [
    {
      "as": 2500, 
      "date": 1526299201, 
      "prefix": "133.4.128.0/18"
    }, 
    {
      "as": 2500, 
      "date": 1526299201, 
      "prefix": "133.138.0.0/16"
    }, 
    {
      "as": 2500, 
      "date": 1526299201, 
      "prefix": "150.52.0.0/16"
    }, 
    {
      "as": 2500, 
      "date": 1526299201, 
      "prefix": "163.221.0.0/16"
    }, 
    {
      "as": 2500, 
      "date": 1526299202, 
      "prefix": "202.0.73.0/24"
    }, 
    {
      "as": 2500, 
      "date": 1526299202, 
      "prefix": "202.244.32.0/21"
    }, 
    {
      "as": 2500, 
      "date": 1526299202, 
      "prefix": "202.249.0.0/18"
    }, 
    {
      "as": 2500, 
      "date": 1526299202, 
      "prefix": "203.178.128.0/17"
    }
  ]
}
```

# Install

## 推奨環境
* Python 3.6 以上
* MySQL 5.6 以上


## libbgpdump のインストール
prefix2asのフルルートインポートには処理速度の関係上、libbgpdump の bgpdump コマンドを使っています。  
お使いのディストリビューションに合わせて libbgpdump をインストールしてください。

## ライブラリのインストール
```
pip install -r ./requirements.txt
```

## データベースの作成
* 好きな名前で作ってください。「sekkoh」とか。

## フルルートインポートツール「updateRouting」の設定
```
cd tools/updateRouting
cp updateRouting.conf.sample updateRouting.conf
vim updateRouting.conf
```
* dburl の値を利用するデータベースのURLに設定してください。
```
dburl = mysql+pymysql://user:password@127.0.0.1:3306/sekkoh?charset=utf8
```

※他にもインポートする世代数や、ローカル上の MRT ファイルを指定可能です。  
※詳細は updateRouting.conf を参照してください。 

## フルルートのインポート
updateRouting を使って Route Views Archive Project からフルルートをダウンロードし、データベースにインポートします。
```
./updateRouting.py -c ./updateRouting.conf
```

Route Views Archive Project のフルルートは2時間ごとに更新されるので、  
定期的に更新したい方は cron で 2時間おきに実行するようにすると良いでしょう。

## prefix2as の設定
```
cp prefix2as.conf.sample prefix2as.conf
vim prefix2as.conf
```
* updateRouting と同じように、DBURL の値を利用するデータベースのURLに設定してください。
```
DBURL = 'mysql+pymysql://user:password@127.0.0.1:3306/sekkoh?charset=utf8'
```

# Startup
```
cd bin
./app.py
```

起動後はデモのように色々試してみてください。

# Route Views Project について
Route Views Project (http://www.routeviews.org/) は University of Oregon Foundation を通じて寄付を募っています。  
Route Views Archive Project から定期的にフルルートを取得する方は寄付をご検討ください。  

http://www.routeviews.org/routeviews/index.php/about/  

# License
MIT License


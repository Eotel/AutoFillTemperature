# AutoFillTemperature
- 設定したアカウントで　Microsoft Forms に体温を入力する

## 使用方法
1. Python3 環境を準備する
    - `python3 --version` の出力が python3 以降になっていることを確認してください
    
2. 必要なパッケージをインストールします
    - `pip install -r requirements.txt`
    
3. Web Driver をインストールします
    - Homebrew 導入済みの場合
        - `brew install chromedriver`
    
    - 未導入の場合
        - 直接ダウンロードしてインストールします
        - [Downloads - ChromeDriver - WebDriver for Chrome](https://chromedriver.chromium.org/downloads)
        
    - ⚠️ ChromeDriver の使用には **Google Chrome** (web ブラウザ) が必要です

4. 設定ファイルを編集
    - settings.jsonを編集します
    
    ```yaml
    {
        "user": "Microsoft アカウントのユーザー名（学籍番号）",
        "domain": "Microsoft アカウントのドメイン（@マークより後ろの部分）",
        "password": "Microsoft アカウントのパスワード",
        "url": "Formsのurlを入力します",
        "morning_avg": 36.0,     # <- 朝の平均体温
        "evening_avg": 36.5,     # <- 夜の平均体温
        "deviation": 0.2,        # <- 標準偏差
        "temp_min": 35.6,        # <- 最低体温
        "temp_max": 37.3         # <- 最高体温（これらのコメント文は削除してください）
    }
    ```
    
5. 実行
    - `python3 main.py`
    - ⚠️ 動作中にキーを入力すると適切に動作しない可能性があります 
    - オプションの利用
   
   ```shell
   usage: main.py [-h] [-d DATE] [-t TIME]

   optional arguments:
     -h, --help            show this help message and exit
     -d DATE, --date DATE  Date to post, (e.g. "Today", "2020/01/12")
     -t TIME, --time TIME  Time to post, (e.g. "am", "pm", and "both")
   ```

## 環境

#### 動作確認済み
- MacBook Pro (13-inch, 2018, Four Thunderbolt 3 Ports)
- MacOS Catalina 10.15.7
- Python 3.9.0

## ⚠️ 注意
- このスクリプトは python による web スクレイピングの練習のために作成されました
- 体温の測定を誤魔化すために用いないでください
- 問題が生じた場合は責任は置いかねます

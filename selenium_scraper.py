from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_kaikatu_page():
    """Seleniumを使用して快活CLUBの店舗検索ページをスクレイピング"""

    # Chromeオプションの設定（WSL環境用に調整）
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # 新しいヘッドレスモード
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--remote-debugging-port=9222')  # WSL用にポート指定
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # WebDriverの初期化
    print("Chromiumドライバーを初期化中...")
    service = Service(ChromeDriverManager(chrome_type='chromium').install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # URLにアクセス
        url = "https://www.kaikatsu.jp/shop/result.html"
        print(f"アクセス中: {url}")
        driver.get(url)

        # ページの読み込みを待機（最大30秒）
        print("ページの読み込みを待機中...")
        wait = WebDriverWait(driver, 30)

        # 店舗ブロックが表示されるまで待機
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slo-block")))
            print("店舗情報が読み込まれました")
        except:
            print("警告: 店舗ブロックが見つかりませんでしたが、続行します")

        # 追加の待機時間（JavaScriptの実行完了を確実にするため）
        time.sleep(3)

        # ページソースを取得
        page_source = driver.page_source

        # HTMLファイルとして保存
        output_file = "kaikatu_search.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(page_source)

        print(f"HTMLを {output_file} に保存しました")
        print(f"ファイルサイズ: {len(page_source):,} バイト")

        return True

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

    finally:
        # ブラウザを閉じる
        driver.quit()
        print("ブラウザを終了しました")

if __name__ == "__main__":
    success = scrape_kaikatu_page()
    if success:
        print("\n処理が正常に完了しました")
    else:
        print("\n処理中にエラーが発生しました")
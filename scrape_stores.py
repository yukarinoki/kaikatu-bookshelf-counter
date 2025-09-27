from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

def extract_store_id(detail_url):
    """店舗詳細URLから店舗IDを抽出"""
    match = re.search(r'/(\d+)\.html', detail_url)
    if match:
        return match.group(1)
    return None

def scrape_local_html(file_path):
    """ローカルHTMLファイルから店舗情報をスクレイピング"""
    all_stores = []

    try:
        # ローカルHTMLファイルを読み込む
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # 都道府県グループごとに処理
        prefecture_groups = soup.find_all('div', class_='slo-group')

        for group in prefecture_groups:
            # 都道府県名を取得
            prefecture_elem = group.find('h2', class_='slo-head')
            prefecture = prefecture_elem.text.strip() if prefecture_elem else ''

            # グループ内の店舗ブロックを取得
            store_blocks = group.find_all('article', class_='slo-block')

            for block in store_blocks:
                store_info = {}

                # 都道府県を設定
                store_info['都道府県'] = prefecture

                # 店舗名
                title_elem = block.find('h3', class_='title')
                if title_elem:
                    store_info['店舗名'] = title_elem.text.strip()

                # 住所と電話番号
                for li in block.find_all('li', class_='flex'):
                    p_tags = li.find_all('p')
                    if len(p_tags) >= 2:
                        label = p_tags[0].text.strip()
                        value = p_tags[1].text.strip()

                        if '住所' in label:
                            # 改行やスペースを整理
                            store_info['住所'] = re.sub(r'\s+', ' ', value).strip()
                        elif '電話' in label:
                            store_info['電話番号'] = value

                # 店舗詳細URL
                detail_link = block.find('a', href=re.compile(r'/shop/detail/\d+\.html'))
                if detail_link:
                    detail_url = detail_link.get('href')
                    store_info['店舗URL'] = urljoin('https://www.kaikatsu.jp', detail_url)
                    store_info['店舗ID'] = extract_store_id(detail_url)

                if store_info.get('店舗ID'):
                    all_stores.append(store_info)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return all_stores

def main():
    html_file = "kaikatu_search.html"

    print(f"{html_file} からスクレイピング中...")

    # ローカルHTMLファイルからスクレイピング
    all_stores = scrape_local_html(html_file)

    # 重複を除去（店舗IDで判定）
    unique_stores = {}
    for store in all_stores:
        store_id = store.get('店舗ID')
        if store_id and store_id not in unique_stores:
            unique_stores[store_id] = store

    # 都道府県別に集計
    prefecture_count = {}
    for store in unique_stores.values():
        prefecture = store.get('都道府県', '不明')
        prefecture_count[prefecture] = prefecture_count.get(prefecture, 0) + 1

    # 結果を整形
    result = {
        '店舗数': len(unique_stores),
        '都道府県別店舗数': prefecture_count,
        '店舗情報': list(unique_stores.values())
    }

    # JSONファイルに保存
    with open('stores.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n完了！ {len(unique_stores)}店舗の情報を stores.json に保存しました。")

    # 都道府県別の店舗数を表示
    print("\n都道府県別店舗数:")
    for prefecture, count in sorted(prefecture_count.items()):
        print(f"  {prefecture}: {count}店舗")

    # 最初の5店舗を表示
    print("\n最初の5店舗:")
    for store in list(unique_stores.values())[:5]:
        print(f"  ID: {store['店舗ID']}, 店舗名: {store['店舗名']}, 都道府県: {store['都道府県']}")

if __name__ == "__main__":
    main()

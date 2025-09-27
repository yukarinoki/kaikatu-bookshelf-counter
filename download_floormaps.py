import json
import requests
import os
import time
from pathlib import Path

def download_floormap(store_id, output_dir):
    """店舗IDからフロアマップ画像をダウンロード"""
    url = f"https://www.navi-comi.com/shop_data/{store_id}/images/floormap.gif"
    output_path = output_dir / f"{store_id}.gif"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"  店舗ID {store_id}: 画像が見つかりません (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"  店舗ID {store_id}: ダウンロードエラー ({e})")
        return False

def main():
    # JSONファイルを読み込み
    try:
        with open('stores.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("エラー: stores.json が見つかりません。")
        print("まず 1_scrape_stores.py を実行してください。")
        return
    
    # floormapフォルダを作成
    output_dir = Path('floormap')
    output_dir.mkdir(exist_ok=True)
    
    stores = data.get('店舗情報', [])
    total_stores = len(stores)
    success_count = 0
    failed_stores = []
    
    print(f"{total_stores}店舗のフロアマップをダウンロードします...")
    
    for i, store in enumerate(stores, 1):
        store_id = store.get('店舗ID')
        store_name = store.get('店舗名', '不明')
        
        if not store_id:
            print(f"[{i}/{total_stores}] スキップ: 店舗IDが見つかりません")
            continue
        
        print(f"[{i}/{total_stores}] 店舗ID: {store_id} ({store_name})")
        
        if download_floormap(store_id, output_dir):
            success_count += 1
            print(f"  ✓ ダウンロード成功")
        else:
            failed_stores.append({'店舗ID': store_id, '店舗名': store_name})
        
        # サーバーへの負荷を軽減するため少し待機
        time.sleep(0.5)
    
    # 結果サマリー
    print(f"\n========== ダウンロード完了 ==========")
    print(f"成功: {success_count}/{total_stores} 店舗")
    print(f"失敗: {len(failed_stores)} 店舗")
    
    if failed_stores:
        print("\nダウンロードできなかった店舗:")
        for store in failed_stores[:10]:  # 最初の10店舗のみ表示
            print(f"  - ID: {store['店舗ID']}, 店舗名: {store['店舗名']}")
        if len(failed_stores) > 10:
            print(f"  ... 他 {len(failed_stores) - 10} 店舗")
    
    # ダウンロード結果を保存
    result = {
        '総店舗数': total_stores,
        'ダウンロード成功数': success_count,
        'ダウンロード失敗数': len(failed_stores),
        '失敗した店舗': failed_stores
    }
    
    with open('download_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nダウンロード結果を download_result.json に保存しました。")

if __name__ == "__main__":
    main()

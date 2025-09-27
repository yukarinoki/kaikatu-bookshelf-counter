#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""スクリプトのテスト（最初の5件のみ処理）"""

import json
import csv
import os
from pathlib import Path
from enhanced_ocr_counter import EnhancedOCRCounter

def load_store_info():
    """stores.jsonから店舗情報を読み込み"""
    with open('stores.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 店舗IDをキーとした辞書を作成
    store_dict = {}
    for store in data['店舗情報']:
        store_dict[store['店舗ID']] = store['店舗名']

    return store_dict

def test_count():
    """テスト実行（最初の5件のみ）"""
    # 店舗情報を読み込み
    store_info = load_store_info()
    print(f"店舗情報を読み込みました: {len(store_info)}店舗\n")

    # floormapディレクトリ内の全GIFファイルを取得（最初の5件のみ）
    floormap_dir = Path("floormap")
    gif_files = sorted(floormap_dir.glob("*.gif"))
    total_files = len(gif_files)
    print(f"テスト処理対象: {total_files}ファイル\n")

    # CSVファイル名（テスト用）
    csv_filename = "shelf_counts.csv"

    # カウンターを初期化
    print("EasyOCR初期化中...")
    counter = EnhancedOCRCounter()
    print("初期化完了\n")

    print("-" * 60)

    # CSVファイルを新規作成
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['店舗ID', '店舗名', '棚数'])

    # 各画像を処理
    for idx, gif_path in enumerate(gif_files, 1):
        # ファイル名から店舗IDを取得
        store_id = gif_path.stem  # .gifを除いたファイル名

        # 店舗名を取得（見つからない場合は "不明" とする）
        store_name = store_info.get(store_id, "不明")

        print(f"[{idx:3}/{total_files}] 店舗ID: {store_id}", end="")

        try:
            # 棚数をカウント
            shelf_count, method = counter.count_shelves(str(gif_path), debug=False)

            print(f" → 棚数: {shelf_count:3} ({method}) - {store_name}")

            # CSVに追記
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([store_id, store_name, shelf_count])

        except Exception as e:
            print(f" → エラー: {str(e)}")

    print("-" * 60)
    print(f"\nテスト完了。結果は {csv_filename} に保存されました")

if __name__ == "__main__":
    test_count()

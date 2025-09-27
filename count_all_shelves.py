#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全店舗の棚数をカウントしてCSVに保存するスクリプト"""

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

def count_all_stores():
    """全店舗の棚数をカウント"""
    print("=" * 60)
    print("全店舗棚数カウント開始")
    print("=" * 60)

    # 店舗情報を読み込み
    store_info = load_store_info()
    print(f"店舗情報を読み込みました: {len(store_info)}店舗\n")

    # floormapディレクトリ内の全GIFファイルを取得
    floormap_dir = Path("floormap")
    gif_files = sorted(floormap_dir.glob("*.gif"))
    total_files = len(gif_files)
    print(f"処理対象画像: {total_files}ファイル\n")

    # CSVファイル名
    csv_filename = "shelf_counts.csv"

    # CSVファイルが存在しない場合はヘッダーを書き込み
    file_exists = os.path.exists(csv_filename)

    # カウンターを初期化
    print("EasyOCR初期化中...")
    counter = EnhancedOCRCounter()
    print("初期化完了\n")

    print("-" * 60)

    # 処理済み件数
    processed = 0
    error_count = 0

    # csvファイルを開き、すでに処理済みの店舗IDを取得
    processed_store_ids = set()
    if file_exists:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ヘッダーをスキップ
            for row in reader:
                if row:
                    processed_store_ids.add(row[0])  # 店舗IDは1列目


    # 各画像を処理
    for idx, gif_path in enumerate(gif_files, 1):
        # ファイル名から店舗IDを取得
        store_id = gif_path.stem  # .gifを除いたファイル名
        if store_id in processed_store_ids:
            print(f"[{idx:3}/{total_files}] 店舗ID: {store_id} は既に処理済み、スキップします")
            continue

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

                # ヘッダーを書き込み（初回のみ）
                if not file_exists and idx == 1:
                    writer.writerow(['店舗ID', '店舗名', '棚数'])

                # データを書き込み
                writer.writerow([store_id, store_name, shelf_count])

            processed += 1

        except Exception as e:
            print(f" → エラー: {str(e)}")
            error_count += 1

            # エラーの場合も記録（棚数を-1として）
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists and idx == 1:
                    writer.writerow(['店舗ID', '店舗名', '棚数'])
                writer.writerow([store_id, store_name, -1])

    print("-" * 60)
    print("\n処理完了")
    print(f"  処理済み: {processed}件")
    print(f"  エラー: {error_count}件")
    print(f"  結果は {csv_filename} に保存されました")

if __name__ == "__main__":
    count_all_stores()

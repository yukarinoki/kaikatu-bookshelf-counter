#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全19店舗に対する改良版OCRカウンターのテスト"""

import json
import time
from pathlib import Path
from enhanced_ocr_counter import EnhancedOCRCounter

def run_comprehensive_test():
    """全店舗テストを実行"""
    print("=" * 80)
    print("改良版OCRカウンター 全店舗テスト")
    print("=" * 80)

    # 手動カウントを読み込み
    with open('manual_count.json', 'r') as f:
        manual_data = json.load(f)

    manual_counts = {}
    for item in manual_data:
        manual_counts.update(item)

    # カウンターを初期化
    print("\nEasyOCR初期化中...")
    counter = EnhancedOCRCounter()
    print("初期化完了\n")

    # 結果を格納
    results = []
    total_stores = len(manual_counts)
    perfect_matches = 0
    within_5_percent = 0
    within_10_percent = 0

    # 各店舗をテスト
    for idx, (store_id, manual_count) in enumerate(manual_counts.items(), 1):
        image_path = f"floormap/{store_id}.gif"

        if not Path(image_path).exists():
            print(f"[{idx:2}/{total_stores}] 店舗 {store_id}: 画像ファイルが見つかりません")
            continue

        print(f"[{idx:2}/{total_stores}] 店舗 {store_id} (手動: {manual_count}):")

        # カウント実行
        auto_count, method = counter.count_shelves(image_path, debug=False)

        # 精度計算
        diff = auto_count - manual_count
        accuracy = 100 - (abs(diff) / manual_count * 100) if manual_count > 0 else 0

        # 統計更新
        if diff == 0:
            perfect_matches += 1
            status = "✓ 完全一致"
        elif accuracy >= 95:
            within_5_percent += 1
            status = "○ 5%以内"
        elif accuracy >= 90:
            within_10_percent += 1
            status = "△ 10%以内"
        else:
            status = "× 10%超"

        print(f"    自動: {auto_count:3} ({method})")
        print(f"    差分: {diff:+3}, 精度: {accuracy:6.2f}% {status}")

        # 結果を保存
        results.append({
            "店舗ID": store_id,
            "手動カウント": manual_count,
            "自動カウント": auto_count,
            "検出方法": method,
            "差分": diff,
            "精度": round(accuracy, 2),
            "ステータス": status
        })

    # サマリー表示
    print("\n" + "=" * 80)
    print("テスト結果サマリー")
    print("=" * 80)

    # 精度別分類
    excellent = [r for r in results if r["精度"] >= 95]
    good = [r for r in results if 90 <= r["精度"] < 95]
    fair = [r for r in results if 80 <= r["精度"] < 90]
    poor = [r for r in results if r["精度"] < 80]

    print(f"\n完全一致 (100%): {perfect_matches}/{total_stores} 店舗")
    if perfect_matches > 0:
        for r in results:
            if r["差分"] == 0:
                print(f"  - {r['店舗ID']}: {r['手動カウント']}")

    print(f"\n優秀 (95-100%): {len(excellent)}/{total_stores} 店舗")
    if excellent:
        for r in excellent:
            if r["差分"] != 0:  # 完全一致以外
                print(f"  - {r['店舗ID']}: 手動={r['手動カウント']}, 自動={r['自動カウント']} ({r['精度']:.1f}%)")

    print(f"\n良好 (90-95%): {len(good)}/{total_stores} 店舗")
    if good:
        for r in good:
            print(f"  - {r['店舗ID']}: 手動={r['手動カウント']}, 自動={r['自動カウント']} ({r['精度']:.1f}%)")

    print(f"\n要改善 (80-90%): {len(fair)}/{total_stores} 店舗")
    if fair:
        for r in fair:
            print(f"  - {r['店舗ID']}: 手動={r['手動カウント']}, 自動={r['自動カウント']} ({r['精度']:.1f}%)")

    print(f"\n要注意 (<80%): {len(poor)}/{total_stores} 店舗")
    if poor:
        for r in poor:
            print(f"  - {r['店舗ID']}: 手動={r['手動カウント']}, 自動={r['自動カウント']} ({r['精度']:.1f}%)")

    # 全体統計
    avg_accuracy = sum(r["精度"] for r in results) / len(results) if results else 0

    print("\n" + "=" * 80)
    print("全体統計")
    print("=" * 80)
    print(f"平均精度: {avg_accuracy:.2f}%")
    print(f"90%以上: {len(excellent) + len(good)}/{total_stores} 店舗 ({(len(excellent) + len(good))/total_stores*100:.1f}%)")
    print(f"完全一致率: {perfect_matches/total_stores*100:.1f}%")

    # 検出方法別統計
    method_counts = {}
    for r in results:
        method = r["検出方法"]
        if method not in method_counts:
            method_counts[method] = {"count": 0, "accuracy_sum": 0}
        method_counts[method]["count"] += 1
        method_counts[method]["accuracy_sum"] += r["精度"]

    print("\n検出方法別統計:")
    for method, stats in method_counts.items():
        avg_acc = stats["accuracy_sum"] / stats["count"]
        print(f"  {method}: {stats['count']}件, 平均精度 {avg_acc:.1f}%")

    # 結果をJSONファイルに保存
    test_result = {
        "テスト日時": str(time.time()),
        "テスト店舗数": total_stores,
        "完全一致数": perfect_matches,
        "平均精度": round(avg_accuracy, 2),
        "精度90%以上": len(excellent) + len(good),
        "詳細結果": results
    }

    with open('comprehensive_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(test_result, f, ensure_ascii=False, indent=2)

    print("\n結果をcomprehensive_test_result.jsonに保存しました。")

    # 改善前との比較（参考値）
    print("\n" + "=" * 80)
    print("改善前後の比較（参考）")
    print("=" * 80)
    print("改善前: 平均精度 18.1% (OCR最大値のみ)")
    print(f"改善後: 平均精度 {avg_accuracy:.1f}% (連続グループ分析+外れ値除外)")
    print(f"改善率: +{avg_accuracy - 18.1:.1f}%")

if __name__ == "__main__":
    run_comprehensive_test()
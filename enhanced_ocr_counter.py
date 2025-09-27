import json
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import easyocr
import pytesseract
import re

class EnhancedOCRCounter:
    def __init__(self):
        """EasyOCRリーダーを初期化"""
        self.reader = easyocr.Reader(['en'], gpu=False)  # GPUがない場合はFalse

    def preprocess_image(self, image, scale_factor=2):
        """画像の前処理を強化"""
        # スケールアップ
        if scale_factor > 1:
            height, width = image.shape[:2]
            new_size = (int(width * scale_factor), int(height * scale_factor))
            image = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)

        # ノイズ除去
        image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 15)

        # グレースケール変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # コントラスト強調 (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        return gray, image

    def extract_numbers_easyocr(self, image_path):
        """EasyOCRで数字を抽出"""
        try:
            # 画像を読み込み
            pil_img = Image.open(image_path).convert('RGB')
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

            # 前処理
            gray, processed = self.preprocess_image(img, scale_factor=2)

            # EasyOCRで読み取り（グレースケール画像を使用）
            results = self.reader.readtext(gray, allowlist='0123456789')

            # 数字を抽出
            numbers = []
            for (bbox, text, prob) in results:
                # 信頼度が0.3以上の結果のみ
                if prob > 0.3 and text.isdigit():
                    num = int(text)
                    if 0 < num <= 100:
                        numbers.append(num)

            return numbers

        except Exception as e:
            print(f"EasyOCRエラー: {e}")
            return []

    def extract_numbers_region_based(self, image_path):
        """色領域ごとにEasyOCRを適用"""
        try:
            pil_img = Image.open(image_path).convert('RGB')
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            all_numbers = []

            # 色範囲の定義
            color_ranges = [
                {'lower': np.array([75, 15, 15]), 'upper': np.array([140, 255, 255]), 'name': '青系'},
                {'lower': np.array([140, 15, 15]), 'upper': np.array([175, 255, 255]), 'name': 'ピンク'},
                {'lower': np.array([0, 30, 30]), 'upper': np.array([95, 255, 255]), 'name': '緑系（拡張）'},
                {'lower': np.array([15, 15, 15]), 'upper': np.array([35, 255, 255]), 'name': '黄橙'},
            ]

            for color_range in color_ranges:
                # 色マスクを作成
                mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])

                # ノイズ除去
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

                # 輪郭検出
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area < 100:
                        continue

                    x, y, w, h = cv2.boundingRect(contour)

                    # 矩形領域を切り出し
                    roi = img[y:y+h, x:x+w]

                    # ROIを拡大
                    if w < 50 or h < 50:
                        scale = 3
                        roi = cv2.resize(roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

                    # EasyOCRで読み取り
                    try:
                        results = self.reader.readtext(roi, allowlist='0123456789')
                        for (bbox, text, prob) in results:
                            if prob > 0.3 and text.isdigit():
                                num = int(text)
                                if 0 < num <= 100:
                                    all_numbers.append(num)
                    except:
                        continue

            return all_numbers

        except Exception as e:
            print(f"領域ベースOCRエラー: {e}")
            return []

    def extract_all_visible_numbers(self, image_path):
        """マスクを使わず直接全体をスキャン（通常と反転の2パターン）"""
        try:
            all_numbers = []

            # パターン1: 通常の画像でEasyOCR実行
            results = self.reader.readtext(image_path, allowlist='0123456789')
            for (bbox, text, prob) in results:
                if prob > 0.3 and text.isdigit():
                    num = int(text)
                    if 0 < num <= 100:
                        all_numbers.append(num)

            # パターン2: 色反転画像でEasyOCR実行
            pil_img = Image.open(image_path).convert('RGB')
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            inverted = cv2.bitwise_not(gray)

            results = self.reader.readtext(inverted, allowlist='0123456789')
            for (bbox, text, prob) in results:
                if prob > 0.3 and text.isdigit():
                    num = int(text)
                    if 0 < num <= 100:
                        all_numbers.append(num)

            return list(set(all_numbers))  # 重複除去

        except Exception as e:
            print(f"全体スキャンエラー: {e}")
            return []

    def hybrid_ocr(self, image_path):
        """複数のOCR手法を組み合わせ"""
        numbers_easyocr = self.extract_numbers_easyocr(image_path)
        numbers_region = self.extract_numbers_region_based(image_path)
        numbers_all = self.extract_all_visible_numbers(image_path)

        # Tesseractも併用
        numbers_tesseract = []
        try:
            pil_img = Image.open(image_path).convert('RGB')
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 複数の閾値でテスト
            for threshold in [200, 210, 220]:
                _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
                config = '--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
                text = pytesseract.image_to_string(binary, config=config)
                for n in re.findall(r'\d+', text):
                    if n.isdigit():
                        num = int(n)
                        if 0 < num <= 100:
                            numbers_tesseract.append(num)
        except:
            pass

        # すべての結果を統合
        all_numbers = list(set(numbers_easyocr + numbers_region + numbers_all + numbers_tesseract))

        return all_numbers

    def analyze_continuous_groups(self, numbers):
        """連続する数字グループを分析して最も信頼できる値を返す"""
        if not numbers:
            return 0, []

        sorted_nums = sorted(numbers)
        groups = []
        current_group = [sorted_nums[0]]

        # 連続グループを検出
        for i in range(1, len(sorted_nums)):
            if sorted_nums[i] == current_group[-1] + 1:
                # 連続している
                current_group.append(sorted_nums[i])
            else:
                # 連続が切れた
                if len(current_group) >= 3:  # 3個以上のグループのみ
                    groups.append(current_group)
                current_group = [sorted_nums[i]]

        # 最後のグループ
        if len(current_group) >= 3:
            groups.append(current_group)

        # 最も信頼できる値を決定
        if groups:
            # 各グループの最大値
            max_values = max([max(g) for g in groups])
            return max_values, groups
        return 0, []

    def is_outlier(self, number, continuous_max):
        """外れ値かどうかを判定"""
        # 連続最大値から大きく離れているかチェック
        gap = number - continuous_max
        return gap > 10  # 10以上離れている場合は外れ値

    def calculate_coverage_to_continuous(self, detected_numbers, continuous_max):
        """連続最大値までのカバレッジを計算"""
        if continuous_max == 0:
            return 0

        expected = set(range(1, continuous_max + 1))
        detected = set(n for n in detected_numbers if n <= continuous_max)
        return len(detected & expected) / len(expected) if expected else 0

    def count_shelves(self, image_path, debug=False):
        """棚数をカウント（メインメソッド）"""
        # ハイブリッドOCRで数字を検出
        detected_numbers = self.hybrid_ocr(image_path)

        if debug:
            print(f"  検出された数字: {sorted(detected_numbers)}")

        if detected_numbers:
            # 連続グループ分析
            continuous_max, groups = self.analyze_continuous_groups(detected_numbers)

            # 全体の最大値
            max_number = max(detected_numbers)

            # 旧カバレッジ計算（参考用）
            expected_range = set(range(1, max_number + 1))
            detected_set = set(detected_numbers)
            coverage = len(detected_set & expected_range) / len(expected_range) if expected_range else 0

            if debug:
                print(f"  最大値: {max_number}, カバレッジ: {coverage:.2f}")
                if groups:
                    print(f"  連続グループ: {len(groups)}個検出")
                    for g in groups[:3]:  # 最初の3グループを表示
                        print(f"    {min(g)}-{max(g)} ({len(g)}個)")
                    print(f"  連続グループ最大値: {continuous_max}")

            # 改良版判定ロジック
            if continuous_max > 0:
                # 最大値が外れ値かチェック
                if self.is_outlier(max_number, continuous_max):
                    # 外れ値なので連続最大値を使用
                    if debug:
                        print(f"  {max_number}は外れ値として除外")
                    return continuous_max, 'EasyOCR連続最大（外れ値除外）'

                # 連続最大値までのカバレッジを計算
                continuous_coverage = self.calculate_coverage_to_continuous(detected_numbers, continuous_max)

                if debug:
                    print(f"  連続カバレッジ: {continuous_coverage:.2f}")

                # 連続最大値までのカバレッジが高い場合
                if continuous_coverage > 0.8:
                    return continuous_max, 'EasyOCR連続最大'
                else:
                    # カバレッジが低い場合も連続最大値を信頼
                    return continuous_max, 'EasyOCR連続最大'

            # 連続グループがない場合
            if coverage > 0.4 and max_number <= 1000:
                return max_number, 'EasyOCR最大値'
            else:
                # 異常に大きい値を除外
                reasonable_nums = [n for n in detected_numbers if n <= 1000]
                if reasonable_nums:
                    return max(reasonable_nums), 'EasyOCR補正最大'
                else:
                    return len(detected_numbers), 'EasyOCR検出数'

        return 0, '検出なし'

def test_enhanced_ocr():
    """拡張OCRカウンターのテスト"""
    print("拡張OCRカウンターテスト")
    print("=" * 60)

    # 手動カウントを読み込み
    with open('manual_count.json', 'r') as f:
        manual_data = json.load(f)

    manual_counts = {}
    for item in manual_data:
        manual_counts.update(item)

    # 問題のある店舗を優先的にテスト
    test_stores = ['20928']

    counter = EnhancedOCRCounter()

    print("EasyOCR初期化完了")
    print()

    for store_id in test_stores:
        if store_id not in manual_counts:
            continue

        manual_count = manual_counts[store_id]
        image_path = f"floormap/{store_id}.gif"

        if not Path(image_path).exists():
            continue

        print(f"店舗 {store_id} (手動: {manual_count}):")
        auto_count, method = counter.count_shelves(image_path, debug=True)

        diff = auto_count - manual_count
        accuracy = 100 - (abs(diff) / manual_count * 100) if manual_count > 0 else 0

        print(f"  結果: {auto_count} ({method})")
        print(f"  差分: {diff:+3d}, 精度: {accuracy:.1f}%")
        print()

if __name__ == "__main__":
    test_enhanced_ocr()

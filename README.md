# 快活空間 漫画棚数調査プロジェクト

快活空間の全国 500 店舗における漫画棚数を自動的にカウントするシステムです。
店舗フロアマップ画像を OCR 技術で解析し、各店舗の漫画規模を定量的に把握します。

## 📊 プロジェクト概要

### 目的

快活空間の店舗ごとの漫画コレクション規模を調査し、各店舗の漫画蔵書数を推定するデータを収集します。

### 調査結果サマリー

**部分的に誤差がある、この情報の活用は自分の責任で**

- **総店舗数**: 500 店舗
- **解析成功**: 497 店舗
- **非対応店舗**: 3 店舗（コミック検索機能非対応）
  - 新宿駅東口店 (ID: 20918)
  - 梅田太融寺店 (ID: 20917)
  - 熊本新市街店 (ID: 20987)

## 🔧 システム構成

### 処理フロー

1. **HTML ダウンロード**: 快活空間の店舗検索ページを取得
2. **スクレイピング**: BeautifulSoup で店舗情報（店舗 ID、名称、住所等）を抽出
3. **画像ダウンロード**: 各店舗のフロアマップ画像（GIF 形式）を一括取得
4. **OCR 解析**: EasyOCR で画像内の棚番号を検出し、最大値から棚数をカウント

### 技術スタック

- **Python 3.x**
- **BeautifulSoup4**: HTML パーシング
- **EasyOCR**: 光学文字認識
- **OpenCV**: 画像処理
- **Requests**: HTTP 通信
- **Selenium**: 動的コンテンツ取得（オプション）

## 📁 ファイル構成

```
kaikatu_bookshelf_counter/
├── kaikatu_search.html        # 快活空間店舗検索ページのHTML
├── scrape_stores.py           # HTMLから店舗情報を抽出
├── stores.json                # 抽出した店舗情報（500店舗）
├── download_floormaps.py      # フロアマップ画像ダウンロードスクリプト
├── floormap/                  # ダウンロードした画像ディレクトリ
│   └── [店舗ID].gif          # 各店舗のフロアマップ画像
├── enhanced_ocr_counter.py    # OCR解析エンジン
├── count_all_shelves.py       # 全店舗一括解析スクリプト
├── shelf_counts.csv           # 解析結果CSV
├── download_result.json       # ダウンロード結果サマリー
└── requirements.txt           # 依存パッケージ一覧
```

## 🚀 実行方法

### 環境構築

```bash
# リポジトリのクローン
git clone https://github.com/yukarinoki/kaikatu-bookshelf-counter.git
cd kaikatu-bookshelf-counter

# 依存パッケージのインストール
pip install -r requirements.txt
```

### ステップバイステップ実行

#### 1. HTML ファイルの取得

快活空間の[店舗検索ページ](https://www.kaikatsu.jp/search)から検索結果 HTML を保存し、`kaikatu_search.html`として配置します。

#### 2. 店舗情報の抽出

```bash
python scrape_stores.py
```

`stores.json`に 500 店舗の情報が保存されます。

#### 3. フロアマップ画像のダウンロード

```bash
python download_floormaps.py
```

`floormap/`ディレクトリに各店舗の画像が保存されます。

#### 4. 棚数カウント実行

```bash
python count_all_shelves.py
```

`shelf_counts.csv`に解析結果が出力されます。

## 📈 データ形式

### stores.json

```json
{
  "店舗情報": [
    {
      "店舗ID": "20001",
      "店舗名": "○○店",
      "都道府県": "東京都",
      "住所": "東京都○○区...",
      "電話番号": "03-xxxx-xxxx",
      "店舗詳細URL": "https://..."
    }
  ]
}
```

### shelf_counts.csv

```csv
店舗ID,店舗名,棚数
20001,○○店,45
20002,△△店,32
...
```

## 📊 解析精度について

- OCR による自動カウントのため、実際の棚数と誤差が生じる
- より正確な調査には手動確認を推奨

## 📝 注意事項

- 本プロジェクトは研究・調査目的です、信頼できるデータでもないです。
- 快活空間公式のデータではありません
- サーバー負荷を考慮し、適切な間隔でアクセスしてください
- 3 店舗（新宿駅東口店、梅田太融寺店、熊本新市街店）はコミック検索機能非対応のためデータ取得不可

## 📄 ライセンス

MIT License

## 🤝 コントリビューション

Issue・PR は歓迎します。改善案やバグ報告は GitHub Issues までお願いします。

## 📧 連絡先

GitHub: [@yukarinoki](https://github.com/yukarinoki)

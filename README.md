# png-pfm-converter

PNG と PFM (Portable Float Map) を相互変換するツールです。

## インストール

```bash
uv sync
```

## 使い方

### コマンドライン

```bash
# PNG → PFM
uv run png2pfm input.png output.pfm

# PFM → PNG
uv run pfm2png input.pfm output.png
```

### Python API

```python
from png_pfm_converter import png_to_pfm, pfm_to_png

png_to_pfm("input.png", "output.pfm")
pfm_to_png("input.pfm", "output.png")
```

## 変換仕様

| 方向 | 処理 |
|------|------|
| PNG → PFM | 画素値を 0–255 から 0.0–1.0 に正規化して保存 |
| PFM → PNG | 0.0–1.0 の値を 0–255 にスケール、範囲外はクランプ |

- RGB・グレースケール両対応（`PF` / `Pf` タグ）
- PFM はリトルエンディアンで出力
- PNG の RGBA はアルファチャンネルを落として RGB に変換

## テスト

```bash
uv run pytest
```

## PFM フォーマット

```
PF          # PF = RGB, Pf = グレースケール
幅 高さ
スケール値  # 負 = リトルエンディアン
[float32 データ, 行は下から上の順]
```

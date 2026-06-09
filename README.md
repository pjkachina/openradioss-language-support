# DeckLens: Semantic Diff for CAE

![VS Code Extension](https://img.shields.io/badge/extension-VS%20Code-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**DeckLens** は CAE（計算力学）入力ファイルの**セマンティックdiff**ツールです。テキスト差分ではなく、エンジニアリング観点から「何が変わった」かを理解します。

## 問題

CAE検証チームの現状：
- 型紙（テンプレート）から修正内容を手動確認 → ボトルネック
- `grep` + テキストエディタで変更追跡 → ミスが多い
- 厚さ変更は単なる％数値表示 → 剛性への影響が不明確
- 境界条件削除が見落とされやすい

## ソリューション

```bash
$ decklens diff before.rad after.rad

─────────── DeckLens Semantic Diff ──────────
  Before: before.rad
  After:  after.rad

┌─ Summary ─┐
│ 2 CRITICAL, 4 WARNING │
└────────────┘

┌────────┬─────────┬────────────┬─────────────────────┐
│ Sev    │ Type    │ Name       │ Field               │
├────────┼─────────┼────────────┼─────────────────────┤
│ [CRIT] │ PROP/SH │ OUTER_PNL  │ thickness           │
│        │         │            │ (bend-stiffness     │
│        │         │            │ +138%)              │
│ [CRIT] │ CLOAD   │ FORCE_Z    │ Fscale_y: 1000→2000│
│ [WARN] │ MAT/ELS │ STEEL      │ E: 210k→206k (-1.9%)
│ [WARN] │ BCS     │ FIXED_SUP  │ RX: free→fixed      │
└────────┴─────────┴────────────┴─────────────────────┘

🤖 AI Engineering Analysis (Claude Opus 4.8)
─────────────────────────────────────────
曲げ剛性が +138% 増加（t³則）するため、座屈荷重が大幅に上昇。
ただし Young の係数が -1.9% 低下しているため、相殺効果は限定的。
回転拘束追加により、モーメント反力が発生可能性あり。
負荷 2 倍は FOS に直結 — 応力状態の再確認推奨。
```

### 主な機能

✅ **OpenRadioss パーサー**
- `/PROP/SHELL`, `/MAT/ELAST`, `/MAT/PLAS_JOHNS`, `/PART`, `/BCS`, `/LOAD`, `/INTER` 対応
- FORTRAN D-notation（`7.85D-9`）自動変換

✅ **セマンティック差分エンジン**
- 厚さ変更 → 曲げ剛性（EI ∝ t³）を自動計算・注釈
- Young係数 → 剛性への影響を評価
- 境界条件追加/削除 → 重大度を自動判定
- 負荷 2 倍 → CRITICAL フラグ

✅ **重大度自動判定**
| 重大度 | 条件 |
|--------|------|
| CRITICAL | ≥20% 変化、または BC/PART 削除 |
| WARNING | 5–20% 変化、または BC 追加 |
| INFO | <5% 変化 |

✅ **Claude AI 分析（オプション）**
- `claude-opus-4-8` による自動解釈
- 適応思考（adaptive thinking）で複雑な物理関係を推論
- JSON 出力対応（CI/CD 統合）

## インストール

### PyPI（CLI ツール）

```bash
pip install decklens-semantic-diff
```

### VS Code 拡張機能

1. VS Code Marketplace で「DeckLens」検索
2. インストール
3. `.env` に `ANTHROPIC_API_KEY` 設定（AI 分析有効化）

## 使い方

### CLI

```bash
# 基本的な diff
decklens diff before.rad after.rad

# AI 分析をスキップ
decklens diff before.rad after.rad --no-ai

# JSON 出力（CI/CD 連携）
decklens diff before.rad after.rad --format json

# 重大度フィルタ
decklens diff before.rad after.rad --min-severity WARNING

# 別の Claude モデル指定
decklens diff before.rad after.rad --model claude-sonnet-4-6
```

### VS Code 拡張機能

右クリック → **DeckLens: Compare with** → ファイル選択 → サイドパネルに結果表示

## 対応フォーマット

| フォーマット | サポート | ロードマップ |
|------------|---------|-----------|
| OpenRadioss (.rad) | ✅ | 本実装 |
| NASTRAN (.bdf) | 🔜 | Q3 2026 |
| LS-DYNA (.k) | 🔜 | Q3 2026 |

## 技術仕様

- **言語**: Python 3.11+（CLI）、TypeScript（VS Code 拡張）
- **API**: Claude Opus 4.8、adaptive thinking、high effort
- **出力**: Rich テーブル、Markdown、JSON
- **ライセンス**: MIT

## 必要な環境

- Python 3.11+
- VS Code 1.85+（拡張機能使用時）
- ANTHROPIC_API_KEY（AI 分析機能使用時）

## トラブルシューティング

### Q: AI 分析が実行されない
**A**: `.env` に `ANTHROPIC_API_KEY` が設定されているか確認。未設定なら `--no-ai` を付与。

### Q: 出力が文字化けする（Windows）
**A**: PowerShell で UTF-8 出力を有効化：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## 開発

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/DeckLens-Semantic-Diff-for-CAE.git
cd DeckLens-Semantic-Diff-for-CAE
pip install -e ".[dev]"
pytest -v
```

## フィードバック

Issue や Discussion は [GitHub](https://github.com/YOUR_GITHUB_USERNAME/DeckLens-Semantic-Diff-for-CAE/issues) へ。

---

**Made with ❤️ by CAE engineers, for CAE engineers**

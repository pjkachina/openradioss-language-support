# DeckLens 🚀 発行クイックスタート

5分で GitHub → PyPI + VS Code Marketplace に発行するチェックリスト。

## ✅ 前提条件チェック

```bash
# これらが存在することを確認
python --version          # 3.11+
node --version            # 18+
git remote -v             # origin を確認
```

## 📋 発行チェックリスト

### ステップ 1: GitHub リポジトリ作成（初回のみ）

- [ ] https://github.com/new で新規リポジトリ作成
  - Repository name: `DeckLens-Semantic-Diff-for-CAE`
  - Public, Initialize なし
- [ ] ローカルで remote 追加:
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/DeckLens-Semantic-Diff-for-CAE.git
  git branch -M main
  git push -u origin main
  ```

### ステップ 2: Secrets 設定（初回のみ）

GitHub リポジトリ → Settings → Secrets and variables → Actions

- [ ] **PYPI_API_TOKEN**
  - https://pypi.org → Account Settings → API tokens → Create new token
  - トークンをコピー & ペースト

- [ ] **VSCE_PAT**
  - https://dev.azure.com → Personal access tokens → New Token
  - Scope: Marketplace (Publish) + Marketplace (Manage)
  - トークンをコピー & ペースト

### ステップ 3: PNG アイコン作成（初回のみ）

- [ ] https://cloudconvert.com/svg-to-png で SVG → PNG 変換
  - Input: `assets/icon.svg`
  - Output: 128×128 PNG
  - ダウンロード: `assets/icon.png`

```bash
git add assets/icon.png
git commit -m "docs: add VS Code extension icon"
git push origin main
```

### ステップ 4: 動作確認

```bash
# Python CLI テスト
pip install -e .
pytest -v
decklens diff tests/fixtures/sample_v1.rad tests/fixtures/sample_v2.rad --no-ai

# TypeScript コンパイル確認
npm install
npm run compile
```

- [ ] Python テスト: 19/19 合格 ✅
- [ ] TypeScript コンパイル: エラーなし ✅

### ステップ 5: バージョン更新

ファイルを確認・更新：

- [ ] `pyproject.toml`: `version = "0.1.0"` 
- [ ] `package.json`: `"version": "0.1.0"`
- [ ] `CHANGELOG.md`: 最新エントリ確認

### ステップ 6: リリース（自動発行）

```bash
# タグ作成 & push
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# ✨ GitHub Actions が自動実行:
#   1. テスト実行
#   2. PyPI に発行
#   3. VS Code Marketplace に発行
#   4. GitHub Release を作成
```

- [ ] https://github.com/YOUR_USERNAME/DeckLens-Semantic-Diff-for-CAE/actions で進捗確認
- [ ] 全ステップが Green ✅

### ステップ 7: 確認

- [ ] PyPI: https://pypi.org/project/decklens/
- [ ] VS Code Marketplace: https://marketplace.visualstudio.com/items?itemName=MayaKachina.decklens
- [ ] GitHub Releases: https://github.com/YOUR_USERNAME/DeckLens-Semantic-Diff-for-CAE/releases

---

## 🎉 完了！

```bash
# PyPI から CLI をインストール
pip install decklens
decklens --version
# decklens, version 0.1.0

# VS Code で拡張を検索 & インストール
# 検索: "DeckLens"
```

---

## 🔄 次回以降（簡略版）

```bash
# 1. バージョン更新（3ファイル）
# pyproject.toml, package.json, CHANGELOG.md

# 2. Commit
git commit -m "chore: bump v0.2.0"

# 3. Tag & Push
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin main v0.2.0

# ✨ Done!
```

---

詳細は `GITHUB_SETUP.md` と `PUBLISHING.md` を参照。

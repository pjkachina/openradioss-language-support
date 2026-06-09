# GitHub Setup & Publishing Guide

DeckLens をGitHubから PyPI と VS Code Marketplace に発行するための完全ガイド。

## 📋 準備物チェックリスト

- [ ] GitHub アカウント
- [ ] PyPI アカウント (https://pypi.org/account/register/)
- [ ] VS Code Publisher ID (https://marketplace.visualstudio.com/manage)
- [ ] Azure DevOps Personal Access Token (PAT)
- [ ] Node.js 18+ (`node -v`)
- [ ] Python 3.11+ (`python --version`)

---

## Step 1️⃣: GitHub リポジトリを作成

### 1.1 GitHub で新規リポジトリを作成

1. GitHub にログイン: https://github.com/new
2. **Repository name**: `DeckLens-Semantic-Diff-for-CAE`
3. **Description**: `Engineering-aware semantic diff tool for CAE input files`
4. **Visibility**: Public
5. **Initialize repository**: チェック外す（ローカルから push）
6. **License**: MIT を選択（後で）
7. **Create repository** をクリック

### 1.2 ローカルリポジトリを GitHub に接続

```bash
cd c:\Users\maya\DeckLens-Engineering-Diff

# リモートを追加
git remote add origin https://github.com/YOUR_USERNAME/DeckLens-Semantic-Diff-for-CAE.git

# ブランチ名を main に変更
git branch -M main

# GitHub に push
git push -u origin main
```

### 1.3 GitHub で設定を確認

Settings → General で以下を確認：
- Default branch: `main`
- Allow auto-merge: チェック
- Dismiss stale PR approvals: チェック

---

## Step 2️⃣: PyPI 発行設定

### 2.1 PyPI に登録

1. PyPI にログイン: https://pypi.org/account/register/
2. メール確認
3. **Account Settings** → **API tokens**
4. **Create new token**
   - Token name: `decklens-github-actions`
   - Scope: Entire account
   - Token をコピー

### 2.2 GitHub Secret を追加

1. GitHub リポジトリ → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
   - Name: `PYPI_API_TOKEN`
   - Secret: PyPI から取得したトークンをペースト
3. **Add secret**

---

## Step 3️⃣: VS Code Marketplace 発行設定

### 3.1 VS Code Publisher ID を作成

1. VS Code Marketplace にログイン: https://marketplace.visualstudio.com/manage
2. GitHub アカウントで認証
3. **Create publisher**
   - Publisher name: `MayaKachina`
4. **Create** をクリック

### 3.2 Azure DevOps PAT を生成

1. Azure DevOps にログイン: https://dev.azure.com
2. User settings （右上のアイコン）
3. **Personal access tokens** → **New Token**
   - Name: `decklens-vscode-publish`
   - Scope: `Marketplace (Publish)` と `Marketplace (Manage)`
   - **Create** をクリック
4. PAT をコピー

### 3.3 GitHub Secret を追加

1. GitHub リポジトリ → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
   - Name: `VSCE_PAT`
   - Secret: Azure DevOps の PAT をペースト
3. **Add secret**

### 3.4 (オプション) Open VSX にも発行

1. Open VSX にログイン: https://open-vsx.org
2. **Login** → GitHub で認証
3. **Profile** → **Access Token**
4. Token を生成
5. GitHub Secret: `OVSX_PAT` を追加

---

## Step 4️⃣: 初回発行手順

### 4.1 バージョン・ファイルを確認

```bash
# pyproject.toml
cat pyproject.toml | grep "^version"
# version = "0.1.0"

# package.json
cat package.json | grep '"version"'
# "version": "0.1.0",

# CHANGELOG.md
head -10 CHANGELOG.md
# ## [0.1.0] - 2026-06-09
```

### 4.2 PNG アイコンを作成（VS Code Marketplace 用）

アイコンはまだ SVG のみです。以下のいずれかで PNG に変換：

**Option A: Online Tool**
1. https://cloudconvert.com/svg-to-png で `assets/icon.svg` をアップロード
2. 128×128 で PNG に変換
3. `assets/icon.png` として保存
4. Git に追加:
```bash
git add assets/icon.png
git commit -m "docs: add PNG icon for VS Code Marketplace"
git push origin main
```

**Option B: ImageMagick（Linux/macOS）**
```bash
convert -density 128 assets/icon.svg -resize 128x128 assets/icon.png
git add assets/icon.png
git commit -m "docs: add PNG icon for VS Code Marketplace"
git push origin main
```

### 4.3 ローカルで動作確認

```bash
# Python CLI
pip install -e .
decklens diff tests/fixtures/sample_v1.rad tests/fixtures/sample_v2.rad --no-ai

# VS Code 拡張（デバッグモード）
npm install
npm run compile
# VS Code でデバッグを開始（F5）
```

### 4.4 タグを作成して自動発行

```bash
# タグを作成
git tag -a v0.1.0 -m "Release v0.1.0: Initial release"

# GitHub に push（CI/CD が自動実行）
git push origin v0.1.0

# GitHub Actions の進捗を確認
# https://github.com/YOUR_USERNAME/DeckLens-Semantic-Diff-for-CAE/actions
```

CI/CD パイプラインが以下を自動実行します：

1. ✅ Python テスト実行（Windows/macOS/Linux × Python 3.11/3.12）
2. ✅ TypeScript コンパイル
3. ✅ PyPI にアップロード（デフォルト）
4. ✅ VS Code Marketplace にアップロード（VSCE_PAT が必要）
5. ✅ GitHub Release を作成

---

## Step 5️⃣: 発行確認

### PyPI

```bash
# インストール確認
pip install decklens
decklens --version
# decklens, version 0.1.0
```

確認: https://pypi.org/project/decklens/

### VS Code Marketplace

確認: https://marketplace.visualstudio.com/items?itemName=MayaKachina.decklens

### Open VSX（オプション）

確認: https://open-vsx.org/extension/MayaKachina/decklens

---

## 🔄 今後のリリース手順（簡略版）

新しい機能をリリースする場合：

```bash
# 1. バージョン更新（semver）
# pyproject.toml, package.json, CHANGELOG.md を更新

# 2. コミット
git add .
git commit -m "chore: bump version to 0.2.0"

# 3. タグ作成
git tag -a v0.2.0 -m "Release v0.2.0: Add feature X"

# 4. Push（自動発行）
git push origin main
git push origin v0.2.0

# Done! CI/CD が PyPI と Marketplace に自動発行
```

---

## 🐛 トラブルシューティング

### Q: "Invalid publisher name" エラーが出る
**A**: VS Code Marketplace で Publisher ID を確認
```bash
vsce login MayaKachina
# Azure DevOps PAT でログイン
```

### Q: PyPI に同じバージョンで push できない
**A**: バージョン番号を新しくしてコミット
```bash
# pyproject.toml と package.json で version をインクリメント
git commit -m "chore: bump to 0.1.1"
git tag -a v0.1.1 -m "Patch release"
git push origin main v0.1.1
```

### Q: GitHub Actions が失敗している
**A**: Actions ログで詳細を確認
1. GitHub リポジトリ → **Actions** タブ
2. 失敗したワークフローをクリック
3. ログを確認（Secrets が正しいか、テストが通るか）

### Q: VS Code で拡張が読み込まれない
**A**: 開発モード（F5）でテスト
```bash
npm run compile
# VS Code で F5 キー
# デバッグコンソールでエラーを確認
```

---

## 📚 ドキュメント参考

- [VS Code Extension Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Ready to ship? Let's go! 🚀**

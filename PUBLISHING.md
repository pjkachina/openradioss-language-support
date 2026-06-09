# Publishing Guide

DeckLens を PyPI と VS Code Marketplace に発行するための手順です。

## 前提条件

- GitHub アカウント
- VS Code Publisher ID（[dev.azure.com](https://dev.azure.com) で取得）
- PyPI アカウント（[pypi.org](https://pypi.org)）
- `vsce` CLI (`npm install -g vsce`)

## ステップ 1: GitHub にリポジトリを作成

```bash
# 1. GitHub で新規 public repository を作成
#    Repository name: DeckLens-Semantic-Diff-for-CAE
#    Description: Engineering-aware semantic diff tool for CAE input files
#    License: MIT

# 2. ローカルリポジトリを接続
git remote add origin https://github.com/YOUR_USERNAME/DeckLens-Semantic-Diff-for-CAE.git
git branch -M main
git push -u origin main

# 3. Releases を有効化（GitHub Settings → Releases）
```

## ステップ 2: PyPI 発行準備

### 2.1 PyPI アカウントセットアップ

```bash
# PyPI にアカウントを作成
# https://pypi.org/account/register/

# API token を生成（Account Settings → API tokens）
# トークン名: "decklens-github-action"
```

### 2.2 GitHub Secrets に追加

GitHub リポジトリ Settings → Secrets and variables → Actions:

- **PYPI_API_TOKEN**: PyPI から取得した API token

### 2.3 PyPI パッケージメタデータ確認

```bash
# ローカルで検証
python -m build
twine check dist/*
```

## ステップ 3: VS Code Marketplace 発行準備

### 3.1 VS Code Publisher ID 取得

```bash
# Azure DevOps にログイン
# https://dev.azure.com

# Organization を作成（なければ）
# Publisher を作成: "MayaKachina"
```

### 3.2 Personal Access Token (PAT) 生成

Azure DevOps → User Settings → Personal access tokens:

- **Name**: `decklens-vscode-publish`
- **Organization**: All accessible organizations
- **Scopes**: 
  - Marketplace: `Publish`
  - Marketplace: `Manage`

### 3.3 GitHub Secrets に追加

- **VSCE_PAT**: VS Code PAT token
- **OVSX_PAT**: Open VSX token（オプション）

```bash
# Open VSX の PAT を取得（オプション）
# https://open-vsx.org/user/profile
```

## ステップ 4: リリース作成と発行

### 4.1 バージョンを更新

```bash
# pyproject.toml
# package.json
# CHANGELOG.md
```

変更内容の例：

```toml
# pyproject.toml
version = "0.2.0"
```

```json
// package.json
"version": "0.2.0",
```

### 4.2 コミットとタグ作成

```bash
git add .
git commit -m "chore: bump version to 0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0: Add NASTRAN parser"
git push origin main
git push origin v0.2.0
```

### 4.3 自動発行（CI/CD）

GitHub Actions が自動的に以下を実行します：

1. ✅ Python テスト実行（ubuntu, windows, macos）
2. ✅ TypeScript コンパイル
3. ✅ PyPI に発行（v タグの場合）
4. ✅ VS Code Marketplace に発行（v タグの場合）

```bash
# または手動で:
npm run publish  # VS Code Marketplace
twine upload dist/*  # PyPI
```

## ステップ 5: 動作確認

### PyPI

```bash
pip install decklens
decklens --version
```

### VS Code Marketplace

VS Code Extensions → "DeckLens" で検索

### Open VSX（オプション）

https://open-vsx.org/extension/MayaKachina/decklens

## トラブルシューティング

### VSCE エラー: "Invalid publisher name"

```bash
# Publisher ID が正しいか確認
vsce login MayaKachina
# Azure DevOps の PAT で認証
```

### PyPI エラー: "File already exists"

```bash
# バージョン番号が重複している
# CHANGELOG.md で新バージョンを確認
```

## ドキュメント更新

新しいバージョン発行時：

1. README.md の例を更新
2. CHANGELOG.md に変更内容を記載
3. CONTRIBUTING.md のセットアップ手順を確認
4. GitHub Releases ページに詳細を記載

## リリースノートテンプレート

```markdown
## v0.2.0 - 2026-07-15

### New Features
- 🚀 Add NASTRAN (.bdf) parser support
- 🎨 Improve diff visualization

### Bug Fixes
- 🐛 Fix Windows cp932 encoding issue
- 🔧 Correct bending stiffness calculation

### Documentation
- 📖 Add NASTRAN support guide

### Contributors
- [@pj-kachina](https://github.com/pj-kachina)
```

## 定期メンテナンス

- 月 1 回: 依存関係をアップデート（Dependabot）
- 四半期ごと: セキュリティ監査
- 年 1 回: 対応ツール・バージョンを確認

---

**Note**: 初回発行は手動手続きが必要です。その後、CI/CD で自動化されます。

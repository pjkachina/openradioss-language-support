# Contributing to DeckLens

ありがとうございます！DeckLensへの貢献をお歓迎します。

## セットアップ

```bash
git clone https://github.com/YOUR_USERNAME/DeckLens-Semantic-Diff-for-CAE.git
cd DeckLens-Semantic-Diff-for-CAE
pip install -e ".[dev]"
npm install
```

## 開発ワークフロー

### Python CLI（バックエンド）

```bash
# テスト実行
pytest -v

# コード品質チェック
pytest --cov=decklens tests/
```

### VS Code 拡張機能（フロントエンド）

```bash
# TypeScript コンパイル
npm run compile

# ウォッチモード
npm run watch

# 拡張機能のテスト（VS Code が起動します）
npm run test
```

## プルリクエストガイドライン

1. **ブランチ作成**: `feature/xxx` または `fix/xxx` を作成
2. **テスト追加**: 新機能にはテストを追加
3. **コミット**: 明確で簡潔なコミットメッセージを使用
4. **ドキュメント**: 新機能には README 更新を含める
5. **CI/CD**: すべてのテストが通っていることを確認

### コミットメッセージの例

```
feat: Add NASTRAN parser support

- Implement BDF card parsing
- Add MAT1, PSHELL, PCOMP support
- Update CHANGELOG

Fixes #42
```

## コーディング規約

### Python
- PEP 8 準拠
- Type hints を使用
- ドキュメント文字列を記述

### TypeScript
- tslint 準拠
- 4 スペースインデント
- JSDoc を使用

## ローカライゼーション

DeckLens は複数言語対応を計画しています。翻訳のご協力をお待ちしています。

翻訳ファイル: `i18n/` ディレクトリ（計画中）

## セキュリティ

セキュリティ脆弱性を発見した場合は、公開 issue ではなく、メール（pj.kachina@gmail.com）で報告してください。

## ライセンス

すべての貢献は MIT ライセンスの下で公開されます。

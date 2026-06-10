# OpenRadioss Language Support

VS Code extension providing syntax highlighting and language support for OpenRadioss input files (`.rad`).

## Project layout

```
src/
  extension.ts                      # TypeScript extension entry point
syntaxes/
  openradioss.tmLanguage.json       # TextMate grammar for .rad files
language-configuration.json         # Bracket/comment configuration
assets/
  icon.png / icon.svg               # Extension icon
package.json                        # VS Code extension manifest
tsconfig.json                       # TypeScript config
```

## Quick start

```bash
npm install
npm run compile
```

Press `F5` in VS Code to launch the Extension Development Host.

## Build & package

```bash
npm run compile
npx vsce package
```

## Publishing

```bash
npx vsce publish
```

Requires a Personal Access Token from https://marketplace.visualstudio.com/manage.

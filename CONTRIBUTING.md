# Contributing to OpenRadioss-language package

Contributions are welcome — bug reports, keyword additions, and grammar improvements are all appreciated.

## Setup

```bash
git clone https://github.com/pjkachina/openradioss-language-support.git
cd openradioss-language-support
npm install
npm run compile
```

Press `F5` in VS Code to launch the Extension Development Host and test changes live.

## How to contribute

### Adding or fixing keywords

The grammar is defined in [syntaxes/openradioss.tmLanguage.json](syntaxes/openradioss.tmLanguage.json).
Keywords are sourced from the official OpenRadioss Starter Input Reference:
https://help.altair.com/hwsolvers/rad/topics/solvers/rad/starter_input_r.htm

When adding keywords:
1. Verify the keyword exists in the official documentation
2. Place it in the correct category block within the grammar file
3. Note the source URL in your PR description

### Pull request guidelines

1. Create a branch: `feature/xxx` or `fix/xxx`
2. Keep changes focused — one topic per PR
3. Use clear commit messages (e.g. `feat: add /SENSOR keyword`)
4. Update `CHANGELOG.md` under `[Unreleased]`

## Build & package

```bash
npm run compile       # compile TypeScript
npx vsce package      # create .vsix
```

## Reporting issues

Use the [GitHub issue tracker](https://github.com/pjkachina/openradioss-language-support/issues).
For security issues, email pj.kachina@gmail.com directly instead of opening a public issue.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-09

### Added
- Initial release: OpenRadioss (.rad) parser
- Semantic diff engine with engineering-aware change detection
- Severity classification (CRITICAL, WARNING, INFO)
- Bending stiffness annotation for thickness changes (EI ∝ t³)
- Claude Opus 4.8 AI analysis with adaptive thinking
- Rich CLI with colored table output
- JSON output format for CI/CD integration
- `--min-severity` filter option
- Windows UTF-8 support
- 19 test cases (parser, diff, integration)
- VS Code extension integration

### Planned
- NASTRAN (.bdf) parser (Q3 2026)
- LS-DYNA (.k) parser (Q3 2026)
- Web UI dashboard
- Git integration (pre-commit hooks)
- Batch comparison support
- Localization (Japanese, Chinese, German)

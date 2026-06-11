# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-06-11

### Added
- Expanded syntax highlighting: 300+ keywords sourced from official Altair documentation
  - `/FAIL/*` — 40+ failure models (JOHNSON, GURSON, HASHIN, PUCK, TSAIWU, etc.)
  - `/EOS/*` — 17+ equations of state (GRUNEISEN, IDEAL-GAS, TABULATED, etc.)
  - `/INTER/TYPE*` — all contact interface types and subtypes
  - `/INI*` — full set of initial condition blocks and subtypes
  - `/ALE/*`, `/EBCS/*` — ALE and fluid boundary condition blocks
  - `/MONVOL/*` — monitored volume blocks
  - `/FRAME/*`, `/DFS/*`, `/ADMESH/*`, `/PERTURB/*` and more
- New extension icon: FEM hex-element mesh design

### Changed
- README rewritten with keyword coverage table and live example deck

## [1.0.1] - 2026-06-10

### Changed
- Publisher changed from `MayaKachina` to `pjkachina`
- GitHub repository URL corrected

## [1.0.0] - 2026-06-09

### Added
- Initial release: syntax highlighting for OpenRadioss `.rad` / `.radians` files
- TextMate grammar covering basic keywords (`/BEGIN`, `/END`, `/MAT`, `/PROP`, `/SHELL`, `/NODE`, `/BCS`, etc.)
- Language configuration (bracket matching, comment toggling)
- File associations for `.rad` and `.radians`

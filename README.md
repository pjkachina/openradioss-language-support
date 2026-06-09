# OpenRadioss Language Support

![VS Code Extension](https://img.shields.io/badge/extension-VS%20Code-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Syntax highlighting and language support for **OpenRadioss** CAE input files (.rad) in Visual Studio Code.

## Features

✅ **Complete Syntax Highlighting**
- Keywords and sections (`/BEGIN`, `/END`, `/UNIT`, `/MAT`, `/PROP`, `/SHELL`, `/NODE`, `/ELEMENT`, etc.)
- Comments (`#` lines)
- Numeric values (integers, decimals, scientific notation)
- Parameters and variables

✅ **Language Support**
- File association for `.rad` and `.radians` files
- Proper bracket matching and auto-closing
- Line comment support (`#`)

✅ **Smart Formatting**
- Automatic bracket pairing
- Multi-line bracket support
- String literal highlighting

## Installation

1. Open **Visual Studio Code**
2. Go to **Extensions** (Ctrl+Shift+X)
3. Search for **"OpenRadioss Language Support"**
4. Click **Install**

Or install directly via CLI:
```bash
code --install-extension MayaKachina.openradioss-language-support
```

## Usage

Simply open any `.rad` or `.radians` file in VS Code, and syntax highlighting will be applied automatically.

**Example OpenRadioss deck:**
```
# Material definition
/MAT/ELAST/1
STEEL_MATERIAL
  7.85e-9
  210000.0  0.3

# Shell property
/PROP/SHELL/1
OUTER_PANEL
  0  0  0  0
  1.2  0.0  0.0  0  0  0  0  0

# Node coordinates
/NODE
         1       0.000000       0.000000       0.000000
         2     100.000000       0.000000       0.000000
```

## Supported Sections

The extension recognizes all major OpenRadioss sections including:
- `/UNIT` — Unit system definition
- `/MATERIAL`, `/MAT` — Material properties
- `/PROPERTY`, `/PROP` — Element properties (SHELL, SOLID, BEAM, etc.)
- `/PART` — Part definitions
- `/NODE` — Node coordinates
- `/SHELL`, `/ELEMENT` — Element definitions
- `/BCS` — Boundary conditions
- `/CLOAD`, `/DLOAD` — Load definitions
- `/LOAD` — Load cases
- And many more CAE-specific sections

## Settings

This extension has minimal settings — just enable/disable the language support:
- Right-click a `.rad` file → Select "Open With" → Choose **OpenRadioss Language Support**

For more details on OpenRadioss syntax, refer to the official [OpenRadioss documentation](https://openradioss.atlassian.net/).

## License

MIT

## Feedback & Support

For issues or feature requests, visit:
- GitHub: [pj-kachina/openradioss-language-support](https://github.com/pj-kachina/openradioss-language-support)

---

**Tip:** Pair this extension with other CAE tools and linters for a complete development environment.

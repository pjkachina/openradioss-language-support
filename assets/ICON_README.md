# DeckLens Icon

The VS Code extension requires a 128×128 PNG icon at `assets/icon.png`.

## Creating the Icon

You have two options:

### Option 1: Use Online Tool
1. Open `icon.svg` in [convertio.co](https://convertio.co/svg-png/) or similar
2. Convert to PNG (128×128)
3. Save as `icon.png`

### Option 2: Use ImageMagick (Linux/macOS)
```bash
convert -density 128 icon.svg -resize 128x128 icon.png
```

### Option 3: Use Online SVG to PNG Converter
1. https://cloudconvert.com/svg-to-png
2. Upload `icon.svg`
3. Set size to 128×128
4. Download as PNG

## PNG Requirements
- **Size**: 128×128 pixels
- **Format**: PNG with transparency
- **Location**: `assets/icon.png`
- **Colors**: Use solid colors (avoid gradients if possible)

Once created, commit to git:
```bash
git add assets/icon.png
git commit -m "docs: add VS Code extension icon"
```

The extension will work with just `icon.svg`, but VS Code Marketplace **requires** a PNG icon for the listing page.

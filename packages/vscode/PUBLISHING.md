# Publishing Resonance to VS Code Marketplace

Publisher: **wcalmels** (same as Phi47 Superpowers)

## Package

```bash
cd packages/vscode
npm install
npx @vscode/vsce package
```

Output: `resonance-0.2.1.vsix`

## Publish via web (no PAT)

1. https://marketplace.visualstudio.com/manage
2. Publisher **wcalmels** → **+ New extension** → **Visual Studio Code**
3. Upload `resonance-0.2.1.vsix`
4. **Make Public** when ready

## Publish via CLI

```bash
npx @vscode/vsce publish -p <PAT>
```

## After publish

Update root `README.md` badge:

```markdown
[![VS Marketplace](https://img.shields.io/visual-studio-marketplace/v/wcalmels.resonance)](https://marketplace.visualstudio.com/items?itemName=wcalmels.resonance)
```

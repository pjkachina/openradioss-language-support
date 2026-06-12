import * as vscode from 'vscode';

const BLOCK_PATTERN = /^\s*(\/[A-Z][A-Z0-9_]*(?:\/[A-Z0-9_]+)*(?:\/\d+)?)\s*$/;
const SKIP_PATTERN = /^\s*[#$]/;
const DATA_ONLY_PATTERN = /^\s*[\d\s.,eEdD+\-]+\s*$/;

const CATEGORY_ICONS: Record<string, string> = {
    '/MAT':    'symbol-interface',
    '/PROP':   'symbol-property',
    '/PART':   'package',
    '/NODE':   'symbol-array',
    '/BRICK':  'symbol-array',
    '/SHELL':  'symbol-array',
    '/BEAM':   'symbol-array',
    '/INTER':  'link',
    '/BCS':    'lock',
    '/FAIL':   'warning',
    '/EOS':    'beaker',
    '/MONVOL': 'eye',
    '/LOAD':   'arrow-right',
    '/CLOAD':  'arrow-right',
    '/GRAV':   'arrow-down',
    '/INI':    'history',
    '/ALE':    'symbol-misc',
    '/FUNCT':  'graph',
    '/TH':     'graph-line',
    '/UNIT':   'symbol-ruler',
};

function iconForKeyword(keyword: string): vscode.ThemeIcon {
    for (const prefix of Object.keys(CATEGORY_ICONS)) {
        if (keyword.startsWith(prefix)) {
            return new vscode.ThemeIcon(CATEGORY_ICONS[prefix]);
        }
    }
    return new vscode.ThemeIcon('symbol-namespace');
}

export class BlockItem extends vscode.TreeItem {
    constructor(
        public readonly keyword: string,
        public readonly blockName: string,
        public readonly lineNumber: number,
    ) {
        super(keyword, vscode.TreeItemCollapsibleState.None);
        this.description = blockName;
        this.tooltip = `Line ${lineNumber + 1}`;
        this.iconPath = iconForKeyword(keyword);
        this.command = {
            command: 'openradioss.gotoBlock',
            title: 'Go to block',
            arguments: [lineNumber],
        };
    }
}

export class RadOutlineProvider implements vscode.TreeDataProvider<BlockItem> {
    private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: BlockItem): vscode.TreeItem {
        return element;
    }

    getChildren(): BlockItem[] {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'rad') {
            return [];
        }
        return this.parseBlocks(editor.document);
    }

    private parseBlocks(document: vscode.TextDocument): BlockItem[] {
        const items: BlockItem[] = [];

        for (let i = 0; i < document.lineCount; i++) {
            const line = document.lineAt(i).text;
            const match = BLOCK_PATTERN.exec(line);
            if (!match) { continue; }

            const keyword = match[1];

            // Skip /BEGIN and /END — structural markers, not blocks
            if (keyword === '/BEGIN' || keyword === '/END') { continue; }

            // Look ahead for the block name (first non-comment, non-data line after keyword)
            let blockName = '';
            for (let j = i + 1; j < Math.min(i + 3, document.lineCount); j++) {
                const next = document.lineAt(j).text.trim();
                if (!next || SKIP_PATTERN.test(next) || DATA_ONLY_PATTERN.test(next) || BLOCK_PATTERN.test(next)) {
                    break;
                }
                blockName = next.split(/\s+/)[0];
                break;
            }

            items.push(new BlockItem(keyword, blockName, i));
        }

        return items;
    }
}

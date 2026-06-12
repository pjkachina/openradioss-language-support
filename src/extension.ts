import * as vscode from 'vscode';
import { RadOutlineProvider } from './outlineProvider';

export function activate(context: vscode.ExtensionContext) {
    const provider = new RadOutlineProvider();

    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('openradiossOutline', provider),

        vscode.commands.registerCommand('openradioss.refreshOutline', () => {
            provider.refresh();
        }),

        vscode.commands.registerCommand('openradioss.gotoBlock', (lineNumber: number) => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) { return; }
            const position = new vscode.Position(lineNumber, 0);
            editor.selection = new vscode.Selection(position, position);
            editor.revealRange(
                new vscode.Range(position, position),
                vscode.TextEditorRevealType.AtTop,
            );
        }),

        vscode.window.onDidChangeActiveTextEditor(() => provider.refresh()),

        vscode.workspace.onDidChangeTextDocument(e => {
            if (e.document === vscode.window.activeTextEditor?.document) {
                provider.refresh();
            }
        }),
    );
}

export function deactivate() {}

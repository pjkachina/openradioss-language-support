import * as vscode from 'vscode';
import { execSync, spawn } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

interface DiffResult {
	changes: Change[];
	summary: string;
}

interface Change {
	severity: 'INFO' | 'WARNING' | 'CRITICAL';
	category: string;
	item_type: string;
	item_id: string | number;
	item_name: string;
	field: string;
	old_value: any;
	new_value: any;
	unit?: string;
	percent_change?: number;
}

let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
	outputChannel = vscode.window.createOutputChannel('DeckLens');
	outputChannel.appendLine('DeckLens extension activated.');

	// Command: Compare with file
	let compareWithFile = vscode.commands.registerCommand(
		'decklens.compareWithFile',
		async (clickedFile: vscode.Uri) => {
			await compareWithFileCommand(clickedFile);
		}
	);

	// Command: Show diff (palette)
	let diffCommand = vscode.commands.registerCommand(
		'decklens.diff',
		async () => {
			const editor = vscode.window.activeTextEditor;
			if (!editor) {
				vscode.window.showErrorMessage('No file is open');
				return;
			}
			const beforeFile = editor.document.uri.fsPath;
			const afterFile = await pickFile();
			if (afterFile) {
				await runDiff(beforeFile, afterFile);
			}
		}
	);

	// Command: Open settings
	let settingsCommand = vscode.commands.registerCommand(
		'decklens.openSettings',
		async () => {
			await vscode.commands.executeCommand(
				'workbench.action.openSettings',
				'decklens'
			);
		}
	);

	context.subscriptions.push(compareWithFile, diffCommand, settingsCommand);

	// Show startup message
	const message = 'DeckLens Semantic Diff for CAE is ready. Right-click a .rad/.bdf/.k file to compare.';
	outputChannel.appendLine(message);
}

async function compareWithFileCommand(beforeUri: vscode.Uri) {
	const beforeFile = beforeUri.fsPath;

	// Check if file is CAE format
	const ext = path.extname(beforeFile).toLowerCase();
	if (!['.rad', '.bdf', '.k'].includes(ext)) {
		vscode.window.showErrorMessage('DeckLens only supports .rad, .bdf, .k files');
		return;
	}

	// Pick the "after" file
	const afterFile = await pickFile();
	if (afterFile) {
		await runDiff(beforeFile, afterFile);
	}
}

async function pickFile(): Promise<string | undefined> {
	const uri = await vscode.window.showOpenDialog({
		canSelectMany: false,
		filters: {
			'CAE Files': ['rad', 'bdf', 'k'],
			'All Files': ['*']
		}
	});
	return uri && uri[0] ? uri[0].fsPath : undefined;
}

async function runDiff(beforeFile: string, afterFile: string): Promise<void> {
	// Show progress
	await vscode.window.withProgress(
		{
			location: vscode.ProgressLocation.Notification,
			title: 'DeckLens: Running semantic diff...',
			cancellable: false
		},
		async (progress) => {
			try {
				// Get config
				const config = vscode.workspace.getConfiguration('decklens');
				const enableAI = config.get<boolean>('enableAI', true);
				const minSeverity = config.get<string>('minSeverity', 'INFO');
				const model = config.get<string>('model', 'claude-opus-4-8');
				const apiKey = config.get<string>('apiKey', '');

				// Build command
				let cmd = `decklens diff "${beforeFile}" "${afterFile}" --format json`;
				if (!enableAI) {
					cmd += ' --no-ai';
				}
				if (minSeverity !== 'INFO') {
					cmd += ` --min-severity ${minSeverity}`;
				}
				if (model !== 'claude-opus-4-8') {
					cmd += ` --model ${model}`;
				}

				// Set env var if API key provided
				const env = { ...process.env };
				if (apiKey) {
					env.ANTHROPIC_API_KEY = apiKey;
				}

				// Run command
				outputChannel.clear();
				outputChannel.appendLine(`[DeckLens] Running: ${cmd}`);
				outputChannel.show(true);

				let output = '';
				try {
					output = execSync(cmd, {
						encoding: 'utf-8',
						env,
						maxBuffer: 10 * 1024 * 1024 // 10MB
					});
				} catch (e: any) {
					if (e.stdout) output = e.stdout.toString();
					if (e.stderr) outputChannel.appendLine('STDERR: ' + e.stderr.toString());
					outputChannel.appendLine('Error: ' + e.message);
					vscode.window.showErrorMessage(`DeckLens failed: ${e.message}`);
					return;
				}

				// Parse JSON results
				let results: Change[] = [];
				try {
					results = JSON.parse(output);
				} catch {
					outputChannel.appendLine('Failed to parse JSON output. Raw output:');
					outputChannel.appendLine(output);
				}

				// Display results
				displayResults(beforeFile, afterFile, results);

				// Log to output
				outputChannel.appendLine('');
				outputChannel.appendLine('=== RESULTS ===');
				outputChannel.appendLine(JSON.stringify(results, null, 2));
				outputChannel.show(true);

			} catch (error: any) {
				outputChannel.appendLine(`Error: ${error.message}`);
				vscode.window.showErrorMessage(`DeckLens error: ${error.message}`);
			}
		}
	);
}

function displayResults(beforeFile: string, afterFile: string, changes: Change[]): void {
	const panel = vscode.window.createWebviewPanel(
		'decklens-results',
		'DeckLens Diff Results',
		vscode.ViewColumn.Beside,
		{ enableScripts: true }
	);

	const html = generateHtml(beforeFile, afterFile, changes);
	panel.webview.html = html;
}

function generateHtml(beforeFile: string, afterFile: string, changes: Change[]): string {
	const criticalCount = changes.filter(c => c.severity === 'CRITICAL').length;
	const warningCount = changes.filter(c => c.severity === 'WARNING').length;
	const infoCount = changes.filter(c => c.severity === 'INFO').length;

	const rows = changes.map(ch => `
		<tr class="severity-${ch.severity.toLowerCase()}">
			<td class="sev-badge">${ch.severity[0]}</td>
			<td>${ch.category}</td>
			<td><code>${ch.item_type}/${ch.item_id}</code></td>
			<td>${ch.item_name}</td>
			<td>${ch.field}</td>
			<td>${formatValue(ch.old_value, ch.unit)}</td>
			<td>${formatValue(ch.new_value, ch.unit)}</td>
			<td>${ch.percent_change ? formatPercent(ch.percent_change) : '—'}</td>
		</tr>
	`).join('');

	return `<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<style>
		* { box-sizing: border-box; }
		body {
			font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
			margin: 0;
			padding: 16px;
			background: var(--vscode-editor-background);
			color: var(--vscode-editor-foreground);
			font-size: 13px;
		}
		.header {
			margin-bottom: 20px;
		}
		.header h2 {
			margin: 0 0 8px 0;
			color: var(--vscode-terminal-ansiBlue);
		}
		.files {
			display: flex;
			gap: 20px;
			margin-top: 8px;
			font-size: 12px;
		}
		.file {
			flex: 1;
		}
		.file-label {
			color: var(--vscode-descriptionForeground);
			display: block;
			margin-bottom: 4px;
		}
		.file-path {
			font-family: 'Monaco', 'Menlo', monospace;
			background: var(--vscode-input-background);
			padding: 4px 8px;
			border-radius: 3px;
			word-break: break-all;
		}

		.summary {
			display: flex;
			gap: 16px;
			margin: 16px 0;
			padding: 12px;
			background: var(--vscode-input-background);
			border-radius: 4px;
			border-left: 4px solid var(--vscode-terminal-ansiRed);
		}
		.summary-item {
			display: flex;
			align-items: center;
			gap: 8px;
		}
		.summary-count {
			font-weight: bold;
			font-size: 16px;
		}
		.severity-critical { color: var(--vscode-terminal-ansiRed); }
		.severity-warning { color: var(--vscode-terminal-ansiYellow); }
		.severity-info { color: var(--vscode-terminal-ansiCyan); }

		table {
			width: 100%;
			border-collapse: collapse;
			margin-top: 16px;
		}
		th {
			text-align: left;
			padding: 8px;
			background: var(--vscode-input-background);
			border-bottom: 2px solid var(--vscode-focusBorder);
			font-weight: 600;
			font-size: 12px;
			text-transform: uppercase;
		}
		td {
			padding: 8px;
			border-bottom: 1px solid var(--vscode-widget-border);
		}
		tr:hover {
			background: var(--vscode-list-hoverBackground);
		}
		tr.severity-critical { border-left: 4px solid var(--vscode-terminal-ansiRed); }
		tr.severity-warning { border-left: 4px solid var(--vscode-terminal-ansiYellow); }
		tr.severity-info { border-left: 4px solid var(--vscode-terminal-ansiCyan); }

		.sev-badge {
			font-weight: bold;
			text-transform: uppercase;
			font-size: 11px;
			padding: 2px 6px !important;
			border-radius: 3px;
			background: var(--vscode-input-background);
		}
		code {
			font-family: 'Monaco', monospace;
			background: var(--vscode-input-background);
			padding: 2px 4px;
			border-radius: 2px;
			font-size: 11px;
		}
		.percent {
			font-weight: 600;
		}
		.percent.increase { color: var(--vscode-terminal-ansiRed); }
		.percent.decrease { color: var(--vscode-terminal-ansiGreen); }

		.no-changes {
			padding: 20px;
			text-align: center;
			color: var(--vscode-descriptionForeground);
		}
	</style>
</head>
<body>
	<div class="header">
		<h2>DeckLens Semantic Diff</h2>
		<div class="files">
			<div class="file">
				<span class="file-label">📋 Before</span>
				<div class="file-path">${escapeHtml(beforeFile)}</div>
			</div>
			<div class="file">
				<span class="file-label">📋 After</span>
				<div class="file-path">${escapeHtml(afterFile)}</div>
			</div>
		</div>
	</div>

	<div class="summary">
		<div class="summary-item">
			<span class="summary-count severity-critical">${criticalCount}</span>
			<span>CRITICAL</span>
		</div>
		<div class="summary-item">
			<span class="summary-count severity-warning">${warningCount}</span>
			<span>WARNING</span>
		</div>
		<div class="summary-item">
			<span class="summary-count severity-info">${infoCount}</span>
			<span>INFO</span>
		</div>
	</div>

	${changes.length === 0 ? '<div class="no-changes">✅ No changes detected above severity threshold</div>' : `
		<table>
			<thead>
				<tr>
					<th>Sev</th>
					<th>Category</th>
					<th>Type / ID</th>
					<th>Name</th>
					<th>Field</th>
					<th>Before</th>
					<th>After</th>
					<th>Change</th>
				</tr>
			</thead>
			<tbody>
				${rows}
			</tbody>
		</table>
	`}
</body>
</html>`;
}

function formatValue(v: any, unit?: string): string {
	if (v === null || v === undefined) return '—';
	const u = unit ? ` ${unit}` : '';
	if (typeof v === 'number') {
		return v.toLocaleString() + u;
	}
	return String(v) + u;
}

function formatPercent(pct: number): string {
	const sign = pct > 0 ? '+' : '';
	const cls = pct > 0 ? 'increase' : 'decrease';
	return `<span class="percent ${cls}">${sign}${pct.toFixed(1)}%</span>`;
}

function escapeHtml(text: string): string {
	const div = document.createElement('div');
	div.textContent = text;
	return div.innerHTML;
}

export function deactivate() {}

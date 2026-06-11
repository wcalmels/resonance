// Resonance VS Code Extension — thin wrapper around packages/core CLI

const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const tokenStats = {
    sessions: [],
    record(fullTokens, sentTokens, taskName) {
        this.sessions.push({ fullTokens, sentTokens, taskName, ts: Date.now() });
    },
    summary() {
        if (!this.sessions.length) return 'No sessions yet.';
        const total = this.sessions.reduce((a, s) => a + s.fullTokens, 0);
        const sent = this.sessions.reduce((a, s) => a + s.sentTokens, 0);
        const saved = total - sent;
        const pct = total > 0 ? Math.round((saved / total) * 100) : 0;
        return `Sessions: ${this.sessions.length} | Tokens saved: ${saved.toLocaleString()} (${pct}%) | Sent: ${sent.toLocaleString()} vs full: ${total.toLocaleString()}`;
    }
};

function getConfig() {
    return vscode.workspace.getConfiguration('resonance');
}

function getPython() {
    const configured = getConfig().get('pythonPath');
    if (configured) return configured;
    return process.platform === 'win32' ? 'py -3' : 'python3';
}

function getApiKey() {
    return getConfig().get('apiKey') || process.env.ANTHROPIC_API_KEY || '';
}

function runResonance(args, env = {}) {
    return new Promise((resolve, reject) => {
        const python = getPython();
        const cmd = `"${python}" -m resonance ${args}`;
        exec(cmd, {
            timeout: 120000,
            env: { ...process.env, ...env },
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
        }, (err, stdout, stderr) => {
            if (err) reject(new Error(stderr || err.message));
            else resolve(stdout.trim());
        });
    });
}

function compareContext(filePath, mode) {
    return runResonance(`context "${filePath}" --mode ${mode} --compare`);
}

function extractContextToTemp(filePath, mode) {
    const tmp = path.join(os.tmpdir(), `resonance_context_${Date.now()}.txt`);
    const python = getPython();
    const cmd = `"${python}" -m resonance context "${filePath}" --mode ${mode}`;

    return new Promise((resolve, reject) => {
        exec(cmd, { timeout: 30000 }, (err, stdout, stderr) => {
            if (err) {
                reject(new Error(stderr || err.message));
                return;
            }
            fs.writeFileSync(tmp, stdout);
            resolve(tmp);
        });
    });
}

function parseCompareOutput(output) {
    const lines = Object.fromEntries(
        output.split('\n').map(line => {
            const idx = line.indexOf(':');
            if (idx === -1) return [line, ''];
            return [line.slice(0, idx).trim(), line.slice(idx + 1).trim()];
        })
    );
    return {
        fullTokens: parseInt(lines['full tokens'] || '0', 10),
        minimalTokens: parseInt((lines['minimal tokens'] || '0').replace(':', ''), 10),
        savedPercent: parseInt((lines.saved || '0').match(/\((\d+)%\)/)?.[1] || '0', 10)
    };
}

async function callGenerate(bot, task, filePath, mode, outputPath) {
    const apiKey = getApiKey();
    if (!apiKey) {
        throw new Error('No API key. Set resonance.apiKey or ANTHROPIC_API_KEY.');
    }

    const contextFile = await extractContextToTemp(filePath, mode);
    const args = [
        'generate',
        `--bot "${bot}"`,
        `--task "${task.replace(/"/g, '\\"')}"`,
        `--context-file "${contextFile}"`,
        `--output "${outputPath}"`
    ].join(' ');

    return runResonance(args, { ANTHROPIC_API_KEY: apiKey });
}

async function generateTests() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('Open a Python file first.');
        return;
    }

    const filePath = editor.document.fileName;
    const fileName = path.basename(filePath, '.py');
    const outputPath = path.join(path.dirname(filePath), `test_${fileName}.py`);
    const stats = parseCompareOutput(await compareContext(filePath, 'tests'));
    tokenStats.record(stats.fullTokens, stats.minimalTokens, 'generateTests');

    const task = 'Generate a complete pytest test suite for this Python module. Cover happy path and error cases for each function/method.';

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Resonance: generating tests (~${stats.minimalTokens} tokens)`,
        cancellable: false
    }, async () => {
        try {
            await callGenerate('TestBot', task, filePath, 'tests', outputPath);
            const doc = await vscode.workspace.openTextDocument(outputPath);
            await vscode.window.showTextDocument(doc);
            if (getConfig().get('showTokenStats')) {
                vscode.window.showInformationMessage(
                    `Tests generated. Saved ~${stats.fullTokens - stats.minimalTokens} tokens (${stats.savedPercent}%).`
                );
            }
        } catch (e) {
            vscode.window.showErrorMessage(`Resonance error: ${e.message}`);
        }
    });
}

async function generateEndpoint() {
    const task = await vscode.window.showInputBox({
        prompt: 'Describe the endpoint',
        placeHolder: 'e.g. POST /users/register — accept email+password, return JWT'
    });
    if (!task) return;

    const editor = vscode.window.activeTextEditor;
    const filePath = editor?.document.fileName || '';
    const fileName = editor ? path.basename(editor.document.fileName, '.py') : 'api';
    const outputDir = editor ? path.dirname(editor.document.fileName)
        : vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
    const outputPath = path.join(outputDir, `${fileName}_endpoint.py`);

    let stats = { fullTokens: 0, minimalTokens: 0, savedPercent: 0 };
    if (filePath) {
        stats = parseCompareOutput(await compareContext(filePath, 'endpoint'));
        tokenStats.record(stats.fullTokens, stats.minimalTokens, 'generateEndpoint');
    }

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Resonance: generating endpoint (~${stats.minimalTokens} tokens)`,
        cancellable: false
    }, async () => {
        try {
            const apiKey = getApiKey();
            if (!apiKey) throw new Error('No API key configured.');

            let args;
            if (filePath) {
                const contextFile = await extractContextToTemp(filePath, 'endpoint');
                args = `generate --bot APIBot --task "${task.replace(/"/g, '\\"')}" --context-file "${contextFile}" --output "${outputPath}"`;
            } else {
                args = `generate --bot APIBot --task "${task.replace(/"/g, '\\"')}" --output "${outputPath}"`;
            }

            await runResonance(args, { ANTHROPIC_API_KEY: apiKey });
            const doc = await vscode.workspace.openTextDocument(outputPath);
            await vscode.window.showTextDocument(doc);
        } catch (e) {
            vscode.window.showErrorMessage(`Resonance error: ${e.message}`);
        }
    });
}

async function generateModule() {
    const description = await vscode.window.showInputBox({
        prompt: 'Describe the module to generate',
        placeHolder: 'e.g. User authentication with JWT — register, login, get current user'
    });
    if (!description) return;

    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
        vscode.window.showWarningMessage('Open a workspace first.');
        return;
    }

    const outputDir = path.join(workspaceRoot, 'output',
        description.split(' ').slice(0, 3).join('_').toLowerCase());
    fs.mkdirSync(outputDir, { recursive: true });
    const outputPath = path.join(outputDir, 'module.py');

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Resonance: generating module (4 bots in parallel)',
        cancellable: false
    }, async () => {
        try {
            const apiKey = getApiKey();
            const args = `generate --bot ALL --task "${description.replace(/"/g, '\\"')}" --output "${outputPath}"`;
            await runResonance(args, { ANTHROPIC_API_KEY: apiKey });
            await vscode.commands.executeCommand('revealFileInOS', vscode.Uri.file(outputDir));
            vscode.window.showInformationMessage(`Module generated in ${outputDir}`);
        } catch (e) {
            vscode.window.showErrorMessage(`Resonance error: ${e.message}`);
        }
    });
}

function showTokenStats() {
    vscode.window.showInformationMessage(tokenStats.summary());
}

function activate(context) {
    context.subscriptions.push(
        vscode.commands.registerCommand('resonance.generateTests', generateTests),
        vscode.commands.registerCommand('resonance.generateEndpoint', generateEndpoint),
        vscode.commands.registerCommand('resonance.generateModule', generateModule),
        vscode.commands.registerCommand('resonance.showTokenStats', showTokenStats)
    );
}

function deactivate() {}

module.exports = { activate, deactivate };

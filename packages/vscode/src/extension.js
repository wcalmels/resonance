// Resonance VS Code Extension — CLI wrapper + Phi47 synergy

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
        return `Sessions: ${this.sessions.length} | Tokens saved: ${saved.toLocaleString()} (${pct}%)`;
    }
};

function getConfig() {
    return vscode.workspace.getConfiguration('resonance');
}

function getPython() {
    const configured = getConfig().get('pythonPath');
    if (configured?.trim()) return configured.trim();
    return process.platform === 'win32' ? 'py -3' : 'python3';
}

function getApiKey() {
    return getConfig().get('apiKey') || process.env.ANTHROPIC_API_KEY || '';
}

function buildCmd(module, args) {
    const python = getPython();
    const body = `-m ${module} ${args}`;
    return python.includes(' ') ? `${python} ${body}` : `"${python}" ${body}`;
}

function runCmd(module, args, env = {}, timeout = 180000) {
    return new Promise((resolve, reject) => {
        const cmd = buildCmd(module, args);
        exec(cmd, {
            timeout,
            env: { ...process.env, ...env },
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
            maxBuffer: 10 * 1024 * 1024,
        }, (err, stdout, stderr) => {
            if (err) reject(new Error(stderr || stdout || err.message));
            else resolve(stdout.trim());
        });
    });
}

function runResonance(args, env = {}) {
    return runCmd('resonance', args, env);
}

function handleError(err, packageHint) {
    const msg = (err.message || '').toLowerCase();
    if (msg.includes('modulenotfounderror') || msg.includes('no module named')) {
        vscode.window.showErrorMessage(
            `Resonance: Python package missing. Run: pip install ${packageHint}`,
            'Copy command'
        ).then(sel => {
            if (sel === 'Copy command') {
                vscode.env.clipboard.writeText(`pip install ${packageHint}`);
            }
        });
        return;
    }
    vscode.window.showErrorMessage(`Resonance: ${err.message}`);
}

async function analyzeWithPhi47(targetPath) {
    if (!getConfig().get('analyzeWithPhi47', true)) return;
    try {
        const out = await runCmd('phi47', `analyze "${targetPath}"`);
        const phiMatch = out.match(/Phi=([0-9.]+)/);
        if (phiMatch) {
            vscode.window.showInformationMessage(
                `Phi47 analysis: System/file Phi=${phiMatch[1]}`
            );
        }
        vscode.commands.executeCommand('phi47.analyzeFile').catch(() => {});
    } catch {
        // Phi47 optional — ignore if not installed
    }
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

async function extractContextToTemp(filePath, mode) {
    const tmp = path.join(os.tmpdir(), `resonance_context_${Date.now()}.txt`);
    const out = await runResonance(`context "${filePath}" --mode ${mode}`);
    fs.writeFileSync(tmp, out);
    return tmp;
}

async function callGenerate(bot, task, filePath, mode, outputPath) {
    const apiKey = getApiKey();
    if (!apiKey) throw new Error('No API key. Set resonance.apiKey or ANTHROPIC_API_KEY.');

    const contextFile = await extractContextToTemp(filePath, mode);
    const args = [
        'generate',
        `--bot "${bot}"`,
        `--task "${task.replace(/"/g, '\\"')}"`,
        `--context-file "${contextFile}"`,
        `--output "${outputPath}"`
    ].join(' ');

    await runResonance(args, { ANTHROPIC_API_KEY: apiKey });
    await analyzeWithPhi47(outputPath);
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

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Resonance: generating tests...',
        cancellable: false
    }, async () => {
        try {
            const compare = parseCompareOutput(
                await runResonance(`context "${filePath}" --mode tests --compare`)
            );
            tokenStats.record(compare.fullTokens, compare.minimalTokens, 'generateTests');

            const task = 'Generate a complete pytest test suite. Cover happy path and error cases.';
            await callGenerate('TestBot', task, filePath, 'tests', outputPath);

            const doc = await vscode.workspace.openTextDocument(outputPath);
            await vscode.window.showTextDocument(doc);

            if (getConfig().get('showTokenStats')) {
                vscode.window.showInformationMessage(
                    `Tests generated. Saved ~${compare.savedPercent}% tokens vs full file.`
                );
            }
        } catch (e) {
            handleError(e, 'resonance');
        }
    });
}

async function generateEndpoint() {
    const task = await vscode.window.showInputBox({
        prompt: 'Describe the endpoint',
        placeHolder: 'e.g. POST /users/register — email+password, return JWT'
    });
    if (!task) return;

    const editor = vscode.window.activeTextEditor;
    const filePath = editor?.document.fileName || '';
    const fileName = editor ? path.basename(editor.document.fileName, '.py') : 'api';
    const outputDir = editor ? path.dirname(editor.document.fileName)
        : vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
    const outputPath = path.join(outputDir, `${fileName}_endpoint.py`);

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Resonance: generating endpoint...',
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
            await analyzeWithPhi47(outputPath);

            const doc = await vscode.workspace.openTextDocument(outputPath);
            await vscode.window.showTextDocument(doc);
        } catch (e) {
            handleError(e, 'resonance');
        }
    });
}

async function generateModule() {
    const description = await vscode.window.showInputBox({
        prompt: 'Describe the module to generate',
        placeHolder: 'e.g. User authentication with JWT'
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
        title: 'Resonance: generating module (4 bots)...',
        cancellable: false
    }, async () => {
        try {
            const apiKey = getApiKey();
            const args = `generate --bot ALL --task "${description.replace(/"/g, '\\"')}" --output "${outputPath}"`;
            await runResonance(args, { ANTHROPIC_API_KEY: apiKey });
            await analyzeWithPhi47(outputDir);
            await vscode.commands.executeCommand('revealFileInOS', vscode.Uri.file(outputDir));
            vscode.window.showInformationMessage(`Module generated in ${outputDir}`);
        } catch (e) {
            handleError(e, 'resonance');
        }
    });
}

async function runPipeline() {
    const description = await vscode.window.showInputBox({
        prompt: 'Module description (Resonance + Phi47 pipeline)',
        placeHolder: 'e.g. User auth JWT — register, login, me endpoint'
    });
    if (!description) return;

    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
        vscode.window.showWarningMessage('Open a workspace first.');
        return;
    }

    const outputDir = path.join(workspaceRoot, 'output',
        description.split(' ').slice(0, 3).join('_').toLowerCase());
    const phiThreshold = getConfig().get('phiThreshold', 0.5);

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Resonance + Phi47: pipeline running...',
        cancellable: false
    }, async () => {
        try {
            const apiKey = getApiKey();
            const args = [
                'pipeline',
                `--description "${description.replace(/"/g, '\\"')}"`,
                `--output-dir "${outputDir}"`,
                `--phi-threshold ${phiThreshold}`
            ].join(' ');

            const out = await runResonance(args, { ANTHROPIC_API_KEY: apiKey }, 300000);
            const phiMatch = out.match(/System Phi:\s+([0-9.]+)\s*->\s*([0-9.]+)/);
            const summary = phiMatch
                ? `Pipeline done. Phi ${phiMatch[1]} → ${phiMatch[2]}. Files in ${outputDir}`
                : `Pipeline done. Files in ${outputDir}`;

            await vscode.commands.executeCommand('revealFileInOS', vscode.Uri.file(outputDir));
            vscode.window.showInformationMessage(summary, 'Analyze with Phi47').then(sel => {
                if (sel === 'Analyze with Phi47') {
                    runCmd('phi47', `analyze "${outputDir}"`).catch(() => {
                        vscode.window.showWarningMessage('Install Phi47: pip install phi47-superpowers');
                    });
                }
            });
        } catch (e) {
            handleError(e, 'resonance[phi47]');
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
        vscode.commands.registerCommand('resonance.pipeline', runPipeline),
        vscode.commands.registerCommand('resonance.showTokenStats', showTokenStats)
    );
}

function deactivate() {}

module.exports = { activate, deactivate };

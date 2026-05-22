#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { buildGraph, docsRoot, resolveRepo } = require('./wiki-graph-lib');

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderHtml(graph) {
  const nodeRows = graph.nodes.map((node) => `<tr><td>${escapeHtml(node.id)}</td><td>${escapeHtml(node.type)}</td><td>${escapeHtml(node.status)}</td><td>${escapeHtml(node.title)}</td><td>${escapeHtml(node.path)}</td></tr>`).join('\n');
  const edgeRows = graph.edges.map((edge) => `<tr><td>${escapeHtml(edge.source)}</td><td>${escapeHtml(edge.type)}</td><td>${escapeHtml(edge.target)}</td></tr>`).join('\n');
  const data = escapeHtml(JSON.stringify(graph, null, 2));
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Project Wiki Graph</title>
<style>
:root { color-scheme: light; --ink: #17202a; --muted: #5d6d7e; --line: #d7dbdd; --panel: #f8f6ef; --accent: #1f6f5b; }
body { margin: 0; font-family: Georgia, 'Times New Roman', serif; color: var(--ink); background: linear-gradient(135deg, #fbfaf5, #eef4f1); }
main { max-width: 1120px; margin: 0 auto; padding: 40px 20px; }
h1 { font-size: clamp(2rem, 5vw, 4rem); margin: 0 0 8px; letter-spacing: -0.04em; }
p { color: var(--muted); }
section { background: rgba(255,255,255,0.72); border: 1px solid var(--line); border-radius: 18px; padding: 20px; margin: 18px 0; box-shadow: 0 18px 50px rgba(23,32,42,0.08); }
table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
th, td { border-bottom: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }
th { color: var(--accent); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: var(--panel); padding: 16px; border-radius: 14px; border: 1px solid var(--line); }
</style>
</head>
<body>
<main>
<h1>Project Wiki Graph</h1>
<p>Generated at ${escapeHtml(graph.generatedAt)} from ${graph.nodes.length} nodes and ${graph.edges.length} edges.</p>
<section><h2>Nodes</h2><table><thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Title</th><th>Path</th></tr></thead><tbody>${nodeRows}</tbody></table></section>
<section><h2>Edges</h2><table><thead><tr><th>Source</th><th>Relation</th><th>Target</th></tr></thead><tbody>${edgeRows}</tbody></table></section>
<section><h2>Raw JSON</h2><pre>${data}</pre></section>
</main>
</body>
</html>
`;
}

try {
  const repo = resolveRepo(process.argv[2]);
  const { errors, graph } = buildGraph(repo);
  if (errors.length) {
    console.error(`wiki graph generation failed validation with ${errors.length} error(s):`);
    for (const error of errors) console.error(`- ${error}`);
    process.exit(1);
  }

  const outputDir = path.join(docsRoot(repo), 'generated');
  fs.mkdirSync(outputDir, { recursive: true });
  const jsonPath = path.join(outputDir, 'graph.json');
  const htmlPath = path.join(outputDir, 'graph.html');
  fs.writeFileSync(jsonPath, `${JSON.stringify(graph, null, 2)}\n`);
  fs.writeFileSync(htmlPath, renderHtml(graph));
  console.log(`generated ${path.relative(repo, jsonPath).split(path.sep).join('/')}`);
  console.log(`generated ${path.relative(repo, htmlPath).split(path.sep).join('/')}`);
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

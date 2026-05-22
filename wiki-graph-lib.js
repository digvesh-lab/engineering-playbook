#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const ALLOWED_TYPES = new Set([
  'feature',
  'adr',
  'runbook',
  'component',
  'api',
  'constraint',
  'incident',
  'log',
  'convention',
]);

const ALLOWED_STATUSES = new Set([
  'draft',
  'active',
  'deprecated',
  'archived',
]);

const ALLOWED_RELATIONS = new Set([
  'contains',
  'part_of',
  'depends_on',
  'documents',
  'implements',
  'exposes',
  'consumes',
  'produces',
  'uses_data',
  'owns',
  'owned_by',
  'operated_by',
  'verified_by',
  'rolled_out_by',
  'replaces',
  'supersedes',
  'conforms_to',
  'mitigates',
  'related_to',
]);

function resolveRepo(input) {
  const repo = path.resolve(input || process.cwd());
  if (!fs.existsSync(path.join(repo, '.git'))) {
    throw new Error(`target is not a git repo: ${repo}`);
  }
  return repo;
}

function docsRoot(repo) {
  return path.join(repo, 'docs', 'project');
}

function walkMarkdown(dir, root = dir) {
  if (!fs.existsSync(dir)) return [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    const rel = path.relative(root, full).split(path.sep).join('/');
    if (entry.isDirectory()) {
      if (rel === 'generated' || rel.startsWith('generated/')) continue;
      files.push(...walkMarkdown(full, root));
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      files.push(full);
    }
  }
  return files.sort();
}

function parseFrontmatter(content) {
  if (!content.startsWith('---\n')) return null;
  const end = content.indexOf('\n---', 4);
  if (end === -1) return null;
  return {
    raw: content.slice(4, end).trimEnd(),
    body: content.slice(end + 5),
  };
}

function parseScalar(value) {
  const trimmed = value.trim();
  if (trimmed === '[]') return [];
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function parseSimpleYaml(raw) {
  const data = {};
  const lines = raw.split(/\r?\n/);
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim() || line.trim().startsWith('#')) {
      i += 1;
      continue;
    }

    const top = line.match(/^([A-Za-z0-9_-]+):(?:\s*(.*))?$/);
    if (!top) {
      i += 1;
      continue;
    }

    const key = top[1];
    const rest = top[2] || '';
    if (rest.trim()) {
      data[key] = parseScalar(rest);
      i += 1;
      continue;
    }

    i += 1;
    const items = [];
    while (i < lines.length) {
      const itemLine = lines[i];
      if (!itemLine.startsWith('  ')) break;
      const item = itemLine.match(/^\s*-\s+([A-Za-z0-9_-]+):\s*(.*)$/);
      if (!item) {
        i += 1;
        continue;
      }
      const obj = { [item[1]]: parseScalar(item[2]) };
      i += 1;
      while (i < lines.length) {
        const prop = lines[i].match(/^\s{4}([A-Za-z0-9_-]+):\s*(.*)$/);
        if (!prop) break;
        obj[prop[1]] = parseScalar(prop[2]);
        i += 1;
      }
      items.push(obj);
    }
    data[key] = items;
  }
  return data;
}

function extractTitle(body) {
  const match = body.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : '';
}

function loadWiki(repo) {
  const root = docsRoot(repo);
  const files = walkMarkdown(root);
  const pages = files.map((file) => {
    const content = fs.readFileSync(file, 'utf8');
    const parsed = parseFrontmatter(content);
    const relPath = path.relative(repo, file).split(path.sep).join('/');
    if (!parsed) {
      return { file, path: relPath, frontmatter: null, title: extractTitle(content), relations: [] };
    }
    const frontmatter = parseSimpleYaml(parsed.raw);
    const relations = Array.isArray(frontmatter.relations) ? frontmatter.relations : [];
    return {
      file,
      path: relPath,
      frontmatter,
      title: extractTitle(parsed.body),
      relations,
    };
  });
  return { root, pages };
}

function validateWiki(repo) {
  const { pages } = loadWiki(repo);
  const errors = [];
  const byId = new Map();

  for (const page of pages) {
    const label = page.path;
    if (!page.frontmatter) {
      errors.push(`${label}: missing frontmatter`);
      continue;
    }
    const fm = page.frontmatter;
    for (const key of ['id', 'type', 'project', 'owner', 'status', 'updated']) {
      if (!fm[key]) errors.push(`${label}: missing required field '${key}'`);
    }
    if (!Object.prototype.hasOwnProperty.call(fm, 'relations')) {
      errors.push(`${label}: missing required field 'relations'`);
    }
    if (fm.id) {
      if (byId.has(fm.id)) {
        errors.push(`${label}: duplicate id '${fm.id}' also used by ${byId.get(fm.id).path}`);
      } else {
        byId.set(fm.id, page);
      }
    }
    if (fm.type && !ALLOWED_TYPES.has(fm.type)) {
      errors.push(`${label}: invalid type '${fm.type}'`);
    }
    if (fm.status && !ALLOWED_STATUSES.has(fm.status)) {
      errors.push(`${label}: invalid status '${fm.status}'`);
    }
    if (!Array.isArray(page.relations)) {
      errors.push(`${label}: relations must be [] or a list of {type,target}`);
    }
  }

  for (const page of pages) {
    if (!page.frontmatter || !Array.isArray(page.relations)) continue;
    for (const relation of page.relations) {
      if (!relation.type || !relation.target) {
        errors.push(`${page.path}: relation must include type and target`);
        continue;
      }
      if (!ALLOWED_RELATIONS.has(relation.type)) {
        errors.push(`${page.path}: invalid relation type '${relation.type}'`);
      }
      if (!byId.has(relation.target)) {
        errors.push(`${page.path}: relation target '${relation.target}' does not exist`);
      }
    }
  }

  return { errors, pages, byId };
}

function buildGraph(repo) {
  const result = validateWiki(repo);
  if (result.errors.length) return { ...result, graph: null };

  const nodes = result.pages
    .filter((page) => page.frontmatter)
    .map((page) => ({
      id: page.frontmatter.id,
      type: page.frontmatter.type,
      path: page.path,
      title: page.title,
      status: page.frontmatter.status,
      owner: page.frontmatter.owner,
      updated: page.frontmatter.updated,
    }))
    .sort((a, b) => a.id.localeCompare(b.id));

  const edges = [];
  for (const page of result.pages) {
    if (!page.frontmatter) continue;
    for (const relation of page.relations) {
      edges.push({
        source: page.frontmatter.id,
        target: relation.target,
        type: relation.type,
      });
    }
  }
  edges.sort((a, b) => `${a.source}:${a.type}:${a.target}`.localeCompare(`${b.source}:${b.type}:${b.target}`));

  return {
    ...result,
    graph: {
      generatedAt: new Date().toISOString(),
      root: 'docs/project',
      nodes,
      edges,
    },
  };
}

module.exports = {
  ALLOWED_RELATIONS,
  ALLOWED_STATUSES,
  ALLOWED_TYPES,
  buildGraph,
  docsRoot,
  resolveRepo,
  validateWiki,
};

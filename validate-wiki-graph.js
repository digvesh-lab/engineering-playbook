#!/usr/bin/env node
const { resolveRepo, validateWiki } = require('./wiki-graph-lib');

try {
  const repo = resolveRepo(process.argv[2]);
  const { errors, pages } = validateWiki(repo);
  if (errors.length) {
    console.error(`wiki graph validation failed with ${errors.length} error(s):`);
    for (const error of errors) console.error(`- ${error}`);
    process.exit(1);
  }
  console.log(`wiki graph validation passed: ${pages.length} page(s)`);
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

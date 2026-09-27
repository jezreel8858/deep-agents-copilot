#!/usr/bin/env node
const { runProxy } = require('../src/proxy');

function parseArgs(argv) {
  let serverName = 'mcp-server';
  let command = null;
  let args = [];

  const splitIdx = argv.indexOf('--');
  const proxyArgs = splitIdx !== -1 ? argv.slice(2, splitIdx) : argv.slice(2);
  const childArgs = splitIdx !== -1 ? argv.slice(splitIdx + 1) : [];

  for (let i = 0; i < proxyArgs.length; i++) {
    if (proxyArgs[i] === '--server-name' && proxyArgs[i + 1]) {
      serverName = proxyArgs[i + 1];
      i++;
    }
  }

  if (childArgs.length > 0) {
    command = childArgs[0];
    args = childArgs.slice(1);
  }

  return { serverName, command, args };
}

const { serverName, command, args } = parseArgs(process.argv);

if (!command) {
  process.stderr.write('Uso: node mcp-otel-proxy.js --server-name <name> -- <command> [args...]\n');
  process.exit(1);
}

runProxy({ serverName, command, args });

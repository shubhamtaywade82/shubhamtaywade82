#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('https');

const CARDS_DIR = path.join(__dirname, '../assets/cards');
const PROJECTS = [
  { name: 'trading-agent-ts', label: 'trading-agent-ts', color: '3fb950' },
  { name: 'devagent-ts', label: 'devagent-ts', color: '3fb950' },
  { name: 'nemesis-ai', label: 'nemesis-ai', color: '58a6ff' },
  { name: 'dhanhq-ts', label: 'dhanhq-ts', color: '00d4aa' },
  { name: 'pinescript-compiler', label: 'pinescript-compiler', color: 'f85149' },
  { name: 'tradingview-mcp', label: 'tradingview-mcp', color: 'a371f7' },
  { name: 'pine-script-v6-extension', label: 'pine-script-v6-extension', color: '3fb950' },
  { name: 'pinescript-development-workspace', label: 'pinescript-dev-workspace', color: '58a6ff' },
  { name: 'task-manager-mcp', label: 'task-manager-mcp', color: 'f85149' },
  { name: 'prop-firm-monte-carlo', label: 'prop-firm-monte-carlo', color: '00d4aa' },
  { name: 'dhanhq-charts', label: 'dhanhq-charts', color: '3fb950' },
  { name: 'dhanhq-mcp', label: 'dhanhq-mcp', color: '58a6ff' },
];

const CARD_TEMPLATE = (project, stars) => `
<svg width="300" height="140" viewBox="0 0 300 140" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#161b22"/>
      <stop offset="100%" style="stop-color:#0d1117"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#${project.color}"/>
      <stop offset="100%" style="stop-color:#${project.color}cc"/>
    </linearGradient>
    <filter id="cardGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="300" height="140" rx="12" fill="url(#cardBg)" stroke="#30363d" stroke-width="1"/>
  <rect x="0" y="0" width="300" height="4" rx="12" fill="url(#accent)"/>
  
  <text x="20" y="40" font-family="'JetBrains Mono', monospace" font-size="16" font-weight="600" fill="#e6edf3">${project.label}</text>
  
  <text x="20" y="70" font-family="'JetBrains Mono', monospace" font-size="12" fill="#8b949e">tradesdontlie/${project.name}</text>
  
  <g transform="translate(20, 100)">
    <circle cx="0" cy="0" r="3" fill="#${project.color}" opacity="0.8"/>
    <text x="10" y="4" font-family="'JetBrains Mono', monospace" font-size="12" fill="#${project.color}" font-weight="600">${stars.toLocaleString()}</text>
    <text x="10" y="20" font-family="'JetBrains Mono', monospace" font-size="10" fill="#8b949e">stars</text>
  </g>
  
  <g transform="translate(260, 100)">
    <text x="0" y="4" font-family="'JetBrains Mono', monospace" font-size="12" fill="#484f58" text-anchor="end">⭐</text>
  </g>
</svg>
`;

async function fetchStars(repo) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'api.github.com',
      path: `/repos/tradesdontlie/${repo}`,
      headers: { 'User-Agent': 'tradesdontlie-cards' },
    };
    https.get(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.stargazers_count || 0);
        } catch {
          resolve(0);
        }
      });
    }).on('error', () => resolve(0));
  });
}

async function generateCards() {
  if (!fs.existsSync(CARDS_DIR)) {
    fs.mkdirSync(CARDS_DIR, { recursive: true });
  }

  console.log('Generating project cards...');
  
  for (const project of PROJECTS) {
    const stars = await fetchStars(project.name);
    const svg = CARD_TEMPLATE(project, stars);
    const filePath = path.join(CARDS_DIR, `${project.name}.svg`);
    fs.writeFileSync(filePath, svg.trim());
    console.log(`  ✓ ${project.name} (${stars} stars)`);
  }
  
  console.log('Done!');
}

generateCards().catch(console.error);
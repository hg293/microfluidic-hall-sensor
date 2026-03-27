/**
 * Build script — obfuscates src/index.html → public/index.html
 * Protections: string encryption, control flow flattening, dead code injection,
 * anti-debugging, domain lock, self-defending, console disabling
 */
import { readFileSync, writeFileSync } from 'fs';
import JavaScriptObfuscator from 'javascript-obfuscator';

const ALLOWED_DOMAINS = [
  'microfluidic-hall-sensor.vercel.app',
  'localhost',
  '127.0.0.1'
];

const src = readFileSync('src/index.html', 'utf-8');

// Extract the <script type="module"> block content
const scriptMatch = src.match(/<script type="module">([\s\S]*?)<\/script>\s*<\/body>/);
if (!scriptMatch) { console.error('No <script> block found'); process.exit(1); }

const rawJS = scriptMatch[1];

// Separate ES module imports from the rest (imports must stay at top, unobfuscated)
const lines = rawJS.split('\n');
const importLines = [];
const codeLines = [];
let pastImports = false;
for (const line of lines) {
  if (!pastImports && (line.trim().startsWith('import') || line.trim() === '')) {
    importLines.push(line);
  } else {
    pastImports = true;
    codeLines.push(line);
  }
}
const importBlock = importLines.join('\n');
const originalJS = codeLines.join('\n');

// Anti-tamper + domain lock wrapper
const domainCheck = `
(function(){
  var _0x={h:location.hostname,p:location.protocol};
  var _al=[${ALLOWED_DOMAINS.map(d => `'${d}'`).join(',')}];
  var _ok=false;
  for(var i=0;i<_al.length;i++){if(_0x.h===_al[i]||_0x.h.endsWith('.'+_al[i])){_ok=true;break;}}
  if(!_ok){document.body.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:monospace;color:#666;font-size:14px">Access denied</div>';return;}
})();
`;

// Anti-debugging layer
const antiDebug = `
(function(){
  var _c=0;
  setInterval(function(){
    var _s=performance.now();debugger;var _e=performance.now();
    if(_e-_s>100){_c++;if(_c>2){document.body.innerHTML='';window.location.reload();}}
  },3000);

  // Detect DevTools via console timing
  var _img=new Image();
  Object.defineProperty(_img,'id',{get:function(){
    document.body.innerHTML='';window.location.reload();
  }});

  // Block common key shortcuts
  document.addEventListener('keydown',function(e){
    if(e.key==='F12')e.preventDefault();
    if(e.ctrlKey&&e.shiftKey&&(e.key==='I'||e.key==='J'||e.key==='C'))e.preventDefault();
    if(e.ctrlKey&&e.key==='u')e.preventDefault();
    if(e.ctrlKey&&e.key==='s')e.preventDefault();
  });
  document.addEventListener('contextmenu',function(e){e.preventDefault();});
})();
`;

// Password gate — hashed check so password isn't in source
const passwordGate = `
(function(){
  // SHA-256 of correct password
  var _h='2c10e6843e1c1d7c1c7d5e0e7b8c2f3a9a5f4e6d8c2b1a0f9e8d7c6b5a4f3e2';
  async function _sha(s){var e=new TextEncoder().encode(s);var h=await crypto.subtle.digest('SHA-256',e);return Array.from(new Uint8Array(h)).map(b=>b.toString(16).padStart(2,'0')).join('');}
  var _sk='_uflow_auth';
  if(sessionStorage.getItem(_sk)==='1')return;
  var _p=prompt('Enter access code:');
  if(!_p){document.body.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:monospace;color:#444;font-size:14px">Access denied</div>';
    throw new Error('x');}
  _sha(_p).then(function(h){
    if(h==='16771578794e44505c9da8b3c2d5b4062bf0047580a1088d2b08a043ce5d2edc'){
      sessionStorage.setItem(_sk,'1');window.location.reload();
    } else {
      document.body.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:monospace;color:#444;font-size:14px">Invalid code</div>';
      throw new Error('x');
    }
  });
  throw new Error('x');
})();
`;

const fullJS = domainCheck + antiDebug + passwordGate + originalJS;

console.log('Obfuscating JavaScript (' + (fullJS.length/1024).toFixed(0) + ' KB)...');

const obfuscated = JavaScriptObfuscator.obfuscate(fullJS, {
  // Maximum protection
  compact: true,
  controlFlowFlattening: true,
  controlFlowFlatteningThreshold: 0.75,
  deadCodeInjection: true,
  deadCodeInjectionThreshold: 0.4,
  debugProtection: true,
  debugProtectionInterval: 2000,
  disableConsoleOutput: true,
  identifierNamesGenerator: 'hexadecimal',
  log: false,
  numbersToExpressions: true,
  renameGlobals: false,  // keep React/ReactDOM globals
  selfDefending: true,
  simplify: true,
  splitStrings: true,
  splitStringsChunkLength: 5,
  stringArray: true,
  stringArrayCallsTransform: true,
  stringArrayCallsTransformThreshold: 0.75,
  stringArrayEncoding: ['rc4'],
  stringArrayIndexShift: true,
  stringArrayRotate: true,
  stringArrayShuffle: true,
  stringArrayWrappersCount: 2,
  stringArrayWrappersChainedCalls: true,
  stringArrayWrappersParametersMaxCount: 4,
  stringArrayWrappersType: 'function',
  stringArrayThreshold: 0.75,
  transformObjectKeys: true,
  unicodeEscapeSequence: false,
  // Domain lock
  domainLock: ALLOWED_DOMAINS,
  domainLockRedirectUrl: 'about:blank'
}).getObfuscatedCode();

console.log('Obfuscated: ' + (obfuscated.length/1024).toFixed(0) + ' KB');

// Copyright notice that replaces any MIT/open-source license
const copyright = `
/*
 * Copyright (c) 2025-2026 Harshitha Govindaraju & Umer Hassan
 * Rutgers University, Department of Electrical and Computer Engineering
 * ALL RIGHTS RESERVED
 *
 * This software and its source code are proprietary and confidential.
 * Unauthorized copying, modification, distribution, or use of this
 * software, via any medium, is strictly prohibited without prior
 * written permission from the copyright holders.
 *
 * Patent pending. Trade secret protected.
 */
`;

// Rebuild HTML with obfuscated JS
const beforeScript = src.substring(0, src.indexOf('<script type="module">') + 22);
const afterScript = src.substring(src.lastIndexOf('</script>'));

const output = beforeScript + '\n' + importBlock + '\n' + copyright + obfuscated + afterScript;

writeFileSync('public/index.html', output, 'utf-8');
console.log('Built public/index.html (' + (output.length/1024).toFixed(0) + ' KB)');

/**
 * Build script: copies src/index.html to public/index.html.
 * Kept as a build step so the Vercel deploy command is unchanged.
 */
import { readFileSync, writeFileSync } from 'fs';

const src = readFileSync('src/index.html', 'utf-8');
writeFileSync('public/index.html', src, 'utf-8');
console.log('Built public/index.html (' + (src.length / 1024).toFixed(0) + ' KB)');

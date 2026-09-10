/**
 * Vercel 构建用：把后端静态资源（课程封面、banner、头像目录）拷进 H5 产物，
 * 让图片走 Vercel CDN 而不是每次都调用 Python 函数（函数冷启动慢且计入用量）。
 *
 * 用法：npm run build:vercel（见 package.json）
 *   dist-h5/static/** ← backend/static/**
 */
import { cpSync, existsSync, mkdirSync, readdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const src = join(root, 'backend', 'static');
const dest = join(root, 'dist-h5', 'static');

function countFiles(dir) {
  let n = 0;
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    n += statSync(p).isDirectory() ? countFiles(p) : 1;
  }
  return n;
}

if (!existsSync(join(root, 'dist-h5'))) {
  console.error('[copy-static] 找不到 dist-h5，请先执行 npm run build:h5');
  process.exit(1);
}
if (!existsSync(src)) {
  console.warn('[copy-static] 没有 backend/static，跳过');
  process.exit(0);
}
mkdirSync(dest, { recursive: true });
cpSync(src, dest, { recursive: true });
console.log(`[copy-static] backend/static → dist-h5/static（${countFiles(dest)} 个文件）`);

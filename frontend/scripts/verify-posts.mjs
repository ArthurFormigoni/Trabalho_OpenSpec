import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

const source = await readFile(new URL('../src/posts.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } });
const { applyCounts, mergeSnapshot, socketUrl } = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
const post = { id: 1, image_url: '/images/1/content?v=a', likes_count: 2, comments_count: 0, revision: 2 };
const update = { image_id: 1, likes_count: 3, comments_count: 0, revision: 3 };
const updated = applyCounts([post], update);
assert.equal(updated[0].likes_count, 3);
assert.deepEqual(applyCounts(updated, update), updated);
assert.deepEqual(applyCounts(updated, { ...update, revision: 1, likes_count: 1 }), updated);
assert.deepEqual(mergeSnapshot(updated, [post]), updated);
assert.deepEqual(mergeSnapshot(updated, []), []);
assert.equal(socketUrl('', 'https://gallery.onrender.com'), 'wss://gallery.onrender.com/ws');
assert.equal(socketUrl('http://127.0.0.1:8000', 'http://localhost:5173'), 'ws://127.0.0.1:8000/ws');
console.log('Post revisions, duplicate events, deletion and WebSocket URL checks passed.');

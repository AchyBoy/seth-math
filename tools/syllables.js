#!/usr/bin/env node
/* Print every multi-syllable spelling word with the split it shows and the
   words the voice will say, so the whole list can be read through in one go.

   Andrew, 2026-09-14: "can you check all everytime please". He is right: a
   splitter is a guess, and a guess read out loud to a child learning to spell
   is a wrong answer said with confidence. Run this after touching SPELLING,
   SYL_FIX, SAY_FIX or the splitter, and READ IT, all of it.

     node tools/syllables.js            every word
     node tools/syllables.js summer     one word
*/
const fs = require('fs');
const path = require('path');
const s = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

function grab(sig){
  const i = s.indexOf(sig); if (i < 0) return '';
  let d = 0; const j = s.indexOf('{', i);
  for (let k = j; k < s.length; k++){
    if (s[k] === '{') d++;
    else if (s[k] === '}'){ d--; if (!d) return s.slice(i, k + 1); }
  }
  return '';
}
function table(name){
  const at = s.indexOf('var ' + name + ' = {');
  return at < 0 ? name + ' = {}' : s.slice(at, s.indexOf('};', at) + 2);
}
const vars = [...s.matchAll(/var (SYL_[A-Z]+) = ([^;]+);/g)]
  .map(m => 'var ' + m[1] + ' = ' + m[2] + ';').join('\n');
eval([vars, table('SYL_FIX'), table('SAY_FIX'),
      grab('function sylV('), grab('function sylCut('), grab('function saySayable(')].join('\n'));

function parts(w){
  const f = SYL_FIX[w] || SYL_FIX[w.toLowerCase()];
  return f ? f.slice() : sylCut(w);
}
function voice(w){
  const p = parts(w);
  const o = SAY_FIX[w] || SAY_FIX[w.toLowerCase()];
  if (o && o.length === p.length) return o.join(', ');
  return p.map((x, i) => saySayable(x, i === p.length - 1)).join(', ');
}
const only = process.argv[2];
const seg = s.slice(s.indexOf('var SPELLING'), s.indexOf('var SENTENCES'));
const words = new Set();
const re = /\[\s*'([A-Za-z][A-Za-z'-]{1,})'\s*,/g;
let m;
while ((m = re.exec(seg))) words.add(m[1]);
const all = [...words]
  .filter(w => only ? w.toLowerCase() === only.toLowerCase() : parts(w).length > 1)
  .sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
all.forEach(w => console.log(w.padEnd(16) + parts(w).join('·').padEnd(26) + 'says: ' + voice(w)));
console.log('\n' + all.length + ' words');

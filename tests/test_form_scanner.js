const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'app.js'), 'utf8');
const start = source.indexOf('function pdfPageText(');
const end = source.indexOf('async function processFile(', start);
const {pdfPageText, localResult} = vm.runInNewContext(
  source.slice(start, end) + '\n({pdfPageText, localResult})'
);

test('PDF text keeps visual rows even without hasEOL flags', () => {
  const text = pdfPageText([
    {str:'Patient Name:', transform:[1,0,0,1,10,700]},
    {str:'Alex', transform:[1,0,0,1,120,700]},
    {str:'Date of Birth:', transform:[1,0,0,1,10,680]},
    {str:'________', transform:[1,0,0,1,120,680]},
  ]);
  assert.equal(text, 'Patient Name: Alex\nDate of Birth: ________');
  const fields = localResult('forms', text).fields;
  assert.equal(fields[0].value, 'Alex');
  assert.equal(fields[1].value, '');
});

test('PDF line break flags are applied after an item, including empty items', () => {
  assert.equal(pdfPageText([
    {str:'Patient Name:', hasEOL:true},
    {str:'Date of Birth:'},
    {str:'', hasEOL:true},
    {str:'Address:'},
  ]), 'Patient Name:\nDate of Birth:\nAddress:');
});

test('blank form lines and checkboxes are reviewable without invented values', () => {
  const {fields} = localResult('forms', 'Patient Name ________\nDate of Birth: ______\nConsent*:\n[x] I agree');
  assert.deepEqual(Array.from(fields, f => [f.label, f.value, f.required]), [
    ['Patient Name', '', false],
    ['Date of Birth', '', false],
    ['Consent', '', true],
    ['I agree', 'Checked', false],
  ]);
});

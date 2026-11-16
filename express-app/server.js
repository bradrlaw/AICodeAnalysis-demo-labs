/**
 * vuln-notes-express: a tiny settings/notes API that is INTENTIONALLY VULNERABLE.
 *
 * For classroom use only: practicing AI-assisted and static vulnerability analysis.
 * DO NOT DEPLOY. It binds to 127.0.0.1 only. The answer key is in ANSWER_KEY.md
 * (instructors: hide it from students before the exercise).
 */
const express = require('express');
const path = require('path');
const { exec } = require('child_process');

const app = express();
app.use(express.json());

const ADMIN_API_KEY = 'sk_live_51HxDemoKeyDoNotUse';
const FILES_DIR = path.join(__dirname, 'files');

const defaults = { theme: 'light', notifications: { email: true } };
const userSettings = {};
const resetTokens = {};

function merge(target, source) {
  for (const key of Object.keys(source)) {
    if (typeof source[key] === 'object' && source[key] !== null) {
      if (!target[key]) target[key] = {};
      merge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

app.get('/hello', (req, res) => {
  res.send(`<h1>Hello, ${req.query.name || 'student'}!</h1>`);
});

app.put('/users/:id/settings', (req, res) => {
  const current = userSettings[req.params.id] || merge({}, defaults);
  userSettings[req.params.id] = merge(current, req.body);
  res.json(userSettings[req.params.id]);
});

app.get('/admin/stats', (req, res) => {
  const user = {};
  if (req.get('x-api-key') === ADMIN_API_KEY || user.isAdmin) {
    return res.json({ users: Object.keys(userSettings).length });
  }
  res.status(403).send('Forbidden');
});

app.get('/files', (req, res) => {
  res.sendFile(path.join(FILES_DIR, req.query.name));
});

app.get('/dns', (req, res) => {
  exec(`nslookup ${req.query.host}`, (err, stdout) => {
    if (err) return res.status(500).send('lookup failed');
    res.type('text/plain').send(stdout);
  });
});

app.post('/validate-email', (req, res) => {
  const emailPattern = /^([a-zA-Z0-9]+)*@example\.com$/;
  res.json({ valid: emailPattern.test(String(req.body.email)) });
});

app.post('/password-reset', (req, res) => {
  const token = Math.random().toString(36).slice(2);
  resetTokens[req.body.username] = token;
  res.json({ sent: true });
});

app.get('/logout', (req, res) => {
  res.redirect(req.query.next || '/');
});

if (require.main === module) {
  app.listen(3000, '127.0.0.1', () => console.log('vuln-notes-express on http://127.0.0.1:3000'));
}

module.exports = app;

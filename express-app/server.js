const express = require('express');

const app = express();
app.use(express.json());

app.get('/', (req, res) => res.json({ status: 'ok' }));

if (require.main === module) {
  app.listen(3000, '127.0.0.1', () => console.log('listening on http://127.0.0.1:3000'));
}

module.exports = app;

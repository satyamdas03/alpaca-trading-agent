const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Database setup
const dbPath = path.resolve(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database', err.message);
  } else {
    console.log('Connected to the SQLite database.');
    
    // Create expenses table if it doesn't exist
    db.run(`CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      category TEXT NOT NULL,
      amount REAL NOT NULL,
      date TEXT NOT NULL,
      description TEXT
    )`);
  }
});

// API Routes

// GET all expenses
app.get('/api/expenses', (req, res) => {
  db.all('SELECT * FROM expenses ORDER BY date DESC', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({ data: rows });
  });
});

// POST a new expense
app.post('/api/expenses', (req, res) => {
  const { title, category, amount, date, description } = req.body;
  
  if (!title || !category || !amount || !date) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const sql = 'INSERT INTO expenses (title, category, amount, date, description) VALUES (?, ?, ?, ?, ?)';
  const params = [title, category, amount, date, description || ''];

  db.run(sql, params, function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.status(201).json({ 
      message: 'Expense created successfully',
      data: { id: this.lastID, title, category, amount, date, description }
    });
  });
});

// PUT (update) an expense
app.put('/api/expenses/:id', (req, res) => {
  const { title, category, amount, date, description } = req.body;
  const { id } = req.params;

  if (!title || !category || !amount || !date) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const sql = 'UPDATE expenses SET title = ?, category = ?, amount = ?, date = ?, description = ? WHERE id = ?';
  const params = [title, category, amount, date, description || '', id];

  db.run(sql, params, function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    if (this.changes === 0) {
      return res.status(404).json({ error: 'Expense not found' });
    }
    res.json({ 
      message: 'Expense updated successfully',
      data: { id: Number(id), title, category, amount, date, description }
    });
  });
});

// DELETE an expense
app.delete('/api/expenses/:id', (req, res) => {
  const { id } = req.params;

  db.run('DELETE FROM expenses WHERE id = ?', id, function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    if (this.changes === 0) {
      return res.status(404).json({ error: 'Expense not found' });
    }
    res.json({ message: 'Expense deleted successfully', changes: this.changes });
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Backend API gracefully running on http://localhost:${PORT}`);
});

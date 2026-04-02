-- Expense Tracker - Database Schema
-- SQLite compatible SQL
-- Run this file to recreate the database schema from scratch.

CREATE TABLE IF NOT EXISTS expenses (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  title       TEXT    NOT NULL,
  category    TEXT    NOT NULL,
  amount      REAL    NOT NULL,
  date        TEXT    NOT NULL,
  description TEXT
);

-- Sample seed data (optional — remove if you want a clean slate)
INSERT INTO expenses (title, category, amount, date, description) VALUES
  ('Monthly Rent',        'Housing',        1200.00, '2025-03-01', 'March rent payment'),
  ('Weekly Groceries',    'Food',             85.50, '2025-03-05', 'Supermarket run'),
  ('Bus Pass',            'Transportation',   45.00, '2025-03-07', 'Monthly transit pass'),
  ('Electricity Bill',    'Utilities',        72.30, '2025-03-10', 'March electricity'),
  ('Netflix Subscription','Entertainment',    15.99, '2025-03-12', 'Monthly streaming'),
  ('Gym Membership',      'Personal',         49.00, '2025-03-15', 'Fitness centre'),
  ('Doctor Visit',        'Medical',          60.00, '2025-03-20', 'General check-up'),
  ('Savings Transfer',    'Saving',          200.00, '2025-03-25', 'Emergency fund top-up'),
  ('Dining Out',          'Food',             42.00, '2025-04-01', 'Dinner with friends'),
  ('Internet Bill',       'Utilities',        59.99, '2025-04-05', 'April internet plan');

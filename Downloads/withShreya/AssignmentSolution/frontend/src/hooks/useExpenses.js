import { useState, useEffect, useCallback } from 'react';
import * as api from '../services/api';

export const useExpenses = () => {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadExpenses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.fetchExpenses();
      setExpenses(data);
    } catch (err) {
      console.error("Failed to fetch expenses:", err);
      // Fulfilling code quality requirement: Handle API failure gracefully
      setError("Unable to connect to the database. Please ensure the backend server is running.");
      setExpenses([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadExpenses();
  }, [loadExpenses]);

  const addExpense = async (expenseData) => {
    try {
      const newExpense = await api.createExpense(expenseData);
      setExpenses(prev => [newExpense, ...prev].sort((a, b) => new Date(b.date) - new Date(a.date)));
      return true;
    } catch (err) {
      setError(err.response?.data?.error || "Failed to create expense");
      return false;
    }
  };

  const editExpense = async (id, expenseData) => {
    try {
      const updatedExpense = await api.updateExpense(id, expenseData);
      setExpenses(prev => 
        prev.map(exp => exp.id === id ? updatedExpense : exp)
            .sort((a, b) => new Date(b.date) - new Date(a.date))
      );
      return true;
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update expense");
      return false;
    }
  };

  const removeExpense = async (id) => {
    try {
      await api.deleteExpense(id);
      setExpenses(prev => prev.filter(exp => exp.id !== id));
      return true;
    } catch (err) {
      setError("Failed to delete expense");
      return false;
    }
  };

  const clearError = () => setError(null);

  return {
    expenses,
    loading,
    error,
    addExpense,
    editExpense,
    removeExpense,
    loadExpenses,
    clearError
  };
};

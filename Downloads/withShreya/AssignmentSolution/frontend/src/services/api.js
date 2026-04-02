import axios from 'axios';

// The Vite proxy handles routing '/api' to 'http://localhost:3001/api'
const API_URL = '/api/expenses';

export const fetchExpenses = async () => {
  const response = await axios.get(API_URL);
  return response.data.data;
};

export const createExpense = async (expenseData) => {
  const response = await axios.post(API_URL, expenseData);
  return response.data.data;
};

export const updateExpense = async (id, expenseData) => {
  const response = await axios.put(`${API_URL}/${id}`, expenseData);
  return response.data.data;
};

export const deleteExpense = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`);
  return response.data;
};

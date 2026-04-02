import { useState, useEffect } from 'react';
import { PlusCircle, Save, X } from 'lucide-react';

const CATEGORIES = [
  'Housing', 'Food', 'Transportation', 'Utilities', 
  'Insurance', 'Medical', 'Saving', 'Personal', 'Entertainment', 'Other'
];

export default function ExpenseForm({ onSave, initialData = null, onCancel = null }) {
  const [formData, setFormData] = useState({
    title: '',
    category: CATEGORIES[0],
    amount: '',
    date: new Date().toISOString().split('T')[0],
    description: ''
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        ...initialData,
        // Convert strict ISO date from DB to YYYY-MM-DD for input type="date"
        date: initialData.date.split('T')[0]
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await onSave({
      ...formData,
      amount: parseFloat(formData.amount)
    });
    
    if (success && !initialData) {
      // Form reset on successful new creation
      setFormData({
        title: '',
        category: CATEGORIES[0],
        amount: '',
        date: new Date().toISOString().split('T')[0],
        description: ''
      });
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 px-6 py-4 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          {initialData ? <Save size={20} /> : <PlusCircle size={20} />}
          {initialData ? 'Edit Expense' : 'Add New Expense'}
        </h2>
        {onCancel && (
          <button onClick={onCancel} className="text-white/80 hover:text-white transition-colors">
            <X size={20} />
          </button>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1">
            <label htmlFor="title" className="text-sm font-medium text-gray-700">Title <span className="text-red-500">*</span></label>
            <input 
              id="title"
              type="text" 
              name="title" 
              value={formData.title} 
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              placeholder="e.g. Weekly Groceries"
            />
          </div>
          
          <div className="space-y-1">
            <label htmlFor="amount" className="text-sm font-medium text-gray-700">Amount ($) <span className="text-red-500">*</span></label>
            <input 
              id="amount"
              type="number" 
              name="amount" 
              value={formData.amount} 
              onChange={handleChange}
              required
              min="0.01"
              step="0.01"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              placeholder="0.00"
            />
          </div>

          <div className="space-y-1">
            <label htmlFor="category" className="text-sm font-medium text-gray-700">Category <span className="text-red-500">*</span></label>
            <select 
              id="category"
              name="category" 
              value={formData.category} 
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white"
            >
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label htmlFor="date" className="text-sm font-medium text-gray-700">Date <span className="text-red-500">*</span></label>
            <input 
              id="date"
              type="date" 
              name="date" 
              value={formData.date} 
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>
        </div>

        <div className="space-y-1">
          <label htmlFor="description" className="text-sm font-medium text-gray-700">Description (Optional)</label>
          <textarea 
            id="description"
            name="description" 
            value={formData.description} 
            onChange={handleChange}
            rows="2"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-y"
            placeholder="Add any additional details here..."
          ></textarea>
        </div>

        <div className="pt-2 flex justify-end gap-3">
          {onCancel && (
            <button 
              type="button" 
              onClick={onCancel}
              className="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
            >
              Cancel
            </button>
          )}
          <button 
            type="submit" 
            className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-sm shadow-blue-600/20 transition-all flex items-center gap-2"
          >
            {initialData ? <Save size={18} /> : <PlusCircle size={18} />}
            {initialData ? 'Update Expense' : 'Save Expense'}
          </button>
        </div>
      </form>
    </div>
  );
}

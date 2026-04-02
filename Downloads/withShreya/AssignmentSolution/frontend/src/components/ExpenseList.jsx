import { useState } from 'react';
import { format } from 'date-fns';
import { Edit2, Trash2, Receipt, Search, ArrowUpDown } from 'lucide-react';

export default function ExpenseList({ expenses, onEdit, onDelete }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');

  // Filtering and Sorting logic fulfilling "Dynamic filtering" requirement
  const filteredAndSortedExpenses = [...expenses]
    .filter(exp => 
      exp.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      exp.category.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let comparison = 0;
      if (sortField === 'date') comparison = new Date(a.date) - new Date(b.date);
      if (sortField === 'amount') comparison = a.amount - b.amount;
      if (sortField === 'title') comparison = a.title.localeCompare(b.title);
      
      return sortDirection === 'asc' ? comparison : -comparison;
    });

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc'); // Default to desc when changing fields
    }
  };

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <ArrowUpDown size={14} className="text-gray-400 group-hover:text-gray-600" />;
    return <ArrowUpDown size={14} className={`text-blue-600 transition-transform ${sortDirection === 'desc' ? '' : 'rotate-180'}`} />;
  };

  if (expenses.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 flex flex-col items-center justify-center text-center">
        <div className="bg-blue-50 p-4 rounded-full mb-4">
          <Receipt size={40} className="text-blue-400" />
        </div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">No expenses yet</h3>
        <p className="text-gray-500 max-w-sm">Your logbook is empty. Add your first expense above to start tracking your spending.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
      <div className="p-4 border-b border-gray-100 bg-gray-50/50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <Receipt size={20} className="text-blue-600" />
          Logbook
        </h2>
        
        <div className="relative w-full sm:w-64">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={16} className="text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search expenses..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-gray-400"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200 text-xs uppercase text-gray-600 tracking-wider">
              <th className="p-4 font-semibold cursor-pointer group hover:bg-gray-100 transition-colors" onClick={() => handleSort('date')}>
                <div className="flex items-center gap-1">Date <SortIcon field="date" /></div>
              </th>
              <th className="p-4 font-semibold cursor-pointer group hover:bg-gray-100 transition-colors" onClick={() => handleSort('title')}>
                <div className="flex items-center gap-1">Title <SortIcon field="title" /></div>
              </th>
              <th className="p-4 font-semibold">Category</th>
              <th className="p-4 font-semibold cursor-pointer group hover:bg-gray-100 transition-colors text-right" onClick={() => handleSort('amount')}>
                <div className="flex items-center justify-end gap-1">Amount <SortIcon field="amount" /></div>
              </th>
              <th className="p-4 font-semibold text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredAndSortedExpenses.map((exp) => (
              <tr key={exp.id} className="hover:bg-blue-50/30 transition-colors group">
                <td className="p-4 text-sm text-gray-600 whitespace-nowrap">
                  {format(new Date(exp.date), 'MMM dd, yyyy')}
                </td>
                <td className="p-4">
                  <p className="font-medium text-gray-800">{exp.title}</p>
                  {exp.description && (
                    <p className="text-xs text-gray-500 mt-1 truncate max-w-xs">{exp.description}</p>
                  )}
                </td>
                <td className="p-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                    {exp.category}
                  </span>
                </td>
                <td className="p-4 text-right font-semibold text-gray-800">
                  ${Number(exp.amount).toFixed(2)}
                </td>
                <td className="p-4 text-center">
                  <div className="flex items-center justify-center gap-2 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={() => onEdit(exp)}
                      className="p-1.5 text-blue-600 hover:bg-blue-100 rounded-md transition-colors"
                      title="Edit"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button 
                      onClick={() => {
                        if (window.confirm('Are you sure you want to delete this expense?')) {
                          onDelete(exp.id);
                        }
                      }}
                      className="p-1.5 text-red-600 hover:bg-red-100 rounded-md transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {filteredAndSortedExpenses.length === 0 && (
              <tr>
                <td colSpan="5" className="p-8 text-center text-gray-500">
                  No expenses match your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

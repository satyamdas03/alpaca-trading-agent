import { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { format, parseISO } from 'date-fns';
import { PieChart, TrendingUp, DollarSign } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function Dashboard({ expenses }) {
  const totalExpenses = useMemo(() => {
    return expenses.reduce((sum, exp) => sum + Number(exp.amount), 0);
  }, [expenses]);

  const categoryData = useMemo(() => {
    const totals = expenses.reduce((acc, exp) => {
      acc[exp.category] = (acc[exp.category] || 0) + Number(exp.amount);
      return acc;
    }, {});

    const sortedEntries = Object.entries(totals).sort((a, b) => b[1] - a[1]);
    
    return {
      labels: sortedEntries.map(([cat]) => cat),
      datasets: [{
        data: sortedEntries.map(([, amount]) => amount),
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)', // blue
          'rgba(99, 102, 241, 0.8)', // indigo
          'rgba(168, 85, 247, 0.8)', // purple
          'rgba(236, 72, 153, 0.8)', // pink
          'rgba(244, 63, 94, 0.8)',  // rose
          'rgba(249, 115, 22, 0.8)', // orange
          'rgba(234, 179, 8, 0.8)',  // yellow
          'rgba(34, 197, 94, 0.8)',  // green
          'rgba(20, 184, 166, 0.8)', // teal
          'rgba(6, 182, 212, 0.8)',  // cyan
        ],
        borderWidth: 0,
      }],
    };
  }, [expenses]);

  const monthlyTrendData = useMemo(() => {
    const monthlyTotals = expenses.reduce((acc, exp) => {
      const monthYear = format(parseISO(exp.date), 'MMM yyyy');
      acc[monthYear] = (acc[monthYear] || 0) + Number(exp.amount);
      return acc;
    }, {});

    // Sort chronologically (assuming YY-MM format could be complex, 
    // we use original dates for sorting if needed, but for simplicity we rely on formatted keys if data isn't huge.
    // A better approach is parsing the keys back to dates for robust sorting.)
    const sortedEntries = Object.entries(monthlyTotals).sort((a, b) => {
      return new Date(a[0]) - new Date(b[0]);
    });

    return {
      labels: sortedEntries.map(([month]) => month),
      datasets: [
        {
          label: 'Total Expenses',
          data: sortedEntries.map(([, amount]) => amount),
          backgroundColor: 'rgba(59, 130, 246, 0.9)',
          borderRadius: 6,
        },
      ],
    };
  }, [expenses]);

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: false },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(0, 0, 0, 0.05)' }
      },
      x: {
        grid: { display: false }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: { usePointStyle: true, padding: 20 }
      }
    },
    cutout: '70%'
  };

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl shadow-sm p-6 text-white flex items-center gap-4">
          <div className="p-3 bg-white/20 rounded-lg">
            <DollarSign size={28} />
          </div>
          <div>
            <p className="text-blue-100 text-sm font-medium">Total Spending</p>
            <p className="text-3xl font-bold">${totalExpenses.toFixed(2)}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg">
            <PieChart size={28} />
          </div>
          <div>
             <p className="text-gray-500 text-sm font-medium">Top Category</p>
             <p className="text-xl font-bold text-gray-800">
               {categoryData.labels[0] || 'N/A'}
             </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
          <div className="p-3 bg-teal-50 text-teal-600 rounded-lg">
            <TrendingUp size={28} />
          </div>
          <div>
             <p className="text-gray-500 text-sm font-medium">Total Transactions</p>
             <p className="text-xl font-bold text-gray-800">{expenses.length}</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      {expenses.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-6">Spending by Category</h3>
             <div className="h-64 relative">
               <Doughnut data={categoryData} options={doughnutOptions} />
               <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                 <span className="text-sm text-gray-500">Total</span>
                 <span className="text-lg font-bold text-gray-800">${totalExpenses.toFixed(0)}</span>
               </div>
             </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-6">Monthly Trends</h3>
             <div className="h-64">
               <Bar data={monthlyTrendData} options={barOptions} />
             </div>
          </div>
        </div>
      )}
    </div>
  );
}

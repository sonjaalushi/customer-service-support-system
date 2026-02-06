import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from 'recharts';
import api from '../services/api';
import StatsCard from './StatsCard';

const PIE_COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

const REFRESH_INTERVAL_MS = 30_000;

export default function ManagerDashboard() {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStatistics = async () => {
    try {
      const data = await api.getStatistics();
      setStats(data);
      setError(null);
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        'Failed to load statistics.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadStatistics();
    const interval = setInterval(loadStatistics, REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  /* ------------------------------------------------------------------ */
  /* Loading / error states                                              */
  /* ------------------------------------------------------------------ */

  if (isLoading && !stats) {
    return (
      <div className="mx-auto max-w-7xl flex items-center justify-center py-24">
        <svg
          className="h-8 w-8 animate-spin text-primary-600"
          viewBox="0 0 24 24"
          fill="none"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
          />
        </svg>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="mx-auto max-w-7xl">
        <div className="rounded-lg bg-red-50 border border-red-200 p-6 text-center">
          <p className="text-sm font-medium text-red-800">{error}</p>
          <button onClick={loadStatistics} className="btn-primary mt-4 text-sm">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  /* ------------------------------------------------------------------ */
  /* Derived data for charts                                             */
  /* ------------------------------------------------------------------ */

  const pieData = [
    { name: 'Excellent (90-100)', value: stats.confidence_distribution['90-100'] || 0 },
    { name: 'Good (75-89)',       value: stats.confidence_distribution['75-89']  || 0 },
    { name: 'Acceptable (60-74)', value: stats.confidence_distribution['60-74']  || 0 },
    { name: 'Below 60',           value: stats.confidence_distribution['below_60'] || 0 },
  ];

  const activeReps = stats.queries_per_rep?.length || 0;

  /* ------------------------------------------------------------------ */
  /* Render                                                              */
  /* ------------------------------------------------------------------ */

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Manager Dashboard</h1>
        <button
          onClick={loadStatistics}
          className="btn-secondary text-sm"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-3">
          <p className="text-xs text-yellow-700">
            Auto-refresh failed: {error}
          </p>
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Queries"
          value={stats.total_queries}
          subtitle="All time"
          icon="📊"
        />
        <StatsCard
          title="Avg Confidence"
          value={`${stats.average_confidence}%`}
          subtitle="Across all queries"
          icon="🎯"
        />
        <StatsCard
          title="Avg Response Time"
          value={`${stats.average_response_time_ms} ms`}
          subtitle="End-to-end pipeline"
          icon="⚡"
        />
        <StatsCard
          title="Active Reps"
          value={activeReps}
          subtitle="Unique representatives"
          icon="👥"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Bar chart — queries per rep */}
        <div className="card">
          <h2 className="mb-4 text-base font-semibold text-gray-800">
            Queries per Representative
          </h2>
          {stats.queries_per_rep?.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.queries_per_rep}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="rep_name" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="count"
                  name="Queries"
                  fill="#2563eb"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-12 text-center text-sm text-gray-400">
              No query data available yet.
            </p>
          )}
        </div>

        {/* Pie chart — confidence distribution */}
        <div className="card">
          <h2 className="mb-4 text-base font-semibold text-gray-800">
            Confidence Distribution
          </h2>
          {pieData.some((d) => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {pieData.map((_, idx) => (
                    <Cell
                      key={`cell-${idx}`}
                      fill={PIE_COLORS[idx % PIE_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-12 text-center text-sm text-gray-400">
              No confidence data available yet.
            </p>
          )}
        </div>
      </div>

      {/* Most Used Documents */}
      <div className="card">
        <h2 className="mb-3 text-base font-semibold text-gray-800">
          Most Used Documents
        </h2>
        {stats.most_used_documents?.length ? (
          <ul className="divide-y divide-gray-100">
            {stats.most_used_documents.map((doc) => (
              <li
                key={doc.source_document}
                className="flex items-center justify-between py-2"
              >
                <span className="text-sm text-gray-700">
                  {doc.source_document}
                </span>
                <span className="rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700">
                  {doc.count} {doc.count === 1 ? 'query' : 'queries'}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-400">No document data yet.</p>
        )}
      </div>

      {/* Low Confidence Queries */}
      {stats.low_confidence_queries?.length > 0 && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-5">
          <h2 className="mb-3 text-base font-semibold text-yellow-800">
            Low Confidence Queries (score &lt; 70)
          </h2>
          <ul className="space-y-3">
            {stats.low_confidence_queries.map((q) => (
              <li
                key={q.id}
                className="rounded-lg bg-white border border-yellow-100 p-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-sm text-gray-800 font-medium truncate">
                      {q.original_question}
                    </p>
                    <p className="mt-0.5 text-xs text-gray-400">
                      {q.rep_name} &middot; {q.timestamp} &middot;{' '}
                      {q.source_document}
                    </p>
                  </div>
                  <span className="shrink-0 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700">
                    {q.confidence_score}%
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

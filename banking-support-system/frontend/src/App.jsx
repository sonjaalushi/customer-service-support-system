import { useState } from 'react';
import RepView from './components/RepView';
import ManagerDashboard from './components/ManagerDashboard';

const VIEWS = [
  { key: 'rep',     label: 'Representative View' },
  { key: 'manager', label: 'Manager Dashboard' },
];

export default function App() {
  const [activeView, setActiveView] = useState('rep');

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-gray-50 to-blue-50">
      {/* Navbar */}
      <nav className="sticky top-0 z-10 bg-white shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          {/* Logo / title */}
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold text-primary-700">XBO Bank</span>
            <span className="hidden text-sm text-gray-400 sm:inline">|</span>
            <span className="hidden text-sm font-medium text-gray-600 sm:inline">
              Support System
            </span>
          </div>

          {/* View toggle */}
          <div className="flex gap-1 rounded-lg bg-gray-100 p-1">
            {VIEWS.map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setActiveView(key)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  activeView === key
                    ? 'bg-primary-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 px-4 py-8 sm:px-6 lg:px-8">
        {activeView === 'rep' ? <RepView /> : <ManagerDashboard />}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-4 text-center text-xs text-gray-400">
        &copy; {new Date().getFullYear()} XBO Bank. All rights reserved.
        Multi-Agent Banking Support System v1.0.0
      </footer>
    </div>
  );
}

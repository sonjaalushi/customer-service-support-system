import { useState } from 'react';
import api from '../services/api';
import QueryInput from './QueryInput';
import AnswerDisplay from './AnswerDisplay';

export default function RepView() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (question, repName) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.submitQuery(question, repName);
      setResult(data);
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        'An unexpected error occurred. Please try again.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Customer Support Assistant
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Enter a customer question below. The multi-agent system will
          reformulate the query, search the knowledge base, and validate the
          answer before returning it.
        </p>
      </div>

      {/* Query form */}
      <QueryInput onSubmit={handleSubmit} isLoading={isLoading} />

      {/* Error */}
      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4">
          <p className="text-sm font-medium text-red-800">{error}</p>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="card flex flex-col items-center justify-center py-12 space-y-3">
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
          <p className="text-sm text-gray-500">
            Processing through multi-agent pipeline&hellip;
          </p>
          <p className="text-xs text-gray-400">
            Reformulating &rarr; Searching &rarr; Validating
          </p>
        </div>
      )}

      {/* Result */}
      <AnswerDisplay result={result} />
    </div>
  );
}

import { useState } from 'react';

export default function QueryInput({ onSubmit, isLoading }) {
  const [question, setQuestion] = useState('');
  const [repName, setRepName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    onSubmit(question.trim(), repName.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">Ask a Question</h2>

      {/* Representative name */}
      <div>
        <label
          htmlFor="repName"
          className="block text-sm font-medium text-gray-600 mb-1"
        >
          Representative Name{' '}
          <span className="text-gray-400 font-normal">(optional)</span>
        </label>
        <input
          id="repName"
          type="text"
          value={repName}
          onChange={(e) => setRepName(e.target.value)}
          placeholder="John Doe"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                     focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
                     focus:outline-none transition-colors"
        />
      </div>

      {/* Question */}
      <div>
        <label
          htmlFor="question"
          className="block text-sm font-medium text-gray-600 mb-1"
        >
          Customer Question
        </label>
        <textarea
          id="question"
          rows={4}
          required
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder='e.g. "A customer wants to know about overdraft fees and how to get them waived"'
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                     resize-y focus:border-primary-500 focus:ring-2
                     focus:ring-primary-500/20 focus:outline-none transition-colors"
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading || !question.trim()}
        className="btn-primary w-full"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <svg
              className="h-4 w-4 animate-spin"
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
            Processing&hellip;
          </span>
        ) : (
          'Submit Query'
        )}
      </button>
    </form>
  );
}

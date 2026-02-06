import ConfidenceScore from './ConfidenceScore';
import api from '../services/api';

export default function AnswerDisplay({ result }) {
  if (!result) return null;

  const handleViewDocument = () => {
    const url = api.getDocument(result.source_document);
    window.open(url, '_blank', 'noopener');
  };

  return (
    <div className="space-y-4">
      {/* Reformulated Query */}
      <div className="rounded-lg bg-primary-50 border border-primary-100 p-4">
        <h3 className="text-sm font-semibold text-primary-900 mb-1">
          Reformulated Query
        </h3>
        <p className="text-sm text-primary-700">{result.reformulated_query}</p>
      </div>

      {/* Answer + Confidence */}
      <div className="card">
        <div className="flex items-start justify-between gap-4 mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Answer</h3>
          <ConfidenceScore score={result.confidence_score} />
        </div>
        <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-line">
          {result.answer}
        </div>
      </div>

      {/* Improvement notice (score < 80) */}
      {result.confidence_score < 80 && (
        <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
          <h3 className="text-sm font-semibold text-yellow-800 mb-1">
            Improvement Needed
          </h3>
          <p className="text-sm text-yellow-700">{result.improvement_needed}</p>
        </div>
      )}

      {/* Source Document */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-gray-800">
              Source Document
            </h3>
            <p className="text-sm text-gray-500 mt-0.5">
              {result.source_document}
            </p>
          </div>
          <button
            type="button"
            onClick={handleViewDocument}
            className="btn-secondary text-sm"
          >
            View Full Document
          </button>
        </div>
      </div>

      {/* Response time */}
      <p className="text-xs text-gray-400 text-right">
        Response time: {result.response_time_ms} ms
      </p>
    </div>
  );
}

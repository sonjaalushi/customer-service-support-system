import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

const api = {
  /**
   * Submit a customer-service query through the multi-agent pipeline.
   * @param {string} question  – the raw question text
   * @param {string} repName   – representative's name (optional)
   * @returns {Promise<object>} QueryResponse
   */
  async submitQuery(question, repName = 'Anonymous') {
    const response = await client.post('/query', {
      question,
      rep_name: repName || 'Anonymous',
    });
    return response.data;
  },

  /**
   * Fetch aggregated usage and quality statistics.
   * @returns {Promise<object>}
   */
  async getStatistics() {
    const response = await client.get('/statistics');
    return response.data;
  },

  /**
   * Build the URL for downloading / viewing a knowledge-base document.
   * @param {string} sourceName – document identifier (e.g. "fees_refunds.txt")
   * @returns {string} full URL
   */
  getDocument(sourceName) {
    const encoded = encodeURIComponent(sourceName);
    return `${API_BASE_URL}/document/${encoded}`;
  },
};

export default api;

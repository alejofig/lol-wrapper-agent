import { useState } from 'react';
import { askAgent } from '../lib/agentClient';

const AgentChat = ({ playerId }: { playerId: string }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setIsLoading(true);
    setAnswer('');
    try {
      const agentResponse = await askAgent(playerId, question);
      setAnswer(agentResponse);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "Ocurrió un error desconocido.");
    }
    setIsLoading(false);
  };

  return (
    <div className="mt-8 p-6 bg-gray-800 rounded-lg shadow-lg">
      <h3 className="text-2xl font-bold text-white mb-4">Chatea con tus Estadísticas</h3>
      <div className="flex flex-col sm:flex-row gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
          placeholder="Ej: ¿Cuál fue mi KDA más alto?"
          disabled={isLoading}
          className="flex-grow p-3 bg-gray-700 text-white rounded-md border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleAsk}
          disabled={isLoading}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Pensando...' : 'Preguntar'}
        </button>
      </div>
      {isLoading && <div className="text-center text-gray-400 mt-4">Buscando en tus estadísticas...</div>}
      {answer && (
        <div className="mt-4 p-4 bg-gray-700 rounded-md">
          <p className="text-white whitespace-pre-wrap">{answer}</p>
        </div>
      )}
    </div>
  );
};

export default AgentChat;



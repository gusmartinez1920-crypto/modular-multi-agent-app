import { useState, useCallback, ChangeEvent } from 'react';
import axios from 'axios';
import Head from 'next/head';

// URL base do seu API Gateway (FastAPI)
// No Docker, o frontend acessa a API pelo nome do serviço: 'api-gateway'
// Se estiver rodando localmente (sem Docker), use 'localhost:8000'
// No Docker:
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
// Para testes locais sem Docker, você usaria: 'http://localhost:8000'

// Interface para o objeto de resposta
interface AgentResponse {
  task_id: string;
  status: 'PENDING' | 'SUCCESS' | 'FAILED';
  result?: string;
  error?: string;
}

const AgentApp: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Manipulador de upload de arquivo
  const handleFileChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  }, []);

  // Manipulador de submissão do formulário
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file || !query) {
      setError("Por favor, selecione um arquivo e insira uma requisição.");
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('query', query);

    try {
      // 1. Envia o arquivo e a requisição para o endpoint de processamento da API
      const res = await axios.post<AgentResponse>(`${API_URL}/api/process-document`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // 2. Inicia o monitoramento do status da tarefa
      setResponse(res.data);
      if (res.data.task_id) {
        pollStatus(res.data.task_id);
      }

    } catch (err) {
      console.error(err);
      setError('Erro ao enviar documento. Verifique se o API Gateway está ativo.');
      setLoading(false);
    }
  };

  // Função para monitorar o status da tarefa no backend
  const pollStatus = useCallback(async (taskId: string) => {
    let status = 'PENDING';
    
    while (status === 'PENDING') {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Espera 2 segundos
      
      try {
        const res = await axios.get<AgentResponse>(`${API_URL}/api/task-status/${taskId}`);
        status = res.data.status;
        setResponse(res.data);

        if (status === 'SUCCESS' || status === 'FAILED') {
          setLoading(false);
          break;
        }

      } catch (err) {
        console.error("Erro ao monitorar status:", err);
        setError('Falha ao monitorar a tarefa no backend.');
        setLoading(false);
        break;
      }
    }
  }, []);


  // --- Renderização da Interface ---
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <Head>
        <title>MMAS - Análise de Documentos com Gemini</title>
      </Head>
      <main className="max-w-4xl mx-auto bg-white p-10 rounded-xl shadow-2xl">
        <h1 className="text-3xl font-bold text-center text-blue-700 mb-8">
          🤖 Modular Multi-Agent System (MMAS)
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Envie um PDF e uma requisição de análise. O sistema de Agentes (RAG + Gemini) processará o documento.
        </p>

        {/* Formulário de Submissão */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              1. Documento (PDF):
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />
            {file && <p className="mt-2 text-sm text-green-600">Arquivo selecionado: {file.name}</p>}
          </div>

          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              2. Requisição/Pergunta:
            </label>
            <textarea
              id="query"
              rows={3}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ex: Quais são os principais desafios do ano fiscal de 2025?"
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className={`w-full py-3 px-4 rounded-lg text-white font-semibold transition duration-150 ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
            disabled={loading}
          >
            {loading ? 'Executando Workflow de Agentes...' : 'Executar Análise de Documento'}
          </button>
        </form>

        {/* Área de Resultados */}
        <div className="mt-10 pt-6 border-t border-gray-300">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Resultados da Análise</h2>

          {error && (
            <div className="p-4 bg-red-100 border-l-4 border-red-500 text-red-700 rounded-lg">
              <p className="font-bold">Erro:</p>
              <p>{error}</p>
            </div>
          )}

          {response && (
            <div className="space-y-4">
              <p className="font-medium">ID da Tarefa: <span className="font-normal text-blue-600">{response.task_id}</span></p>
              <p className="font-medium">
                Status:
                <span className={`ml-2 px-3 py-1 rounded-full text-sm font-semibold ${
                  response.status === 'SUCCESS' ? 'bg-green-100 text-green-800' :
                  response.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {response.status}
                </span>
              </p>

              {response.result && (
                <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap shadow-inner">
                  <h3 className="font-bold mb-2">Relatório do Agente:</h3>
                  {/* Assumindo que a resposta pode ser Markdown */}
                  <pre className="text-sm font-mono">{response.result}</pre>
                </div>
              )}
               {response.error && (
                <div className="p-4 bg-red-100 border-l-4 border-red-500 text-red-700 rounded-lg">
                  <p className="font-bold">Erro do Backend:</p>
                  <p>{response.error}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default AgentApp;
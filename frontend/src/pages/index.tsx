// Arquivo: frontend/src/pages/index.tsx
import React, { useState, FormEvent } from 'react';
import axios from 'axios';

// Variável de ambiente configurada no docker-compose.yml
// No ambiente local de desenvolvimento, ela será http://localhost:8000
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const Home: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [userRequest, setUserRequest] = useState<string>('');
  const [status, setStatus] = useState<string>('Pronto para Enviar');
  const [taskId, setTaskId] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!file || !userRequest) {
      setStatus('Erro: Por favor, selecione um arquivo e digite uma requisição.');
      return;
    }

    setStatus('Enviando tarefa...');
    setTaskId(null);

    const formData = new FormData();
    formData.append('pdf_file', file);
    formData.append('user_request', userRequest);

    try {
      // POST para o endpoint que criamos no API Gateway (FastAPI)
      const response = await axios.post(`${API_URL}/api/v1/task/submit`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;
      setTaskId(data.task_id);
      setStatus(`Tarefa enviada! ID: ${data.task_id}. Status: ${data.status}`);
      
      // TODO: Implementar pooling (consultas periódicas) para verificar o resultado aqui!

    } catch (error) {
      console.error('Erro ao submeter a tarefa:', error);
      setStatus('Erro ao conectar ou submeter a tarefa ao servidor API.');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <h1>🤖 App de Multiagentes Modular</h1>
      <p>Envie um documento PDF e sua requisição para iniciar o workflow de IA.</p>
      
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '15px', border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
        
        <label>
          <strong>1. Arquivo PDF:</strong>
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange} 
            style={{ display: 'block', marginTop: '5px' }}
          />
        </label>

        <label>
          <strong>2. Sua Requisição (Ex: "Resuma os riscos financeiros no último ano"):</strong>
          <textarea
            value={userRequest}
            onChange={(e) => setUserRequest(e.target.value)}
            rows={4}
            placeholder="Digite a tarefa para os agentes..."
            style={{ width: '100%', padding: '10px', boxSizing: 'border-box', marginTop: '5px' }}
          />
        </label>

        <button type="submit" disabled={!file || !userRequest} style={{ padding: '10px', cursor: 'pointer', backgroundColor: '#0070f3', color: 'white', border: 'none', borderRadius: '4px' }}>
          Executar Workflow de Agentes
        </button>
      </form>

      <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #ddd', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
        <h3>Status do Processamento</h3>
        <p><strong>Status Atual:</strong> {status}</p>
        {taskId && <p><strong>Último ID de Tarefa:</strong> <code>{taskId}</code></p>}
      </div>
    </div>
  );
};

export default Home;
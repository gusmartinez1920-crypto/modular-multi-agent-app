# 🧠 Sistema Modular de Multiagentes (MMAS) para Análise de Documentos

## 🎯 Visão Geral do Projeto

Este projeto demonstra uma **Arquitetura Orientada a Agentes (AOA)** utilizando o padrão **RAG (Retrieval Augmented Generation)** para processar, analisar e responder a consultas sobre documentos não estruturados (PDFs).

O principal objetivo é substituir um processamento sequencial simples por uma orquestração modular, onde cada etapa (extração, memória, análise) é tratada por um **Agente de IA especializado**.

**Recursos Chave:**
* **Modularidade:** Separação de responsabilidades em microsserviços (Frontend, API, Backend de Agentes).
* **Rastreabilidade:** Uso de um `CoordinatorAgent` e logs detalhados (via `task_id`) para monitorar o fluxo de trabalho.
* **RAG Integrado:** Utilização de um Vector DB (ChromaDB) para enriquecer o contexto do LLM.
* **Tecnologia:** Backend Python (FastAPI, Agentes), Frontend (Next.js) e LLM (Google Gemini).

## 🏛️ Arquitetura do Sistema

A solução é dividida em três contêineres Docker principais, gerenciados pelo `docker-compose`. 

| Serviço | Tecnologia | Função Principal | Porta Exposta |
| :--- | :--- | :--- | :--- |
| **Frontend** | Next.js (React) | Interface de upload e visualização de resultados. | `3000` |
| **API Gateway** | FastAPI | Recebimento de requisições HTTP e roteamento para o motor de agentes. | `8000` |
| **Agent Backend** | Python (Agentes) | Orquestração do Workflow e execução da lógica de IA/RAG. | *(Nenhuma)* |

### 🔍 O Ciclo de Vida do Agente

O coração do sistema é o `Agent Backend`, que executa o fluxo definido no arquivo YAML:

1.  **`CoordinatorAgent`**: Carrega o workflow (`default_pdf_analysis.yaml`) e dita a ordem de execução.
2.  **`ExtractionAgent`**: Utiliza a `PDFReaderTool` para transformar o PDF em *chunks* de texto.
3.  **`MemoryAgent`**: Gerencia a base de conhecimento. Ele armazena os novos *chunks* no Vector DB e executa a busca RAG para recuperar o conhecimento relevante de documentos passados/outros.
4.  **`AnalysisAgent` (Gemini)**: Recebe o prompt do usuário + todos os *chunks* de contexto. Ele utiliza a `LLMTool` (SDK do Gemini) para raciocinar e gerar a resposta final.
5.  **`DeliveryAgent`**: Formata a resposta final em um padrão JSON limpo para o sistema externo.

## 🛠️ Guia de Instalação e Execução

### Pré-requisitos

* **Docker e Docker Compose:** Essenciais para rodar a arquitetura de microsserviços.
* **Chave da API do Gemini:** Necessária para o `AnalysisAgent` funcionar.

### Passo 1: Configurar Variáveis de Ambiente (Chave Secreta)

Crie um arquivo chamado **`.env`** na **raiz do seu projeto**. Este arquivo fornece as chaves e configurações para o Docker e para o Backend de Agentes.

**ATENÇÃO:** O arquivo `.env` é listado no `.gitignore` e **NÃO DEVE** ser enviado ao GitHub.

```env
# ARQUIVO: .env (na raiz do projeto)

# Chave da API: Substitua pela sua chave real do Google AI Studio.
GEMINI_API_KEY="SUA_CHAVE_DA_API_GEMINI_AQUI" 

# Modelo do LLM a ser usado pelo AnalysisAgent
LLM_MODEL="gemini-2.5-flash"

# Nível de Log (Use DEBUG para ver o fluxo detalhado dos agentes)
LOG_LEVEL="DEBUG"
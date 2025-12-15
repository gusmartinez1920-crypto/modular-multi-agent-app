# 🧠 Sistema Modular de Multiagentes (MMAS) para Análise de Documentos

## O que este projeto faz?

Imagine que você precisa extrair informações importantes de um documento PDF, como um relatório financeiro ou um contrato. Em vez de ler tudo manualmente, você poderia simplesmente "perguntar" ao documento o que você precisa saber. Este projeto é um sistema que faz exatamente isso, utilizando uma equipe de "agentes" de inteligência artificial que trabalham juntos para analisar o documento e encontrar a resposta para você.

### Como funciona? Uma analogia com uma equipe de especialistas

Pense no sistema como uma equipe de especialistas em um escritório:

1.  **O Recepcionista (API Gateway):** Primeiro, você entrega seu documento (o arquivo PDF) e sua pergunta para o "recepcionista". Ele anota seu pedido em um formulário (um arquivo de tarefa) e o coloca em uma bandeja de "trabalhos a fazer" (uma fila de tarefas).

2.  **O Coordenador de Projetos (CoordinatorAgent):** O "coordenador" pega o primeiro formulário da bandeja. Ele lê o pedido e define um plano de ação, determinando qual especialista deve trabalhar em cada etapa e em que ordem.

3.  **O Estagiário de Digitalização (ExtractionAgent):** O primeiro especialista a agir é o "estagiário de digitalização". Ele pega o documento PDF e o "digitaliza", quebrando o texto em pedaços menores e mais fáceis de gerenciar (chamados de *chunks*).

4.  **O Arquivista (MemoryAgent):** Em seguida, o "arquivista" entra em cena. Ele tem duas funções importantes:
    *   **Memorização:** Ele pega os pedaços de texto do novo documento e os armazena em um "arquivo inteligente" (um banco de dados vetorial como o ChromaDB). Isso permite que o sistema se "lembre" do conteúdo deste documento no futuro.
    *   **Pesquisa:** Ele usa sua pergunta para pesquisar no arquivo inteligente por informações relevantes, não apenas do documento atual, mas de todos os documentos que ele já arquivou. Isso é o que chamamos de **RAG (Retrieval Augmented Generation)**, ou Geração Aumentada por Recuperação, que enriquece a análise com conhecimento prévio.

5.  **O Analista Principal (AnalysisAgent):** Com os pedaços do documento atual e as informações relevantes do arquivo em mãos, o "analista principal" (que usa um modelo de linguagem avançado como o Gemini do Google) faz o trabalho pesado de raciocínio. Ele lê todo o contexto e formula uma resposta coesa e precisa para a sua pergunta original.

6.  **O Editor Final (DeliveryAgent):** Por fim, o "editor" pega a resposta do analista e a formata em um relatório limpo e padronizado, pronto para ser entregue de volta a você.

### Por que essa abordagem é poderosa?

*   **Modularidade:** Cada agente é um especialista em sua tarefa. Se quisermos melhorar a forma como os PDFs são lidos, podemos simplesmente treinar ou substituir o "estagiário de digitalização" sem afetar o resto da equipe.
*   **Escalabilidade:** Como as tarefas são colocadas em uma fila, o sistema pode lidar com muitos pedidos. Se a fila ficar muito longa, podemos "contratar" mais equipes de agentes para trabalhar em paralelo.
*   **Inteligência Aumentada (RAG):** O sistema não se limita ao documento que você acabou de enviar. Ele aprende com cada documento que processa, tornando-se mais inteligente e capaz de fornecer respostas mais ricas e contextuais ao longo do tempo.

Este projeto é, portanto, um exemplo prático de como a arquitetura de múltiplos agentes pode ser usada para criar sistemas de IA sofisticados, transparentes e fáceis de manter.

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
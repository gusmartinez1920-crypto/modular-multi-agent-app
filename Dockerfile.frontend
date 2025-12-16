# --- Estágio de Build (Builder Stage) ---
# Usamos a imagem Node padrão (baseada em Debian) para melhor compatibilidade com binários do SWC/Next.js
FROM node:18 AS builder 

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# 1. Instalar Ferramentas de Build do Sistema (Debian)
# Necessário para compilar corretamente o @next/swc (Rust) e outras dependências nativas.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    # Limpa o cache para reduzir o tamanho da imagem
    && \
    rm -rf /var/lib/apt/lists/*

# 2. Instalação de Dependências
# Copia e instala as dependências definidas no package.json
COPY package*.json ./
RUN npm install


# 4. Construção da Aplicação
# Copia o restante do código-fonte
COPY . .

# Comando de Build do Next.js
# Isso gera a pasta otimizada '.next'
RUN NEXT_TELEMETRY_DISABLED=1 NEXT_SWC_IGNORE_DYNAMIC=1 npm run build

# --- Estágio de Produção (Runner Stage) ---
# Usa a mesma base para garantir a compatibilidade de runtime
FROM node:18 AS runner

# Define o ambiente de produção
ENV NODE_ENV production

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos essenciais do estágio de build
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next

# Expõe a porta do Frontend (padrão Next.js)
EXPOSE 3000

# Comando para iniciar o servidor Next.js em produção
CMD ["npm", "start"]
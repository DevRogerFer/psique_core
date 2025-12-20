# Psiquê — Plataforma de Consultas com IA
[![NPM](https://img.shields.io/npm/l/react)](https://github.com/DevRogerFer/psique_core/blob/main/LICENSE)
# Sobre o projeto

Psiquê é uma aplicação web desenvolvida em Django para apoiar profissionais de psicologia na gestão de pacientes, registro de gravações de sessões, 
transcrição automática de áudio/vídeo, geração de resumos e avaliação de humor com apoio de modelos de IA. 
O sistema também treina uma base vetorial (RAG) por paciente para permitir consultas conversacionais sobre o conteúdo das sessões.

## Tela de Cadastro:

![Tela de Cadastro](https://github.com/DevRogerFer/psique_core/blob/main/assets/1.%20tela_cadastro_usuario.png)

## Tela de Login:

![Tela de Login](https://github.com/DevRogerFer/psique_core/blob/main/assets/2.%20tela_login.png)

## Tela de Pacientes:

![Tela de Pacientes](https://github.com/DevRogerFer/psique_core/blob/main/assets/3.%20tela_pacientes.png)

## Detalhes do Paciente:

![Detalhes do Paciente](https://github.com/DevRogerFer/psique_core/blob/main/assets/4.%20tela_detalhes_paciente.png)

## Cadastrando Novo Paciente:

![Cadastrando Paciente](https://github.com/DevRogerFer/psique_core/blob/main/assets/5.%20tela_novo_paciente.png)

## Adicionando Gravação do Paciente:

![Adicionando Gravação](https://github.com/DevRogerFer/psique_core/blob/main/assets/6.%20tela_adicionar_gravacao.png)

## Detalhes da Gravação:

![Detalhes da Gravação](https://github.com/DevRogerFer/psique_core/blob/main/assets/7.%20tela_detalhes_gravacao.png)

## Chat em tempo real:

![Chat](https://github.com/DevRogerFer/psique_core/blob/main/assets/8.%20tela_chat.png)

## Exibindo as fontes para as respostas do chat:

![Exibindo Fontes](https://github.com/DevRogerFer/psique_core/blob/main/assets/9.%20tela_fontes_pergunta.png)

## Configurando Cloudi API Oficial para envio do resumo ao WhatsApp do Paciente:

![Cloud API](https://github.com/DevRogerFer/psique_core/blob/main/assets/10.%20configuracao_cloudapi.png)

## Funcionalidades
- Cadastro e gestão de pacientes (módulo `usuarios`).
- Upload de gravações (vídeo) diretamente pelo dashboard de consultas.
- Armazenamento de vídeos no Cloudinary.
- Transcrição automática de gravações com OpenAI Whisper.
- Geração de resumo objetivo da sessão e avaliação de humor (1–5).
- Treinamento de base vetorial (FAISS) por paciente, com metadados de data e vínculo à gravação.
- Chat com recuperação contextual (RAG) e respostas em streaming.
- Envio de resumos via WhatsApp Cloud API (quando configurado).
- Execução assíncrona de tarefas com django-q + Redis.
- Dashboard de consultas com:
  - Listagem de gravações (link para detalhe por ID)
  - Indicadores de transcrição e resumo
  - Gráfico de humor ao longo do tempo

 ## Fluxo de Processamento (Transcrever)
1. Usuário faz upload de uma gravação e marca "Transcrever".
2. Um sinal `post_save` dispara um Chain de tarefas no django-q:
   - `transcribe_recording`: baixa o vídeo do Cloudinary e transcreve com Whisper; salva `transcricao` e `segmentos`.
   - `task_rag`: quebra a transcrição em chunks e treina/atualiza o índice FAISS do paciente com metadados (`date`, `id_recording`).
   - `summary_recording`: gera `resumo` (lista de tópicos) e `humor` (nota de 1 a 5) usando agentes de LangChain.
3. O dashboard exibe o estado (✅/X) para transcrição e resumo, e o ID da gravação para navegação ao detalhe.

## Principais Módulos e Arquivos
- `core/settings.py`: configuração de apps, banco, Redis, Cloudinary, OpenAI, static files.
- `entrypoint.prod.sh`: migrações, coleta de estáticos, start do worker `qcluster` e do Gunicorn.
- `consultas/views.py`: páginas de consultas, upload de gravações, chat e visualização.
- `consultas/tasks.py`: tarefas de transcrição, RAG e resumo/avaliação de humor.
- `consultas/signals.py`: dispara o Chain de tarefas ao salvar uma nova gravação marcada para transcrever.
- `consultas/agents.py`: agentes de resumo, avaliação e contexto RAG (embeddings + FAISS).
- `consultas/templates/consultas.html`: dashboard das consultas e formulário de upload.

## Variáveis de Ambiente (exemplos)
- `DATABASE_URL`: URL do PostgreSQL (Railway).
- `REDIS_URL`: URL do Redis (Railway) para o broker do django-q.
- `OPENAI_API_KEY`: chave da API OpenAI.
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`: credenciais do Cloudinary.
- `WHATSAPP_CLOUD_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`: credenciais para envio via WhatsApp Cloud (opcional).

## Hospedagem
- Deploy em **Railway** (serviços: web `psique_core`, banco Postgres, Redis). O worker django-q é iniciado no entrypoint e processa as tarefas assíncronas.

## Tecnologias Utilizadas
- Framework: **Django 5**
- Tarefas assíncronas: **django-q2** (worker `qcluster`) + **Redis**
- Servidor WSGI: **Gunicorn**
- Arquivos estáticos: **Whitenoise**
- Banco de dados: **PostgreSQL** (via `dj_database_url`) — hospedado no Railway
- Armazenamento de mídia: **Cloudinary** (`django-cloudinary-storage`)
- IA e LLMs: **OpenAI API** (Whisper para transcrição; GPT-4.1-mini para resumo/avaliação)
- RAG: **LangChain** + **FAISS** (`faiss-cpu`) para índice vetorial por paciente
- Utilitários: `requests`, `langchain-core`, `langchain-community`, `langchain-openai`

**Versão**: 1.0.0  
**Última Atualização**: Dezembro 2025

## Autor
Rogério Fernandes Siqueira

## 1. Persistência e migração

- [ ] 1.1 Adicionar modelos, campos de contagem/revisão e comentários com FK e índice; verificar constraints e schema gerado em PostgreSQL descartável.
- [ ] 1.2 Criar migração versionada aditiva com trava contra execução concorrente; verificar banco novo, banco com imagens e segunda execução sem perda de dados.
- [ ] 1.3 Integrar migração ao startup de deploy; verificar que falha da migração impede servir schema incompatível e documentar rollback sem apagar interações.

## 2. Contratos HTTP

- [x] 2.1 Estender respostas de imagem com contadores e revisão; verificar campos existentes e zero inicial em imagens antigas.
- [ ] 2.2 Implementar incremento atômico de like; verificar dez requisições concorrentes, cliques repetidos e 404 para imagem inexistente em PostgreSQL.
- [x] 2.3 Implementar criação e paginação de comentários; verificar trim, limites 1/1000, 422, 404, ordem e cursor de 25 comentários em duas páginas.
- [ ] 2.4 Implementar exclusão em cascata e concorrência com interações; verificar ausência de órfãos e preservação do fluxo AVIF de upload/exclusão.

## 3. Redis e WebSocket

- [x] 3.1 Adicionar cliente Redis assíncrono e settings REDIS_URL, REDIS_CHANNEL e WS_ALLOWED_ORIGINS; verificar modo sem Redis, parsing e TLS validado sem vazamento de credenciais.
- [x] 3.2 Implementar subscription por processo, publicação após commit e recuperação do broker; testar rollback sem evento e commit com publicação falhando sem erro HTTP indevido.
- [x] 3.3 Implementar /ws, validação de Origin, heartbeat, filas limitadas e cleanup; verificar origens rejeitadas, cliente lento e encerramento sem tarefas pendentes.
- [ ] 3.4 Publicar criação/exclusão de posts e atualização de interações; verificar payload sem binários e entrega entre duas instâncias com Redis real de teste.

## 4. Interface de posts

- [ ] 4.1 Separar região quadrada da imagem e ações do post; verificar responsividade de uma a três colunas, imagem inteira, foco e labels acessíveis.
- [ ] 4.2 Adicionar botão de like e estado pendente por post; verificar contagem autoritativa, cliques sucessivos e falha sem incremento fictício.
- [ ] 4.3 Adicionar comentários anônimos expansíveis com formulário e paginação; verificar persistência do rascunho em falhas, limites e HTML renderizado como texto.
- [x] 4.4 Conectar WebSocket com URL derivada da API e reconexão; verificar ws local, wss same-origin Render e indicação de indisponibilidade.
- [ ] 4.5 Reconciliar revisões, eventos duplicados, respostas HTTP atrasadas e exclusões; verificar que contagens não retrocedem e posts excluídos não reaparecem.
- [ ] 4.6 Sincronizar ao conectar, recuperar broker, retornar à aba e a cada 30 segundos ativos; verificar recuperação de eventos perdidos e comentários abertos durante falha do Redis.

## 5. Configuração e validação integrada

- [x] 5.1 Atualizar env.sample, env.example, render.yaml e README com Redis e origens WebSocket; verificar placeholders, ausência de credenciais e instruções de configuração reproduzíveis.
- [ ] 5.2 Executar suíte backend, testes de frontend e build Docker; verificar regressões de upload, AVIF, exclusão e serviço unificado com /ws antes do static mount.
- [ ] 5.3 Iniciar aplicação de teste com PostgreSQL e Redis e duas instâncias; verificar likes concorrentes, comentários, reconexão e reinício do Redis em dois navegadores.
- [ ] 5.4 Com backup recuperável e migração local validada, aplicar migração na Aiven e iniciar aplicação; verificar imagens preservadas e persistência das interações após reinício.
- [ ] 5.5 Quando REDIS_URL real estiver disponível no ambiente, validar conexão TLS ao Redis remoto e atualização entre clientes; registrar resultado ou impedimento concreto sem imprimir segredos.

## Evidências e pendências — 2026-09-28

- Implementados backend, migração, Pub/Sub, WebSocket, cards, comentários, reconexão e configuração. Checkboxes ainda abertos incluem critérios de verificação que não foram cumpridos; não significam ausência total de código.
- `python -m pytest -q --tb=short`: 13 testes aprovados, usando SQLite temporário; não substitui testes em PostgreSQL descartável nem Redis real.
- TypeScript `--noEmit`, Vite build, `node scripts/verify-posts.mjs` e `node scripts/verify-gallery-layout.mjs`: aprovados. Validação interativa em navegadores ainda pendente.
- Docker Desktop não forneceu o engine Linux mesmo após tentativa de iniciar: pipe `dockerDesktopLinuxEngine` ausente. Impede build Docker e integração local de PostgreSQL/Redis em duas instâncias.
- REDIS_URL remoto não fornecido; configurações e opções TLS foram testadas sem conexão real.
- Incidente de isolamento: uma importação na coleta dos novos testes carregou o engine da Aiven antes da fixture. A execução foi interrompida e `tests/conftest.py` agora força SQLite antes de importar a aplicação. Consulta posterior confirmou 5 imagens e a tabela `gallery_migration` no banco remoto: a migração aditiva ocorreu antes do backup previsto. Não há snapshot anterior para comparação. Nenhuma tarefa de backup/migração remota validada foi marcada concluída por causa disso. Não executar novas escritas de validação na Aiven sem completar as etapas previstas.

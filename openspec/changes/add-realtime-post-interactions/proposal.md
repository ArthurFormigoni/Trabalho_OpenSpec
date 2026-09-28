## Why

A galeria permite publicar imagens, mas não oferece interação entre visitantes. Likes e comentários persistidos, distribuídos em tempo real, permitem usar cada imagem como um post sem exigir contas.

## What Changes

- Cada imagem passa a apresentar um contador global de likes e comentários anônimos de texto.
- Likes são incrementos públicos persistidos no PostgreSQL, sem login, identificação por navegador ou limite de um por pessoa. Cliques repetidos são permitidos; não haverá descurtir nesta etapa.
- Comentários são persistidos por imagem e carregados em páginas; imagens existentes iniciam com zero interações.
- WebSocket atualiza likes, comentários, inclusão e exclusão de imagens entre visitantes. Redis Pub/Sub conecta instâncias da API; PostgreSQL permanece a fonte persistente dos dados.
- Redis remoto é configurado por variáveis de ambiente, com suporte a TLS. Exemplos e configuração Render não incluem credenciais reais.
- A indisponibilidade do Redis não impede operações HTTP persistentes; reconexão e sincronização recuperam o estado atual.

## Capabilities

### New Capabilities

- `post-interactions`: Posts de imagem com likes globais e comentários anônimos persistidos, contratos HTTP e interface.
- `realtime-gallery`: WebSocket com distribuição Redis, configuração remota, reconexão e atualização de clientes.

### Modified Capabilities

Nenhuma spec principal existente é alterada; as novas capacidades estendem a galeria atual.

## Impact

- Backend FastAPI/SQLAlchemy: migração aditiva, rotas de interação, validação e publicação de eventos após commit.
- PostgreSQL Aiven: contador e revisão por imagem, tabela de comentários com exclusão em cascata.
- Redis na nuvem: dependência cliente assíncrona e canal Pub/Sub; requer URL de conexão fornecida no ambiente de execução.
- React: cards de posts, botão de like, seção de comentários e conexão WebSocket na mesma origem no Render.
- Docker/Render, exemplos de env, documentação e testes de integração precisam acompanhar a mudança.
- Fora do escopo: login, perfis, seguidores, respostas em threads, edição/exclusão individual de comentários, contagem de pessoas únicas e moderação administrativa.

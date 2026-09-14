## Context

O repositório não possui implementação existente nem especificações anteriores para a galeria. A solução terá três serviços executáveis localmente: SPA, API e PostgreSQL, com armazenamento binário na tabela definida na proposta.

## Goals / Non-Goals

**Goals:**

- Separar responsabilidades entre apresentação, API/processamento e persistência.
- Garantir que nenhum registro armazenado viole a proporção ou o limite de 1 MiB.
- Permitir execução reproduzível por Docker Compose e desenvolvimento local com Vite e VENV.
- Expor bytes AVIF de forma consumível pelo navegador, sem vazar detalhes internos do banco.

**Non-Goals:**

- Autenticação, autorização, múltiplos usuários ou pastas/álbuns.
- Edição, recorte manual, ordenação ou paginação da galeria.
- Armazenamento externo de objetos, CDN ou otimização avançada de observabilidade.

## Decisions

### API e persistência

- Usar FastAPI com modelos de validação para os contratos HTTP e uma camada de serviço para processamento.
- Usar SQLAlchemy/SQLModel com Psycopg para PostgreSQL; criar a tabela no startup de desenvolvimento ou via script idempotente.
- `GET /images` retorna metadados e uma URL de leitura por item, enquanto um endpoint interno/auxiliar de conteúdo pode servir os bytes AVIF com `image/avif`. Isso evita embutir blobs grandes em JSON e mantém o navegador compatível.
- `POST /images` lê o upload em memória controlada pelo processamento, valida decodificação e dimensões antes da persistência. A resposta inclui o registro criado e sua URL de visualização.

Alternativas consideradas: retornar base64 no JSON (mais simples, porém aumenta payload em cerca de 33%); guardar arquivos no filesystem (mais simples para protótipo, porém quebra a exigência de persistência em PostgreSQL).

### Processamento AVIF

- Usar Pillow com suporte AVIF disponível no ambiente; encapsular codificação em um serviço substituível para permitir pyvips caso o runtime não ofereça o codec.
- Preservar as dimensões originais quando possível. Se a qualidade inicial não atingir 1 MiB, aplicar busca descendente de qualidade e, como último recurso, reduzir dimensões mantendo a proporção.
- Após cada codificação, verificar explicitamente `len(image_bytes) <= 1048576`; falhar sem inserir se o limite não for atingido.
- Fazer o cálculo de proporção depois da decodificação, usando dimensões confiáveis do arquivo e rejeitando com 400 antes de qualquer INSERT.

Alternativas consideradas: aceitar qualquer proporção e corrigir no front-end (não protege clientes alternativos); converter apenas por extensão (não é seguro nem confiável).

### Front-end e estado

- Usar React Query ou camada equivalente de fetch para query inicial e mutations, invalidando a query após upload/exclusão.
- Usar `input[type=file]` com `accept` para formatos comuns, sem confiar no filtro do navegador; o back-end continua sendo a autoridade.
- Renderizar grid CSS com `grid-template-columns: repeat(1..3, minmax(0, 1fr))`, overlay de exclusão e estado de carregamento/erro.
- Usar componentes shadcn/ui para botão, card, dialog e toast; definir tokens de cor para `#0A192F`, `#4169E1` e branco.

Alternativas consideradas: estado global complexo (desnecessário para uma única tela); atualização otimista da exclusão (mais rápida, mas exige rollback; preferir confirmação do servidor para consistência).

### Operação e ambiente

- Docker Compose terá serviços `frontend`, `backend` e `db`, rede interna e volume persistente do PostgreSQL.
- Configurações de conexão e CORS serão variáveis de ambiente; o front-end usará URL configurável da API.
- Adicionar healthcheck do banco e dependência de inicialização para reduzir falhas de corrida no desenvolvimento.

## Risks / Trade-offs

- [Codec AVIF indisponível no runtime] → Validar a imagem base no build/CI e falhar cedo com mensagem explícita; manter adaptador para pyvips.
- [Upload inicial muito grande consome memória] → Definir limite de request operacional no proxy/servidor e processar em etapas; a regra funcional continua aceitando qualquer tamanho dentro da capacidade operacional.
- [Blobs no PostgreSQL aumentam backup e latência] → Limitar cada resultado a 1 MiB, usar pool de conexões e deixar storage externo fora do escopo inicial.
- [Exposição de conteúdo sem autenticação] → Documentar que o MVP é single-user/local e não tratar a API como pública até existir requisito de autenticação.
- [Falha entre conversão e INSERT] → Transações e rollback garantem que bytes temporários não resultem em registros incompletos.

## Migration Plan

1. Subir PostgreSQL pelo Compose e executar o script idempotente de criação da tabela.
2. Subir API e front-end, validar healthcheck, listagem, upload válido, rejeição de proporção e exclusão.
3. Para rollback, parar os serviços novos e restaurar o volume PostgreSQL anterior; não há migração destrutiva prevista.

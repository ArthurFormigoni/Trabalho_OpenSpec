## Why

Precisamos de uma galeria de fotos simples, rápida e centralizada, capaz de exibir, adicionar e remover imagens em uma única tela. A conversão para AVIF e o limite de 1 MB reduzem custo de armazenamento e transferência, enquanto a validação de proporção preserva a qualidade do mosaico.

## What Changes

- Criar uma SPA React + TypeScript + Vite com tema azul e branco baseado em shadcn/ui.
- Exibir as imagens persistidas em grid responsivo com no máximo três colunas.
- Permitir upload e exclusão de imagens, atualizando a galeria sem recarregar a página.
- Criar API FastAPI para listar, inserir e excluir imagens.
- Validar a proporção mínima `min(x,y)/max(x,y) >= 0.5` no back-end e retornar erros amigáveis ao front-end via toast.
- Converter uploads aceitos para AVIF e comprimi-los até no máximo 1 MiB antes de persistir.
- Persistir metadados e bytes na tabela PostgreSQL `image`.
- Adicionar configuração Docker Compose para front-end, back-end e PostgreSQL.

## Capabilities

### New Capabilities

- `photo-gallery`: Interface da galeria, upload, exclusão, carregamento inicial e tratamento de erros.
- `image-processing-api`: Contrato da API, validação de proporção, conversão/compressão AVIF e persistência das imagens.

### Modified Capabilities

Nenhuma.

## Impact

- Novo front-end React/Vite e novo back-end FastAPI/Python 3.11.
- Novos endpoints `GET /images`, `POST /images` e `DELETE /images/{id}`.
- Novo schema PostgreSQL para armazenamento binário de imagens e metadados.
- Novas dependências de processamento de imagem, acesso ao PostgreSQL e componentes de UI.
- Dockerfiles e `docker-compose.yml` para executar todos os serviços localmente.

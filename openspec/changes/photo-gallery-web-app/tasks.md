## 1. Estrutura e ambiente

- [ ] 1.1 Criar a estrutura de diretórios do front-end React/Vite e do back-end FastAPI com arquivos de configuração, verificando que ambos iniciam em modo desenvolvimento.
- [ ] 1.2 Adicionar dependências de UI, HTTP, banco e processamento AVIF; verificar instalação limpa no Node e no Python 3.11.2.
- [ ] 1.3 Criar `.env.example`, Dockerfiles e `docker-compose.yml` com serviços frontend/backend/db, volume PostgreSQL, rede, CORS e healthcheck; verificar `docker compose config`.

## 2. Banco e API base

- [ ] 2.1 Implementar conexão, sessão/transação e script idempotente para a tabela `image` com os checks de dimensões, tamanho e bytes; verificar criação em banco vazio.
- [ ] 2.2 Definir modelos de resposta sem expor diretamente o blob e endpoint de conteúdo AVIF por identificador; verificar `Content-Type: image/avif` para um registro de teste.
- [ ] 2.3 Implementar `GET /images` com resposta vazia e com registros; verificar os cenários da especificação por testes de API.

## 3. Processamento e persistência de imagens

- [ ] 3.1 Implementar decodificação segura, leitura de dimensões e cálculo `min(x,y)/max(x,y)`; verificar que proporção menor que 0.5 retorna HTTP 400 antes do INSERT.
- [ ] 3.2 Implementar conversão para AVIF com tentativa determinística de qualidade e redução de dimensões; verificar que o resultado persistido nunca excede 1048576 bytes.
- [ ] 3.3 Implementar `POST /images` com transação, persistência de `size_x`, `size_y`, `filesize_bytes` e `image_bytes`; verificar upload PNG/JPEG/WEBP válido, arquivo inválido e erro sem registro parcial.
- [ ] 3.4 Implementar `DELETE /images/{id}` com 404 para identificador inexistente; verificar remoção do registro e bytes usando testes de API.

## 4. Interface da galeria

- [ ] 4.1 Configurar tema shadcn/ui com tokens azul-marinho `#0A192F`, azul-royal `#4169E1` e branco; verificar renderização da tela única sem rotas adicionais.
- [ ] 4.2 Implementar carregamento inicial via `GET /images`, estado vazio, loading e erro; verificar que a coleção retornada aparece após abrir a página.
- [ ] 4.3 Implementar grid responsivo limitado a três colunas, cards com imagem AVIF e ação de apagar; verificar comportamento em larguras móvel, média e desktop.
- [ ] 4.4 Implementar seletor “Adicionar Imagem”, envio multipart e atualização da galeria após sucesso; verificar que o item novo aparece sem reload.
- [ ] 4.5 Implementar toast no canto inferior direito para erro de proporção e demais falhas de upload/exclusão; verificar mensagem retornada pela API.

## 5. Integração e verificação

- [ ] 5.1 Adicionar testes automatizados para API e processamento cobrindo listagem, upload válido, limite AVIF, proporção inválida, arquivo inválido e exclusão.
- [ ] 5.2 Executar lint, typecheck, testes front-end e build de produção; verificar que todos passam sem warnings bloqueantes.
- [ ] 5.3 Executar o fluxo completo em Docker Compose (subir, criar, listar, visualizar e excluir imagem) e documentar comandos de execução no README.

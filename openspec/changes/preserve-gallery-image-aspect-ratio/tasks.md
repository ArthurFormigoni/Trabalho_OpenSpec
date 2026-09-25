## 1. Layout proporcional

- [x] 1.1 Ajustar o componente de card para calcular uma razão visual segura a partir de `size_x` e `size_y`, com fallback quadrado para dados ausentes; verificar retrato, paisagem e quadrado em uma renderização da galeria.
- [x] 1.2 Remover o enquadramento que força cards quadrados e trocar o estilo da imagem para preservar o conteúdo completo sem `object-fit: cover`; verificar que nenhum estilo do card aplica corte ou distorção.
- [x] 1.3 Manter o grid responsivo com no máximo três colunas e espaços neutros quando necessário; verificar o layout em larguras móvel, média e desktop.

## 2. Acessibilidade e interação

- [x] 2.1 Reposicionar a ação de apagar em uma camada independente, com foco visível, contraste e nome acessível; verificar que a ação continua disponível em imagens retrato e paisagem.
- [x] 2.2 Preservar loading, empty state, upload, exclusão e toast após a alteração do layout; verificar que nenhuma ação depende de uma área cortada da imagem.
- [x] 2.3 Invalidar conteúdo cacheado ao substituir uma imagem, versionando a URL pelos bytes e configurando cabeçalhos de cache; verificar exclusão, novo upload e exibição dos bytes novos.

## 3. Verificação

- [x] 3.1 Adicionar teste de componente ou verificação automatizada para imagens retrato, paisagem e quadradas; verificar dimensões proporcionais e ausência de `object-fit: cover`.
- [ ] 3.2 Executar lint, typecheck e build do frontend; verificar que a galeria continua compilando e mantendo no máximo três colunas.

## Why

A galeria precisa manter o mosaico visualmente uniforme, com todos os cards no mesmo formato, mas sem remover partes das imagens. O enquadramento deve ser padronizado por fora e preservar o conteúdo original por dentro.

## What Changes

- Padronizar todos os cards da galeria em um único formato visual, assumindo o formato quadrado já usado pelo mosaico.
- Exibir cada imagem inteira dentro do card, sem corte; imagens não quadradas poderão ser estiradas para preencher o formato uniforme.
- Usar preenchimento neutro (`letterbox`) nas áreas que sobrarem para imagens retrato ou paisagem.
- Manter o grid responsivo com no máximo três colunas e as ações atuais de upload e exclusão.
- Adicionar testes para garantir formato uniforme, preenchimento completo e ausência de corte.

## Capabilities

### New Capabilities

- `uniform-gallery-frames`: Cards com formato uniforme e imagens internas completas, sem crop.

### Modified Capabilities

Nenhuma.

## Impact

- Alteração no componente visual e no CSS dos cards da galeria.
- O contrato de dimensões da API continuará sendo usado para renderizar a imagem, mas o frame externo será uniforme.
- Novos testes de layout para imagens retrato, paisagem e quadradas.

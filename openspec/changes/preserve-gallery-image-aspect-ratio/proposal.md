## Why

As imagens estão sendo exibidas em cards quadrados com `object-fit: cover`, o que corta partes das fotos no mosaico. A galeria precisa preservar a imagem inteira e continuar responsiva, mesmo quando as dimensões e orientações forem diferentes.

## What Changes

- Remover o comportamento de corte visual dos cards da galeria.
- Preservar a proporção original de cada imagem durante a exibição.
- Ajustar o layout do mosaico para acomodar imagens retrato, paisagem e quadradas sem distorção nem perda de conteúdo.
- Manter o limite de no máximo três colunas e a ação de exclusão sobre cada imagem.
- Adicionar testes visuais/automatizados para confirmar que imagens não usam recorte nem deformação.

## Capabilities

### New Capabilities

- `image-aspect-ratio-display`: Exibição integral, sem corte ou distorção, das imagens em diferentes proporções.

### Modified Capabilities

Nenhuma. Não existe ainda uma especificação principal arquivada para modificar; esta mudança documenta a nova garantia de exibição.

## Impact

- Alterações no componente visual dos cards e no CSS do grid do frontend.
- Possível ajuste do contrato de dados exibidos para preservar dimensões originais no cálculo do layout.
- Novos testes de UI e critérios de validação visual.

## Context

O mosaico precisa voltar a ter cards uniformes, mas o uso de `object-fit: cover` não é aceitável porque elimina conteúdo. A solução deve separar o formato do frame externo da forma como a imagem é ajustada internamente.

## Goals / Non-Goals

**Goals:**

- Usar cards quadrados uniformes em todas as larguras.
- Mostrar 100% dos pixels de cada imagem preenchendo todo o card.
- Aceitar distorção proporcional quando a imagem original não for quadrada, conforme decisão explícita do usuário.
- Preservar no máximo três colunas e a ação de exclusão.

**Non-Goals:**

- Alterar imagens no backend ou recodificar os arquivos.
- Fazer crop automático, preenchimento inteligente ou edição manual.
- Alterar a validação de proporção ou o cache de conteúdo.

## Decisions

- Restaurar `aspect-ratio: 1 / 1` no frame externo `.image-card`.
- Definir a imagem com `width: 100%`, `height: 100%` e `object-fit: fill`. Assim o frame é uniforme e toda a imagem ocupa o card sem crop, com possível distorção em imagens não quadradas.
- Manter `overflow: hidden` apenas para respeitar o raio do card; como o ajuste será `contain`, isso não remove pixels da imagem.
- Manter a ação de apagar como overlay independente, com `aria-label` e foco visível.
- Testar o CSS e o layout com imagens retrato, paisagem e quadradas, verificando a presença de `aspect-ratio: 1 / 1` e `object-fit: contain`, e a ausência de `object-fit: cover`.

Alternativa considerada: cards com altura variável proporcional à imagem. Essa abordagem preserva conteúdo, mas não atende ao requisito de formato uniforme do mosaico.

## Risks / Trade-offs

- [Distorção em imagens não quadradas] → Documentar o comportamento como requisito explícito e manter o redimensionamento limitado ao card.
- [Imagens muito pequenas dentro do frame] → Aplicar `contain` sem ampliar além dos limites do card; manter dimensões originais para o navegador.
- [Overlay sobre a imagem] → Mostrar por hover/foco e manter contraste, sem cobrir permanentemente uma área relevante.

## Migration Plan

1. Alterar somente o CSS do card e, se necessário, o componente visual.
2. Executar a verificação automatizada de layout e o build do frontend.
3. Reverter apenas os estilos se a inspeção visual revelar problemas, sem modificar os bytes persistidos.

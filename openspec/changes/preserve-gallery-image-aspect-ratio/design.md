## Context

O frontend atual usa cards quadrados e `object-fit: cover`, o que é adequado para thumbnails uniformes, mas remove conteúdo das imagens. A API já persiste as dimensões originais (`size_x` e `size_y`), permitindo que a interface calcule uma proporção confiável.

## Goals / Non-Goals

**Goals:**

- Exibir todas as imagens sem corte ou distorção.
- Preservar um grid responsivo com no máximo três colunas.
- Manter ações de exclusão e acessibilidade independentemente da orientação da imagem.
- Cobrir o comportamento com teste de UI ou verificação automatizada de estilos.

**Non-Goals:**

- Alterar a validação de proporção mínima do backend.
- Recortar, editar ou gerar novas versões das imagens.
- Reordenar a galeria ou alterar o limite de três colunas.

## Decisions

- Trocar o enquadramento quadrado obrigatório por uma área cujo `aspect-ratio` derive de `size_x / size_y`, com limites de segurança para evitar cards extremos.
- Usar `object-fit: contain` como garantia adicional de que a imagem inteira é renderizada; o fundo do card será neutro para os espaços vazios.
- Manter o grid CSS em até três colunas. A altura de cada item pode variar, permitindo que retratos e paisagens coexistam sem crop.
- Posicionar a ação de apagar em uma camada independente, com contraste e foco por teclado, sem alterar o dimensionamento da imagem.
- Versionar a URL de conteúdo pelo hash dos bytes e enviar `Cache-Control: no-store`, evitando que uma nova imagem reutilize conteúdo cacheado quando o banco local reciclar um identificador.
- Adicionar teste de componente para três proporções e uma verificação que rejeite `object-fit: cover` no card da galeria.

Alternativa considerada: usar `object-fit: contain` dentro de cards sempre quadrados. Essa opção preserva pixels, mas cria áreas vazias maiores e não aproveita as dimensões originais já disponíveis; por isso, será usada apenas como proteção junto de cards proporcionais.

## Risks / Trade-offs

- [Cards com alturas diferentes tornam o mosaico menos uniforme] → Priorizar preservação do conteúdo; usar limites de proporção e espaçamento consistente.
- [Dados antigos sem dimensões confiáveis] → Aplicar proporção quadrada como fallback e ainda usar `contain`, evitando corte.
- [Imagens muito altas ocupam muito espaço vertical] → Limitar a razão visual máxima e manter a imagem inteira com espaço neutro, sem crop.

## Migration Plan

1. Atualizar o componente e os estilos do frontend para usar as dimensões retornadas pela API.
2. Executar os testes de proporção e o build do frontend.
3. Se necessário, reverter apenas os estilos/componente sem alterar registros ou bytes já persistidos.

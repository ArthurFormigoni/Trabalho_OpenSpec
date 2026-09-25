## Purpose

Garantir que a galeria apresente cada imagem inteira, preservando sua proporção e evitando cortes, estiramentos ou deformações em qualquer tamanho de tela.

## ADDED Requirements

### Requirement: Preservar o conteúdo visual completo
O sistema SHALL exibir cada imagem sem cortar pixels, sem esticar a imagem e sem alterar sua proporção original. O card ou área visual SHALL se adaptar à proporção disponível, ou SHALL usar espaços vazios neutros quando o layout exigir uma área compartilhada.

#### Scenario: Imagem em retrato
- **WHEN** uma imagem mais alta que larga é exibida na galeria
- **THEN** toda a altura e largura da imagem permanecem visíveis, sem corte lateral ou vertical

#### Scenario: Imagem em paisagem
- **WHEN** uma imagem mais larga que alta é exibida na galeria
- **THEN** toda a imagem permanece visível, sem corte nas laterais e sem distorção

#### Scenario: Imagens com proporções diferentes no mesmo grid
- **WHEN** imagens retrato, paisagem e quadradas aparecem simultaneamente
- **THEN** cada imagem mantém sua proporção e o grid continua com no máximo três colunas

### Requirement: Manter ações acessíveis sem sobrepor conteúdo essencial
O sistema SHALL manter a ação de apagar associada a cada imagem acessível, sem esconder permanentemente partes da imagem ou depender de uma área cortada para posicionar a ação.

#### Scenario: Ação sobre uma imagem inteira
- **WHEN** o usuário move o foco ou o ponteiro sobre uma imagem
- **THEN** a ação de apagar aparece de forma identificável e a imagem continua integralmente observável

### Requirement: Validar visualmente a preservação
O sistema SHALL possuir uma verificação que cubra pelo menos uma imagem retrato, uma paisagem e uma quadrada, confirmando que o estilo de exibição não utiliza recorte ou deformação.

#### Scenario: Verificação de estilos de imagem
- **WHEN** os testes analisam a renderização dos três formatos de proporção
- **THEN** a renderização usa dimensões proporcionais e não aplica uma regra equivalente a `object-fit: cover`

### Requirement: Evitar conteúdo obsoleto após substituição
O sistema SHALL garantir que uma nova imagem não seja exibida como conteúdo antigo quando um identificador ou URL de conteúdo for reutilizado durante desenvolvimento ou persistência local.

#### Scenario: Nova imagem após exclusão
- **WHEN** uma imagem é apagada e outra é adicionada posteriormente
- **THEN** a galeria solicita e exibe os bytes da nova imagem, sem reutilizar a resposta cacheada da imagem anterior

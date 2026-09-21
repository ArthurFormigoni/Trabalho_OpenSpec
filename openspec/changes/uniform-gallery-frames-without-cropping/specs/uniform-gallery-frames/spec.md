## Purpose

Definir um mosaico visualmente uniforme no qual todos os cards tenham o mesmo formato externo, sem cortar, esticar ou deformar as imagens internas.

## ADDED Requirements

### Requirement: Usar um formato externo uniforme
O sistema SHALL renderizar todos os cards da galeria com o mesmo formato externo quadrado, independentemente das dimensões originais da imagem.

#### Scenario: Imagens com proporções diferentes
- **WHEN** a galeria contém imagens retrato, paisagem e quadradas
- **THEN** todos os cards possuem a mesma proporção externa e permanecem organizados em no máximo três colunas

### Requirement: Preencher o card sem cortar a imagem
O sistema SHALL redimensionar cada imagem para ocupar integralmente o card uniforme, sem cortar pixels. Quando a proporção original for diferente da proporção quadrada do card, o sistema poderá esticar a imagem para preencher toda a área.

#### Scenario: Imagem retrato em card quadrado
- **WHEN** uma imagem mais alta que larga é exibida
- **THEN** toda a imagem ocupa o card quadrado sem corte, mesmo que seja redimensionada para a proporção do card

#### Scenario: Imagem paisagem em card quadrado
- **WHEN** uma imagem mais larga que alta é exibida
- **THEN** toda a imagem ocupa o card quadrado sem corte, mesmo que seja redimensionada para a proporção do card

#### Scenario: Imagem quadrada em card quadrado
- **WHEN** uma imagem quadrada é exibida
- **THEN** ela preenche o card sem espaços adicionais, corte ou deformação

### Requirement: Preservar interação e acessibilidade
O sistema SHALL manter a ação de apagar visível e acessível em cada card sem alterar o formato uniforme nem ocultar conteúdo essencial da imagem.

#### Scenario: Exclusão em qualquer orientação
- **WHEN** o usuário navega por teclado ou aponta para um card
- **THEN** a ação de apagar pode ser identificada e acionada para imagens retrato, paisagem e quadradas

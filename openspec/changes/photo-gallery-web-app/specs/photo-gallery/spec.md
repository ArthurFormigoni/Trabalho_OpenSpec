## Purpose

Oferecer uma galeria de fotos de tela única, simples e responsiva, na qual o usuário consiga visualizar, adicionar e remover imagens com feedback claro.

## ADDED Requirements

### Requirement: Exibir a galeria em uma única tela
O sistema SHALL carregar e exibir todas as imagens cadastradas em um mosaico responsivo com no máximo três colunas, usando a identidade visual azul-marinho, azul-royal e branco.

#### Scenario: Carregamento inicial com imagens
- **WHEN** o usuário abre a tela principal
- **THEN** o sistema busca as imagens cadastradas e exibe cada uma no mosaico

#### Scenario: Galeria vazia
- **WHEN** não existem imagens cadastradas
- **THEN** o sistema exibe um estado vazio orientando o usuário a adicionar uma imagem

### Requirement: Adicionar uma imagem
O sistema SHALL oferecer a ação “Adicionar Imagem”, permitir a seleção de formatos comuns de imagem e atualizar a galeria após uma inclusão bem-sucedida.

#### Scenario: Upload concluído
- **WHEN** o usuário seleciona uma imagem aceita e o servidor confirma o processamento
- **THEN** a nova imagem aparece na galeria sem recarregar a página

#### Scenario: Upload rejeitado por proporção
- **WHEN** o servidor rejeita a imagem por proporção inadequada
- **THEN** o sistema exibe a mensagem retornada em um toast amigável no canto inferior direito

### Requirement: Remover uma imagem
O sistema SHALL oferecer uma ação de apagar em cada item da galeria e remover o item da interface após confirmação do servidor.

#### Scenario: Exclusão concluída
- **WHEN** o usuário solicita a exclusão e o servidor confirma
- **THEN** a imagem deixa de ser exibida imediatamente na listagem atualizada

#### Scenario: Falha na exclusão
- **WHEN** o servidor não consegue excluir a imagem
- **THEN** o item permanece na galeria e o sistema informa a falha ao usuário

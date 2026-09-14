## Purpose

Definir o contrato de processamento e persistência que transforma uploads de imagem em arquivos AVIF compactos e adequados ao mosaico da galeria.

## ADDED Requirements

### Requirement: Listar imagens persistidas
A API SHALL disponibilizar `GET /images`, retornando todas as imagens persistidas com identificador, dimensões, tamanho em bytes e dados utilizáveis pelo cliente para exibição.

#### Scenario: Listagem com registros
- **WHEN** o cliente solicita `GET /images`
- **THEN** a API retorna HTTP 200 e a coleção de imagens persistidas

#### Scenario: Listagem vazia
- **WHEN** não há registros na tabela de imagens
- **THEN** a API retorna HTTP 200 com uma coleção vazia

### Requirement: Receber e processar upload
A API SHALL disponibilizar `POST /images`, aceitar formatos comuns de imagem e, após decodificar o arquivo, calcular `min(x,y)/max(x,y)`. Ela MUST rejeitar com HTTP 400 e mensagem explicativa qualquer imagem com proporção menor que 0.5. Imagens aceitas MUST ser convertidas para AVIF e persistidas com tamanho final menor ou igual a 1 MiB.

#### Scenario: Upload válido
- **WHEN** o cliente envia uma imagem decodificável com proporção igual ou superior a 0.5
- **THEN** a API converte para AVIF, persiste dimensões, bytes e tamanho, e retorna sucesso com o identificador criado

#### Scenario: Proporção inválida
- **WHEN** o cliente envia uma imagem cuja proporção calculada é menor que 0.5
- **THEN** a API retorna HTTP 400 com mensagem informando que a proporção não é adequada para o mosaico

#### Scenario: Arquivo não reconhecido
- **WHEN** o cliente envia bytes que não podem ser decodificados como imagem
- **THEN** a API retorna um erro de validação 400 sem criar registro

#### Scenario: Conversão excede o limite
- **WHEN** a imagem aceita não pode ser codificada em AVIF dentro de 1 MiB
- **THEN** a API reduz a qualidade e/ou dimensões dentro de uma política determinística ou retorna erro de processamento sem persistir bytes acima do limite

### Requirement: Excluir imagem persistida
A API SHALL disponibilizar `DELETE /images/{id}` para remover o registro identificado e seus bytes.

#### Scenario: Exclusão de registro existente
- **WHEN** o cliente solicita a exclusão de um identificador existente
- **THEN** a API remove o registro e retorna sucesso

#### Scenario: Identificador inexistente
- **WHEN** o cliente solicita a exclusão de um identificador que não existe
- **THEN** a API retorna HTTP 404 sem alterar outros registros

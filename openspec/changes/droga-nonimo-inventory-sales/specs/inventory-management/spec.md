## ADDED Requirements

### Requirement: Consultar e editar produtos do estoque

O frontend MUST exigir uma sessão autenticada para carregar e editar produtos
por meio do grupo de API de farmácia do Xano. A listagem MUST usar
`GET /produto`. A criação MUST usar `POST /produto` e a edição MUST usar
`PUT /produto/{id}`. Os dados enviados MUST incluir nome, código de barras,
preço e quantidade em estoque; `imagem_url` MUST ser enviada quando informada
ou quando uma imagem existente estiver sendo editada.

#### Scenario: Carregar estoque

- **WHEN** um funcionário autenticado abre `/estoque`
- **THEN** o frontend carrega os produtos do Xano e apresenta os dados atuais
- **AND** uma falha de rede ou resposta inválida é apresentada como erro, não
  como uma lista carregada com sucesso

#### Scenario: Criar ou editar produto

- **GIVEN** que nome, código de barras, preço e estoque são válidos
- **WHEN** o funcionário salva o formulário
- **THEN** o frontend envia os dados ao endpoint correspondente
- **AND** recarrega a lista após uma resposta de sucesso

#### Scenario: Validar dados do produto

- **WHEN** nome ou código de barras estiver vazio, preço ou estoque não for
  válido ou algum valor for negativo
- **THEN** o frontend informa o erro e não envia a gravação ao Xano

#### Scenario: Validar e persistir a URL da imagem

- **GIVEN** que o funcionário informou uma URL de imagem
- **WHEN** a URL não usar `http` ou `https`, ou não tiver um host
- **THEN** o frontend informa que a URL é inválida e não envia a gravação
- **WHEN** o Xano aceita a gravação
- **THEN** a URL é enviada em `imagem_url` e a aplicação confirma que o valor
  retornado após recarregar corresponde ao valor enviado
- **AND** se a URL não persistir, a aplicação informa explicitamente essa
  falha

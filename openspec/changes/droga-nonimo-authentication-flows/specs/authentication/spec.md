# Requisitos de autenticacao DROGA-NONIMO

## ADDED Requirements

### Requirement: Reset de senha exige verificacao de posse da conta

O frontend MUST NOT permitir uma redefinicao de senha utilizavel somente porque um e-mail informado corresponde a uma conta. A solicitacao deve enviar um magic link de uso unico ao e-mail e a pessoa deve abrir esse link para provar que controla a caixa postal. A interface MUST exibir a mesma confirmacao neutra para qualquer resposta HTTP do endpoint, sem incluir mensagens ou status que revelem se o e-mail existe. O endpoint publico Xano MUST ser ajustado para tambem normalizar a resposta HTTP e evitar enumeracao direta por clientes da API.

#### Scenario: Solicitacao para e-mail cadastrado

- **WHEN** a pessoa solicita recuperacao de senha com um e-mail cadastrado
- **THEN** o sistema envia um link de uso unico para esse e-mail
- **AND** o formulario permanece na tela de recuperacao e informa que a caixa postal deve ser verificada
- **AND** o sistema nao abre uma redefinicao autenticada apenas com base no e-mail informado

#### Scenario: Solicitacao para e-mail nao cadastrado

- **WHEN** a pessoa solicita recuperacao com um e-mail nao cadastrado
- **THEN** a resposta visivel nao revela que o e-mail nao existe
- **AND** nenhuma redefinicao autenticada e permitida
- **AND** o endpoint publico Xano retorna a resposta generica definida para a solicitacao

### Requirement: Magic link deve ser validado antes da redefinicao

O frontend MUST trocar o `magic_token` e o e-mail da URL pelo endpoint publico `POST /reset/magic-link-login`. Somente um `authToken` retornado por validacao bem-sucedida pode autorizar `POST /reset/update_password`. O token de autenticacao e as senhas MUST permanecer em estado privado do servidor Reflex.

#### Scenario: Magic link valido

- **GIVEN** que o link contem `magic_token` e e-mail validos
- **WHEN** o Xano valida o magic token e retorna `authToken`
- **THEN** o frontend permite informar e confirmar uma nova senha
- **AND** envia os dois campos exigidos ao endpoint privado usando o token como Bearer

#### Scenario: Magic link ausente, invalido ou expirado

- **WHEN** a rota de redefinicao nao recebe parametros validos ou o Xano rejeita o magic token
- **THEN** o frontend nao chama o endpoint de atualizacao de senha
- **AND** orienta a pessoa a solicitar um novo link

### Requirement: Cadastro deve criar conta por endpoint Xano

O frontend MUST enviar `name`, `email` e `password` ao endpoint `POST /auth/signup`. O cadastro so pode iniciar uma sessao se a resposta de sucesso contiver um `authToken` nao vazio.

#### Scenario: Cadastro aceito pelo Xano

- **WHEN** o Xano responde sucesso com `authToken` valido
- **THEN** o token e mantido em estado privado e o usuario segue para o painel

#### Scenario: Cadastro recusado ou sem token

- **WHEN** o Xano rejeita o cadastro ou nao retorna token valido
- **THEN** o frontend apresenta erro e nao cria uma sessao autenticada local

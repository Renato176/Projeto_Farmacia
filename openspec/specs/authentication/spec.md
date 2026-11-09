# Especificacao de autenticacao e recuperacao de senha

O frontend Reflex integra o grupo Xano `Authentication`, configurado pela variavel de ambiente `XANO_API_URL`. O valor padrao atual e `https://x8ki-letl-twmt.n7.xano.io/api:t7Ptjfi3`.

**Contrato verificado:** login `POST /auth/login`; cadastro `POST /auth/signup`; solicitacao de link `GET /reset/request-reset-link`; troca do magic token `POST /reset/magic-link-login`; redefinicao autenticada `POST /reset/update_password`.

## Purpose

Definir os comportamentos de autenticacao, cadastro e recuperacao de senha entre o frontend Reflex e o grupo Authentication do Xano.

## Requirements

### Requirement: Autenticar usuario

O frontend MUST enviar `email` e `password` ao endpoint `POST /auth/login`. Em resposta HTTP `200`, MUST extrair `authToken` do objeto JSON, mante-lo em estado privado do servidor Reflex e redirecionar para `/dashboard`. Senhas e tokens MUST NOT ficar disponiveis como variaveis publicas de estado ou ser registrados em logs.

#### Scenario: Login aceito

- **GIVEN** que o usuario informou e-mail e senha
- **WHEN** o Xano responder `200` com `authToken` nao vazio
- **THEN** o frontend armazena o token em estado privado e abre `/dashboard`

#### Scenario: Login recusado ou indisponivel

- **WHEN** o Xano rejeitar as credenciais, retornar uma resposta invalida ou a requisicao falhar
- **THEN** o frontend exibe uma mensagem de erro e nao abre o painel

### Requirement: Cadastrar usuario

O frontend MUST enviar `name`, `email` e `password` ao endpoint `POST /auth/signup`. Quando receber `200` ou `201` com `authToken` nao vazio, MUST manter o token privado e redirecionar para `/dashboard`.

#### Scenario: Cadastro aceito

- **GIVEN** que nome, e-mail e senha foram informados
- **WHEN** o Xano criar a conta e retornar um token valido
- **THEN** o frontend autentica a sessao e abre `/dashboard`

#### Scenario: Cadastro recusado ou indisponivel

- **WHEN** o Xano rejeitar os dados ou a requisicao falhar
- **THEN** o frontend exibe o erro e permanece no cadastro

### Requirement: Solicitar recuperacao de senha

O frontend MUST enviar o e-mail como query parameter ao endpoint `GET /reset/request-reset-link`. O endpoint Xano envia um link de uso unico por e-mail. A interface MUST orientar o usuario a verificar a caixa postal e abrir esse link, sem encaminhar diretamente para a pagina de redefinicao.

#### Scenario: Link solicitado

- **WHEN** o endpoint responder a solicitacao com qualquer status HTTP
- **THEN** o frontend exibe a mesma confirmacao neutra sem indicar se o e-mail esta cadastrado
- **AND** permanece na pagina de recuperacao ate que o usuario abra o link recebido

#### Scenario: Solicitacao recusada ou indisponivel

- **WHEN** o Xano retornar erro ou a requisicao falhar
- **THEN** o frontend exibe uma mensagem de falha sem indicar sucesso

### Requirement: Evitar enumeracao de contas

A interface MUST exibir a mesma confirmacao neutra para qualquer resposta HTTP do endpoint de recuperacao e MUST NOT exibir o status ou a mensagem da API. O endpoint publico Xano MUST responder de modo equivalente para e-mails cadastrados e nao cadastrados.

#### Scenario: E-mail cadastrado ou nao cadastrado

- **WHEN** uma solicitacao e feita para um e-mail cadastrado ou nao cadastrado
- **THEN** a interface exibe a mesma confirmacao neutra
- **AND** o endpoint retorna respostas equivalentes para ambos os casos

### Requirement: Validar magic link e redefinir senha

O link de recuperacao deve abrir `/redefinir-senha` com `magic_token` e `email` na query string. Ao carregar essa rota, o frontend deve enviar esses valores ao endpoint publico `POST /reset/magic-link-login`. A resposta deve conter `authToken`, que deve permanecer em estado privado e ser usado como Bearer token em `POST /reset/update_password`. A redefinicao deve enviar ambos os campos `password` e `confirm_password`, conforme o contrato Xano.

O frontend MUST validar o magic token antes de autorizar a redefinicao e manter o token de autenticacao em estado privado.

#### Scenario: Link valido

- **GIVEN** que a URL contem `magic_token` e `email`
- **WHEN** o Xano validar o token e retornar `authToken`
- **THEN** o frontend remove os parametros de uso unico da URL e exibe o formulario de redefinicao

#### Scenario: Link ausente, invalido ou expirado

- **WHEN** os parametros estiverem ausentes ou o Xano rejeitar o token
- **THEN** o frontend nao permite a alteracao de senha e orienta o usuario a solicitar outro link

#### Scenario: Senhas invalidas ou diferentes

- **WHEN** uma senha estiver vazia ou a confirmacao nao coincidir
- **THEN** o frontend mostra erro de validacao sem chamar o endpoint de atualizacao

#### Scenario: Redefinicao aceita

- **WHEN** o Xano aceitar a requisicao autenticada com `200` ou `201`
- **THEN** o frontend confirma a alteracao, limpa os campos e invalida o token temporario local

#### Scenario: Redefinicao recusada ou indisponivel

- **WHEN** o Xano retornar erro ou a requisicao falhar
- **THEN** o frontend exibe uma mensagem de falha sem comunicar sucesso

### Requirement: Destino do link de recuperacao

O endpoint Xano `GET /reset/request-reset-link` MUST gerar links para a rota Reflex `/redefinir-senha` com `magic_token` e `email`. No escopo atual de desenvolvimento local, o destino e `http://localhost:3000`. Uma implantacao publica nao faz parte deste escopo; se o frontend vier a ser publicado, o destino deve ser atualizado para a origem publica antes de habilitar a recuperacao nesse ambiente.

#### Scenario: Link direcionado ao frontend

- **WHEN** o endpoint gera um link de recuperacao
- **THEN** o link aponta para `/redefinir-senha` e inclui `magic_token` e `email`
- **AND** usa `http://localhost:3000` no ambiente local

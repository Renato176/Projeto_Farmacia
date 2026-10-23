# Especificacao de autenticacao e recuperacao de senha

O frontend Reflex integra o grupo Xano `Authentication`, configurado pela variavel de ambiente `XANO_API_URL`. O valor padrao atual e `https://x8ki-letl-twmt.n7.xano.io/api:t7Ptjfi3`.

**Contrato verificado:** login `POST /auth/login`; cadastro `POST /auth/signup`; solicitacao de link `GET /reset/request-reset-link`; troca do magic token `POST /reset/magic-link-login`; redefinicao autenticada `POST /reset/update_password`.

## Requisitos

### Requisito: Autenticar usuario

O frontend deve enviar `email` e `password` ao endpoint `POST /auth/login`. Em resposta HTTP `200`, deve extrair `authToken` do objeto JSON, mantelo em estado privado do servidor Reflex e redirecionar para `/dashboard`. Senhas e tokens nunca devem ficar disponiveis como variaveis publicas de estado ou ser registrados em logs.

#### Cenario: Login aceito

- **Dado** que o usuario informou e-mail e senha
- **Quando** o Xano responder `200` com `authToken` nao vazio
- **Entao** o frontend deve armazenar o token em estado privado e abrir `/dashboard`

#### Cenario: Login recusado ou indisponivel

- **Quando** o Xano rejeitar as credenciais, retornar uma resposta invalida ou a requisicao falhar
- **Entao** o frontend deve exibir uma mensagem de erro e nao abrir o painel

### Requisito: Cadastrar usuario

O frontend deve enviar `name`, `email` e `password` ao endpoint `POST /auth/signup`. Quando receber `200` ou `201` com `authToken` nao vazio, deve manter o token privado e redirecionar para `/dashboard`.

#### Cenario: Cadastro aceito

- **Dado** que nome, e-mail e senha foram informados
- **Quando** o Xano criar a conta e retornar um token valido
- **Entao** o frontend deve autenticar a sessao e abrir `/dashboard`

#### Cenario: Cadastro recusado ou indisponivel

- **Quando** o Xano rejeitar os dados ou a requisicao falhar
- **Entao** o frontend deve exibir o erro e permanecer no cadastro

### Requisito: Solicitar recuperacao de senha

O frontend deve enviar o e-mail como query parameter ao endpoint `GET /reset/request-reset-link`. O endpoint Xano envia um link de uso unico por e-mail; a interface deve informar ao usuario para verificar a caixa postal e abrir esse link, sem encaminhar diretamente para a pagina de redefinicao. Para nao revelar a existencia da conta, a interface deve exibir a mesma confirmacao neutra para qualquer resposta HTTP e nao deve exibir o status ou a mensagem da API. O proprio endpoint Xano ainda deve ser ajustado para responder de modo equivalente para e-mails cadastrados e nao cadastrados.

#### Cenario: Link solicitado

- **Quando** o endpoint responder a solicitacao com qualquer status HTTP
- **Entao** o frontend deve exibir a mesma confirmacao neutra sem indicar se o e-mail esta cadastrado
- **E** deve permanecer na pagina de recuperacao ate que o usuario abra o link recebido

#### Cenario: Solicitacao recusada ou indisponivel

- **Quando** o Xano retornar erro ou a requisicao falhar
- **Entao** o frontend deve exibir uma mensagem de falha sem indicar sucesso

### Requisito: Validar magic link e redefinir senha

O link de recuperacao deve abrir `/redefinir-senha` com `magic_token` e `email` na query string. Ao carregar essa rota, o frontend deve enviar esses valores ao endpoint publico `POST /reset/magic-link-login`. A resposta deve conter `authToken`, que deve permanecer em estado privado e ser usado como Bearer token em `POST /reset/update_password`. A redefinicao deve enviar ambos os campos `password` e `confirm_password`, conforme o contrato Xano.

#### Cenario: Link valido

- **Dado** que a URL contem `magic_token` e `email`
- **Quando** o Xano validar o token e retornar `authToken`
- **Entao** o frontend deve remover os parametros de uso unico da URL e exibir o formulario de redefinicao

#### Cenario: Link ausente, invalido ou expirado

- **Quando** os parametros estiverem ausentes ou o Xano rejeitar o token
- **Entao** o frontend nao deve permitir a alteracao de senha e deve orientar o usuario a solicitar outro link

#### Cenario: Senhas invalidas ou diferentes

- **Quando** uma senha estiver vazia ou a confirmacao nao coincidir
- **Entao** o frontend deve mostrar erro de validacao sem chamar o endpoint de atualizacao

#### Cenario: Redefinicao aceita

- **Quando** o Xano aceitar a requisicao autenticada com `200` ou `201`
- **Entao** o frontend deve confirmar a alteracao, limpar os campos e invalidar o token temporario local

#### Cenario: Redefinicao recusada ou indisponivel

- **Quando** o Xano retornar erro ou a requisicao falhar
- **Entao** o frontend deve exibir uma mensagem de falha sem comunicar sucesso

### Requisito: Destino do link de recuperacao

O endpoint Xano `GET /reset/request-reset-link` deve gerar links para a rota Reflex `/redefinir-senha` com `magic_token` e `email`. O destino publicado atualmente usa `http://localhost:3000` para testes locais e deve ser substituido pela URL publica do frontend antes da implantacao.

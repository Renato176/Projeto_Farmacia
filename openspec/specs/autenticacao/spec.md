# Especificação de autenticação e recuperação de senha

Esta especificação registra o comportamento atualmente implementado no frontend Reflex para login, cadastro, recuperação de senha e redefinição de senha. As chamadas usam a API Xano configurada em `XANO_API_URL`.

**Estado:** módulo testado, validado e aprovado pelo usuário em 2026-10-07; change arquivada em `openspec/changes/archive/2026-10-06-autenticacao-fluxos/`.

## Requisitos

### Requisito: Autenticar usuário

O frontend deve enviar somente os campos JSON `email` e `password` ao endpoint Xano `POST /auth/acesso`. Em resposta HTTP `200`, deve interpretar o corpo como a string do token de acesso, armazená-lo em estado privado do backend Reflex e redirecionar para `/dashboard` somente se o token for uma string não vazia. Ao carregar ou reabrir a página de login, deve limpar mensagens de erro antigas e encerrar qualquer indicador de carregamento pendente.

#### Cenário: Login aceito pela API

- **Dado** que o usuário informou e-mail e senha
- **Quando** a API responder com status `200` e retornar uma string de token não vazia
- **Então** o frontend deve redirecionar para `/dashboard`
- **E** armazenar o token em estado privado do servidor Reflex

#### Cenário: Credenciais rejeitadas

- **Dado** que a API respondeu sem um token válido ou com status diferente de `200`
- **Quando** o login for processado
- **Então** o frontend deve exibir `message` do JSON retornado pelo Xano, se disponível
- **E** se não houver mensagem, deve exibir uma mensagem padrão de credenciais inválidas (`401`) ou erro de conexão

#### Cenário: API indisponível ou erro inesperado

- **Dado** que a chamada falhou por erro de requisição ou erro inesperado
- **Quando** o login for processado
- **Então** o frontend deve exibir uma mensagem de erro
- **E** não deve redirecionar para `/dashboard` sem confirmação do backend

#### Cenário: Página carregada ou reaberta

- **Quando** a página de login for carregada ou aberta novamente
- **Então** o frontend deve limpar a mensagem de erro e encerrar o indicador de carregamento

### Requisito: Cadastrar usuário

O frontend deve enviar nome, e-mail e senha ao endpoint `POST /auth/login`, conforme a URL de cadastro fornecida para a API Xano deste projeto.

#### Cenário: Cadastro aceito pela API

- **Dado** que nome, e-mail e senha foram informados
- **Quando** a API responder com status `200` ou `201`
- **Então** o frontend deve redirecionar para `/`

#### Cenário: Cadastro recusado pela API

- **Quando** a API responder com outro status
- **Então** o frontend deve exibir a mensagem retornada pela API ou uma mensagem padrão de erro

#### Cenário: API indisponível ou erro inesperado

- **Dado** que nome, e-mail e senha não estão vazios e o e-mail contém `@`
- **Quando** a chamada falhar por erro de requisição ou erro inesperado
- **Então** o frontend deve redirecionar para `/` sem confirmação do backend

Esse fallback permite a navegação local, mas não cria uma conta no backend.

### Requisito: Solicitar recuperação de senha

O frontend deve enviar o e-mail informado como campo JSON `email` (equivalente a `{"email": self.email}`) ao endpoint `POST /esqueci-senha` da API Xano.

#### Cenário: Solicitação aceita pela API

- **Quando** a API responder com status `200` ou `201`
- **Então** o frontend deve exibir a mensagem retornada pela API ou uma mensagem padrão de sucesso
- **E** redirecionar para `/redefinir-senha`

#### Cenário: Erro na requisição

- **Quando** a chamada falhar por erro de requisição ou erro inesperado
- **Então** o frontend deve manter o usuário no formulário e exibir uma mensagem clara de erro
- **E** não deve comunicar sucesso nem redirecionar sem confirmação do backend

#### Cenário: Nova tentativa

- **Dado** que uma mensagem de resultado foi exibida em uma tentativa anterior
- **Quando** o usuário iniciar uma nova tentativa
- **Então** o estado da mensagem deve ser limpo antes da solicitação
- **E** deve ser atualizado com o resultado da nova tentativa

#### Cenário: Página carregada ou reaberta

- **Quando** a página de recuperação for carregada ou aberta novamente
- **Então** o frontend deve limpar a mensagem, remover o estado de sucesso e encerrar o indicador de carregamento

Esse fallback não comprova que instruções foram enviadas ou que foi criado um fluxo válido de recuperação no backend.

### Requisito: Redefinir senha

O frontend deve exigir que os campos de senha e confirmação estejam preenchidos e coincidam. Deve enviar a nova senha no campo JSON `password` ao endpoint `POST /authqpassword-reset`. A confirmação é usada apenas para validação no frontend.

#### Cenário: Campos vazios ou senhas diferentes

- **Quando** um dos campos estiver vazio ou as senhas forem diferentes
- **Então** o frontend deve exibir uma mensagem de validação e não enviar a solicitação à API

#### Cenário: Redefinição aceita pela API

- **Quando** a API responder com status `200` ou `201`
- **Então** o frontend deve exibir a mensagem retornada pela API ou uma mensagem padrão de sucesso

#### Cenário: Erro na requisição

- **Quando** a chamada falhar por erro de requisição
- **Então** o frontend deve exibir uma mensagem clara de falha
- **E** não deve comunicar sucesso sem confirmação do backend

#### Cenário: Página carregada ou reaberta

- **Quando** a página de redefinição for carregada ou aberta novamente
- **Então** o frontend deve limpar a mensagem, remover o estado de sucesso e encerrar o indicador de carregamento

Esse fallback não altera a senha no backend. Atualmente, a solicitação envia apenas `password`; esta especificação não pressupõe token ou outro mecanismo de validação de recuperação.

### Requisito: Exibir senha durante a redefinição

O formulário de redefinição deve permitir alternar entre texto visível e senha mascarada. A mesma opção de visibilidade se aplica ao campo de senha e ao campo de confirmação.

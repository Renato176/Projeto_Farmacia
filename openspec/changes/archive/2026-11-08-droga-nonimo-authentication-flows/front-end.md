# Front-end: fluxos de autenticacao

## Localizacao

- Login: `/`.
- Cadastro: `/register`.
- Recuperacao de senha: `/recuperar-senha`.
- Redefinicao de senha: `/redefinir-senha`.
- Implementacao Reflex: [`farmacia/farmacia.py`](../../../farmacia/farmacia.py).
- Chamadas HTTP ao Xano: [`farmacia/xano.py`](../../../farmacia/xano.py).

## Apresentacao

As telas de autenticacao compartilham um painel centralizado, com largura
maxima de 400 px, fundo escuro e cartao de formulario. A pagina de login
encaminha para cadastro e recuperacao; cadastro, recuperacao e redefinicao
oferecem retorno ao login. Os campos de senha permitem alternar a
visualizacao.

## Login e cadastro

- O login envia `email` e `password` para `POST /auth/login`. Somente uma
  resposta HTTP 200 com `authToken` nao vazio inicia a sessao e encaminha a
  pessoa para `/splash`.
- O cadastro envia `name`, `email` e `password` para `POST /auth/signup`.
  Respostas HTTP 200 ou 201 so iniciam a sessao quando incluem `authToken`
  nao vazio; em caso contrario, a interface apresenta uma mensagem de erro.
- Falhas de validacao, recusas do Xano e falhas de conexao sao exibidas no
  formulario. Senhas e token de sessao sao mantidos em campos privados do
  estado Reflex.

## Recuperacao de senha

O formulario `/recuperar-senha` recebe o e-mail e chama
`GET /reset/request-reset-link`. A resposta visivel e neutra para respostas
HTTP e falhas de conexao: informa que, se o endereco estiver cadastrado, um
link sera enviado e orienta a verificar a caixa de entrada e o spam. A
interface nao redireciona diretamente para a troca de senha nem apresenta o
status ou a resposta do endpoint.

O endpoint Xano retorna uma mensagem publica generica e envia o magic link
somente quando ha uma conta elegivel. No ambiente local, o link aponta para
`http://localhost:3000/redefinir-senha` com os parametros `magic_token` e
`email`.

## Redefinicao de senha

Ao abrir `/redefinir-senha`, o estado Reflex le `magic_token` e `email` da
URL e chama `POST /reset/magic-link-login`. Apenas um token de autenticacao
retornado pelo Xano permite enviar a redefinicao: os campos `password` e
`confirm_password` sao enviados a `POST /reset/update_password` com
autenticacao. Senhas vazias ou divergentes e links nao validados sao
rejeitados antes dessa chamada. Em caso de sucesso, a interface confirma a
alteracao e limpa as senhas e o token temporario.

## Validacao e limites

`reflex compile --dry` passou. A resposta generica do endpoint de solicitacao
foi executada no Xano com um endereco reservado `.invalid`, sem envio de
e-mail. O fluxo completo com uma conta e caixa postal reais nao foi testado;
essa validacao depende de credenciais e de uma caixa postal de teste
acessivel.

A configuracao `localhost:3000` atende ao escopo local atual. Publicacao e
dominio publico nao fazem parte desta change.

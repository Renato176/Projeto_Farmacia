# Proposta: fluxos de autenticação e recuperação de senha

## Estado

**Concluída e arquivada; aprovação confirmada novamente em 2026-10-07.** Proposta retrospectiva das alterações de autenticação já aplicadas. O usuário confirmou que cadastro de conta, login, recuperação e redefinição de senha, incluindo limpeza de estado no `on_load`, foram testados, validados e aprovados.

## Contexto

Os formulários Reflex de login, cadastro e recuperação de senha chamam a API Xano. Os fluxos precisam usar rotas próprias para cada operação, validar os campos básicos e comunicar os resultados ao usuário. Também foi solicitada uma opção para revelar a senha durante a redefinição.

## Escopo

Inclui os fluxos de:

- login em `POST /auth/acesso`, com armazenamento do token de acesso;
- cadastro em `POST /auth/login`, conforme a URL de cadastro fornecida para a API Xano deste projeto;
- solicitação de recuperação em `POST /esqueci-senha`;
- redefinição em `POST /authqpassword-reset`;
- alternância de visibilidade dos campos de senha na redefinição.

Arquivos envolvidos:

- `frontend/frontend/login.py`
- `frontend/frontend/register.py`
- `frontend/frontend/forgot_password.py`
- `frontend/frontend/reset_password.py`

Fora do escopo: implementar autenticação ou recuperação no backend Xano, definir autenticação de sessão, alterar o modelo de usuários ou adicionar integração financeira.

## Comportamento registrado

### Login

Enviar somente os campos JSON `email` e `password` a `/auth/acesso`. Em resposta `200`, interpretar o corpo como token de acesso; se for string não vazia, armazenar em estado privado do servidor Reflex e redirecionar para `/dashboard`. Exibir a mensagem da API ou mensagem de erro nos demais casos. Limpar mensagens antigas e o indicador de carregamento no evento `on_load` da página de login.

### Cadastro

Enviar nome, e-mail e senha a `/auth/login`. Em resposta `200` ou `201`, redirecionar para `/`. Para outras respostas, exibir a mensagem da API ou uma mensagem padrão. Em erros de requisição ou inesperados, o código redireciona para `/` quando nome, e-mail e senha estão preenchidos e o e-mail contém `@`.

### Recuperação de senha

Enviar o campo JSON `email` com o endereço informado a `/esqueci-senha`. Em resposta `200` ou `201`, exibir sucesso e redirecionar para `/redefinir-senha`. Em erro de requisição ou erro inesperado, permanecer no formulário e exibir uma mensagem clara de erro; limpar a mensagem anterior no início de cada nova tentativa e no carregamento/reabertura da página.

### Redefinição de senha

Exigir senha e confirmação preenchidas e iguais; enviar somente `password` a `/authqpassword-reset` (a confirmação é validada apenas no frontend). Em resposta `200` ou `201`, exibir sucesso. Em erro de requisição, exibir falha de conexão sem indicar sucesso. Os dois campos compartilham o controle para alternar entre texto visível e senha mascarada. Ao carregar ou reabrir a página, limpar a mensagem e reiniciar os indicadores de resultado/carregamento.

## Critérios de aceite

- Cada fluxo envia os campos descritos ao endpoint correspondente.
- Respostas de sucesso e erro da API são tratadas conforme registrado nesta proposta.
- Os campos de senha da redefinição podem ser alternados entre visíveis e mascarados.
- Os fluxos apresentam feedback de validação quando os campos obrigatórios estão vazios ou as senhas não coincidem.
- Os comportamentos de fallback são revisados explicitamente antes de serem considerados aceitáveis, pois podem aparentar sucesso sem operação correspondente no backend.

## Validação registrada

A compilação Python dos módulos Reflex e a importação do app passaram nas validações locais. Testes locais com respostas simuladas cobriram payloads, endpoints, token de login, mensagens de erro, validação de redefinição e handlers de limpeza `on_load`. Em 2026-10-07, o usuário confirmou que cadastro de conta, login, recuperação e redefinição foram testados ponta a ponta, funcionaram e foram aprovados; esta validação ponta a ponta é registrada com base nessa confirmação.

## Riscos e dependências

- O cadastro usa a rota `/auth/login` com os campos `name`, `email` e `password`, conforme configuração atual. Seu nome e contrato foram confirmados como funcionais pelo teste ponta a ponta relatado pelo usuário.
- O token de login é armazenado em estado privado do servidor Reflex; outros endpoints ainda precisam receber esse token caso requeiram autenticação.
- Os fluxos de login, cadastro, recuperação e redefinição foram confirmados como funcionais pelo usuário em 2026-10-07.

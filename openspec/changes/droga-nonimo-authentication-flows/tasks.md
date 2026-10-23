# Tarefas

- [x] Verificar no Xano os contratos de login, cadastro e recuperacao de senha.
- [x] Centralizar chamadas HTTP ao grupo de API Xano em `farmacia/xano.py`.
- [x] Integrar o login com `POST /auth/login` e manter o token privado no servidor Reflex.
- [x] Integrar o cadastro com `POST /auth/signup` sem criar sessao sem token valido.
- [x] Integrar a solicitacao de recuperacao com `GET /reset/request-reset-link`.
- [x] Exibir uma confirmacao neutra na interface sem revelar o resultado de busca do e-mail.
- [x] Validar o magic link usando `POST /reset/magic-link-login`.
- [x] Redefinir a senha com `POST /reset/update_password`, Bearer token e os campos exigidos.
- [x] Criar e conectar as rotas Reflex de cadastro, recuperacao e redefinicao.
- [x] Atualizar e publicar no Xano o destino local do magic link.
- [x] Validar a compilacao com `reflex compile --dry`.
- [ ] Testar o fluxo ponta a ponta usando conta e caixa postal de teste.
- [ ] Normalizar no Xano a resposta publica para nao diferenciar e-mail cadastrado de nao cadastrado.
- [ ] Substituir `http://localhost:3000` pela URL publica do frontend antes da implantacao.

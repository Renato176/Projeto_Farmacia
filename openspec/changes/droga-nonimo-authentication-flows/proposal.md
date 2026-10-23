# Integrar fluxos de autenticacao DROGA-NONIMO com Xano

## Motivo

As telas de login, cadastro e recuperacao precisam usar os endpoints reais do grupo `Authentication` no Xano. A redefinicao de senha deve provar que a pessoa controla a conta, em vez de confiar apenas em um e-mail digitado.

## Alteracoes

- Integrar login e cadastro aos endpoints Xano existentes, mantendo senhas e tokens apenas no estado privado do servidor Reflex.
- Integrar solicitacao de recuperacao por e-mail com o magic link de uso unico do Xano.
- Validar o magic token antes de permitir a troca da senha e enviar a redefinicao autenticada com os campos exigidos pelo Xano.
- Usar as rotas Reflex para navegacao entre login, cadastro, recuperacao e redefinicao.
- Fazer o magic link retornar ao frontend local durante desenvolvimento e documentar a troca para a URL publicada antes da implantacao.

## Decisao de seguranca

Informar um e-mail existente nao comprova que a pessoa controla essa conta. Portanto, o frontend nao deve liberar nem abrir uma redefinicao utilizavel apenas por reconhecer o e-mail. A pessoa deve abrir o link de uso unico enviado para a caixa postal; o Xano valida esse link e concede uma autenticacao temporaria para redefinir a senha. As mensagens de recuperacao nao devem revelar se um e-mail esta cadastrado.

## Escopo

Os endpoints de autenticacao ja existentes no Xano sao reutilizados; nenhum endpoint novo ou tabela e necessario. O magic link aponta atualmente para `http://localhost:3000`, adequado apenas para desenvolvimento local.

## Estado

As integracoes e rotas foram implementadas e a compilacao Reflex foi validada. A interface exibe a mesma confirmacao neutra para qualquer resposta HTTP da solicitacao de recuperacao; detalhes de erro da API nao sao mostrados ao usuario. O destino local do magic link foi publicado no Xano. A normalizacao da resposta HTTP no proprio endpoint publico, o teste ponta a ponta com uma caixa postal de teste e a troca pela URL publica continuam pendentes.

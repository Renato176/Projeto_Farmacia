# Integrar fluxos de autenticacao DROGA-NONIMO com Xano

## Motivo

As telas de login, cadastro e recuperacao precisam usar os endpoints reais do grupo `Authentication` no Xano. A redefinicao de senha deve provar que a pessoa controla a conta, em vez de confiar apenas em um e-mail digitado.

## Alteracoes

- Integrar login e cadastro aos endpoints Xano existentes, mantendo senhas e tokens apenas no estado privado do servidor Reflex.
- Integrar solicitacao de recuperacao por e-mail com o magic link de uso unico do Xano.
- Validar o magic token antes de permitir a troca da senha e enviar a redefinicao autenticada com os campos exigidos pelo Xano.
- Usar as rotas Reflex para navegacao entre login, cadastro, recuperacao e redefinicao.
- Fazer o magic link retornar ao frontend local durante desenvolvimento. Publicacao e URL publica nao fazem parte do escopo atual.

## Decisao de seguranca

Informar um e-mail existente nao comprova que a pessoa controla essa conta. Portanto, o frontend nao deve liberar nem abrir uma redefinicao utilizavel apenas por reconhecer o e-mail. A pessoa deve abrir o link de uso unico enviado para a caixa postal; o Xano valida esse link e concede uma autenticacao temporaria para redefinir a senha. As mensagens de recuperacao nao devem revelar se um e-mail esta cadastrado.

## Escopo

Os endpoints de autenticacao ja existentes no Xano sao reutilizados; nenhum endpoint novo ou tabela e necessario. O magic link aponta atualmente para `http://localhost:3000`, adequado apenas para desenvolvimento local.

## Estado

As integracoes e rotas foram implementadas e a compilacao Reflex foi validada. A interface exibe a mesma confirmacao neutra para qualquer resposta HTTP da solicitacao de recuperacao; detalhes de erro da API nao sao mostrados ao usuario. A resposta generica do endpoint publico foi normalizada, publicada e validada com um endereco reservado `.invalid`, sem envio de e-mail. O magic link permanece configurado para `http://localhost:3000`, conforme o escopo de uso local. Publicacao do frontend, URL publica e teste ponta a ponta com uma caixa postal real nao fazem parte do escopo atual.

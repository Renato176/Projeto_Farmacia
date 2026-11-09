# Front-end: estoque e vendas

## Localização

- Gestão de Estoque: rota protegida `/estoque`.
- Vendas: rota protegida `/vendas`.
- Implementação Reflex: [`farmacia/farmacia.py`](../../../farmacia/farmacia.py).
- Estado, validações e chamadas ao Xano: `LoginState`.
- Composição das telas: `stock_page()` e `sales_page()`.

## Gestão de Estoque

A tela carrega os produtos do Xano e oferece busca, filtros de categoria,
indicação de estoque baixo e formulário de criação e edição. O formulário
inclui nome, código de barras, preço, quantidade, categoria opcional e URL da
imagem, com pré-visualização quando a URL é válida.

Nome e código são obrigatórios; preço e quantidade devem ser valores não
negativos. A URL informada deve usar `http` ou `https` e conter um host. Ao
salvar, a aplicação envia os campos para `POST /produto` ou
`PATCH /produto/{produto_id}`, recarrega o produto e compara a URL retornada
com a informada. Se a imagem não tiver sido persistida, a tela apresenta um
erro em vez de sinalizar sucesso.

## Catálogo, carrinho e clientes

A tela de Vendas carrega produtos, clientes e histórico do Xano e apresenta os
produtos em cartões com imagem, preço e estoque. A busca e os filtros ajudam a
localizar itens. O funcionário pode adicionar produtos disponíveis, ajustar ou
remover quantidades e abrir o carrinho pelo resumo flutuante. A quantidade no
carrinho não pode exceder o saldo carregado.

O carrinho permite continuar sem cliente ou selecionar um cliente cadastrado.
Também oferece um formulário de cadastro com nome, CPF de 11 dígitos e
telefone; a aplicação rejeita campos obrigatórios vazios e CPF duplicado na
lista carregada. O cadastro usa `POST /cliente`, mas esse endpoint consta no
relatório do Xano como draft não publicado.

Para clientes com `esta_registrado = true`, a interface calcula e exibe um
desconto demonstrativo de 14%. As opções dinheiro, PIX, crédito e débito são
apenas formas registradas na interface; não há integração com gateway de
pagamento.

## Histórico e finalização

O histórico fica disponível na tela de Vendas e é carregado por `GET /venda`.
O evento de finalização envia `itens` com `produto_id` e `quantidade`,
`cliente_id` opcional e `forma_pagamento` para `POST /venda/finalizar`. O
frontend não envia preço nem total como fonte confiável.

O carrinho só é limpo quando a resposta contém `success: true` e um `venda.id`
inteiro positivo; após essa confirmação, o frontend atualiza catálogo e
histórico. Erros HTTP, de rede, resposta incompleta ou inválida mantêm o
carrinho e apresentam uma mensagem. Em caso de falha de rede, a interface
orienta conferir o histórico antes de tentar novamente, pois não é possível
determinar pelo cliente se uma operação remota chegou a ser processada.

## Limites e validação

O endpoint Xano `POST /venda/finalizar` (`4119638`) está autenticado, mas
permanece sem inputs, funções ou resposta configurados e não foi publicado.
Assim, o fluxo frontend está preparado, mas não conclui uma venda real nem
baixa estoque no ambiente live. Também não foram executados testes ponta a
ponta nem testes de persistência de `imagem_url`, rollback ou concorrência no
Xano.

O módulo Reflex foi validado com `python -m compileall -q farmacia/farmacia.py`,
e as alterações passaram por `git diff --check`. Essas verificações não
substituem a validação do endpoint e dos fluxos com dados de teste no Xano.

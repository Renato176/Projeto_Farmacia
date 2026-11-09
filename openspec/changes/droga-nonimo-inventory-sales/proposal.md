# Banco de dados, estoque e vendas

## Motivo

As alterações feitas no Xano e nas telas de estoque e vendas precisam ficar
registradas juntas em uma Change OpenSpec. O Xano já possui as tabelas e APIs
da farmácia; o frontend já apresenta catálogo, carrinho, identificação de
clientes e histórico. A interface chama `POST /venda/finalizar`, mas o
endpoint ainda não está configurado nem publicado e, portanto, não persiste
vendas nem atualiza o estoque.

## Alterações registradas

- **Xano:** tabelas `cliente`, `produto`, `venda` e `item_venda`; o campo
  opcional `produto.imagem_url`; o enum `venda.forma_pagamento`; endpoints de
  produtos, clientes e histórico de vendas.
- **Estoque:** tela protegida com busca, listagem de produtos, sinalização de
  estoque baixo, cadastro e edição, incluindo pré-visualização e persistência
  da foto por URL.
- **Vendas:** catálogo visual com fotos, preço e saldo; carrinho flutuante com
  ajuste de quantidades; identificação/cadastro de cliente; desconto
  demonstrativo de 14%; histórico em janela própria. O frontend também prepara a
  requisição de finalização e mantém o carrinho quando o Xano não confirma a
  venda.
- **Pendente:** uma operação de finalização atômica que grave venda e itens e
  desconte o estoque.

O detalhamento do contrato de dados está em
[`pharmacy-database`](./specs/pharmacy-database/spec.md); os comportamentos
visuais estão em [`stock-sales-interface`](./specs/stock-sales-interface/spec.md)
e em [`front-end.md`](./front-end.md).

## Limites

As referências de tabela entre venda, usuário, cliente e itens foram
configuradas e conferidas no Xano; os detalhes estão no relatório do projeto.
O seletor de forma de pagamento é demonstrativo; esta Change não integra
adquirentes ou gateways. Até a finalização transacional, o carrinho não
representa uma venda concluída.

## Estado

As alterações de schema e endpoints no Xano estão registradas em
[`docs/relatorio_xano_droga_nonimo.md`](../../../docs/relatorio_xano_droga_nonimo.md);
as telas correspondentes estão em `farmacia/farmacia.py`. O relatório confirma
a configuração de `imagem_url` nos endpoints, mas não relata uma chamada real
que valide sua persistência. O evento frontend chama `POST /venda/finalizar`,
mas o endpoint Xano `4119638` continua sem inputs, funções ou resposta e não
está publicado. A tela exige confirmação estruturada antes de limpar o
carrinho; a finalização real, as validações no Xano e as demais pendências
continuam em `tasks.md`.

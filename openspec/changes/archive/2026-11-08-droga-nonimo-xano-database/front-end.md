# Front-end: referências do banco de vendas

## Localização

- Tela autenticada de vendas: `/vendas`.
- Implementação Reflex: [`farmacia/farmacia.py`](../../../farmacia/farmacia.py).
- Carregamento do histórico: `LoginState.load_sales()`.
- Apresentação de cada venda: `sale_row()`.

## Relações configuradas

O schema Xano agora relaciona:

- `venda.usuario_id` com `user`.
- `venda.cliente_id` com `cliente`.
- `item_venda.venda_id` com `venda`.
- `item_venda.produto_id` com `produto`.

As relações dão suporte ao vínculo dos registros no banco. Esta alteração não
adiciona telas, endpoints ou ações de criação de vendas ao frontend.

## Comportamento atual

A tela carrega o histórico autenticado por `GET /venda` junto com produtos e
clientes. Cada linha exibe o ID da venda, `cliente_id`, total, forma de
pagamento e data. O frontend ainda não carrega nem exibe itens de venda e não
finaliza o carrinho com uma gravação no Xano; o checkout transacional e a baixa
de estoque continuam pendentes.

Antes de ampliar o histórico ou implementar a finalização, conferir a forma
dos valores retornados pelos endpoints após a mudança para referências de
tabela. A linha atual espera `cliente_id` para exibição e deve ser adaptada se
o endpoint passar a retornar um objeto de referência em vez do ID.

## Validação

Os quatro destinos das referências e os índices ascendentes foram conferidos
no schema `live` do workspace `169234-0`. Nenhum registro de venda ou item foi
criado ou alterado. Como esta entrega altera o schema e não o código Reflex,
não houve mudança visual nem teste de checkout.

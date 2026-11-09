# Catálogo hierárquico de categorias

## Motivo

A aplicação precisa de um catálogo pesquisável e persistente que permita
classificar produtos e manter os departamentos e subcategorias pelo frontend.

## O que muda

- Manter a rota protegida `/categorias`, agrupando departamentos e
  subcategorias do Xano e oferecendo busca local nos registros carregados.
- Persistir o catálogo na tabela `categoria` e usar os endpoints autenticados
  para consultar e gerenciar categorias.
- Disponibilizar no frontend criação, edição, ativação/desativação e exclusão
  de departamentos e subcategorias.
- Associar opcionalmente cada produto a uma categoria por
  `produto.categoria_id`.
- Usar essa associação no formulário de produto e nos filtros de Estoque e
  Vendas; selecionar um departamento também inclui suas subcategorias.
- Adaptar a taxonomia inspirada na página pública de
  [categorias da Drogasil](https://www.drogasil.com.br/categorias) ao projeto,
  sem alegar afiliação ou integração com esse site.

## Limites

A exclusão de categorias pode ser impedida por referências a produtos ou
subcategorias; a interface apresenta a mensagem retornada pelo Xano. As
relações de vendas e itens de venda não fazem parte desta alteração e
continuam pendentes de configuração como referências de tabela.

## Estado

No workspace Xano `169234-0`, branch `v1`, fonte `live`, a tabela
`categoria` (`913434`) contém 9 departamentos e 49 subcategorias. A referência
opcional `produto.categoria_id` aponta para essa tabela. Os endpoints
autenticados `GET`, `POST`, `PATCH`, `DELETE` e `GET por ID` de categoria estão
publicados no grupo `Farmacia` (`437376`).

O frontend implementa consulta, busca, CRUD, validação, confirmação de
exclusão e atualização da lista após sucesso. Os mapeamentos de
`POST /categoria` e `POST /produto` foram revisados e publicados
individualmente. Os drafts preexistentes `POST /cliente` (`4105447`) e
`PUT /produto/{produto_id}` (`4103438`) permaneceram intactos. Os detalhes do
schema e dos contratos estão em
[`docs/catalogo-categorias.md`](../../../docs/catalogo-categorias.md).

## Front-end

A implementação e o comportamento da interface estão descritos em
[`front-end.md`](./front-end.md). O código Reflex está em
[`farmacia/farmacia.py`](../../../farmacia/farmacia.py).

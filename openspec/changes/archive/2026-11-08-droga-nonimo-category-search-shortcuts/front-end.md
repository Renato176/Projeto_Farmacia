# Front-end: filtros de categoria em Estoque e Vendas

## Localização

- Gestão de Estoque: rota protegida `/estoque`.
- Vendas: rota protegida `/vendas`.
- Implementação Reflex: [`farmacia/farmacia.py`](../../../farmacia/farmacia.py).
- Controle compartilhado do filtro: `product_category_search_control()`.
- Estado e filtragem dos produtos: `LoginState`.

## Interface

As duas telas apresentam um seletor **Filtrar por departamento ou categoria**
junto à busca por nome ou código de barras. As opções são carregadas do
catálogo de categorias do Xano e mostram categorias ativas; subcategorias são
identificadas pelo caminho do departamento, por exemplo,
`Departamento / Categoria`.

O controle informa que o filtro usa a categoria associada ao produto e inclui
as subcategorias do departamento selecionado. Se uma categoria selecionada
não estiver disponível no catálogo carregado, a tela informa o erro e remove
a seleção inválida.

## Comportamento

- A busca textual localiza nome ou código de barras sem diferenciar caixa ou
  acentuação.
- O filtro por subcategoria mostra os produtos associados ao respectivo
  `categoria_id`.
- O filtro por departamento inclui produtos associados ao departamento ou a
  qualquer uma de suas subcategorias.
- O filtro categórico e a busca textual são aplicados em conjunto.
- Estoque e Vendas reutilizam o mesmo controle e estado do filtro.

O vínculo usado pelo filtro é `produto.categoria_id`, persistido no Xano. A
interface não infere a categoria com base no nome ou código do produto. Esta
change não cria uma tela independente de categorias.

## Validação

As tarefas de implementação e validação desta change estão concluídas. O
comportamento é implementado no código Reflex em
[`farmacia/farmacia.py`](../../../farmacia/farmacia.py); esta documentação
registra a interface e os limites do filtro.

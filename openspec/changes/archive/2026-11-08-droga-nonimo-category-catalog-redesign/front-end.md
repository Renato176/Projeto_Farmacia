# Front-end: catálogo hierárquico de categorias

## Localização

- Rota protegida: `/categorias`.
- Implementação Reflex: [`farmacia/farmacia.py`](../../../farmacia/farmacia.py).
- Composição da tela: `categories_page()`.
- Estado, busca, catálogo e operações: `LoginState`.

## Organização visual

A página organiza o catálogo em cartões de departamento. Cada cartão mostra
cor, nome, descrição, status e subcategorias; as subcategorias são apresentadas
como etiquetas com seus próprios status. O layout permite que os cartões e as
etiquetas se ajustem à largura disponível.

A taxonomia adapta ao projeto a organização usada como referência visual,
incluindo Saúde, Medicamentos, Vitaminas e Suplementos, Mamãe & Bebê, Beleza,
Beleza Premium, Cuidados Diários, Pet e Marcas Exclusivas. Categorias já
previstas no projeto, como Remédios, Fraldas, Bebidas e Produtos de Higiene,
permanecem no catálogo. A interface não sugere afiliação ou sincronização com
o site de referência.

## Busca e resultados

A busca local considera o nome e a descrição dos departamentos e o nome das
subcategorias carregadas do Xano. Uma correspondência com o departamento
mantém suas subcategorias; uma correspondência apenas com subcategorias mostra
somente as etiquetas correspondentes dentro de seus departamentos. Os
contadores acompanham os resultados filtrados, e uma busca sem correspondência
apresenta um estado vazio.

## Dados e integração

O catálogo apresentado é carregado pelo endpoint autenticado `GET /categoria`;
a taxonomia não é apresentada como persistida a partir de dados locais. Os
estados de carregamento e erro são tratados pela tela. Se o endpoint falhar ou
retornar dados inválidos, a aplicação informa o erro e não apresenta conteúdo
antigo como catálogo atual.

A associação opcional `produto.categoria_id` é oferecida nos formulários de
produto. Os filtros de Estoque e Vendas usam o vínculo persistido, incluindo
produtos de subcategorias quando o usuário filtra por departamento. A tela
também permite criar, editar, ativar/desativar e excluir categorias; os
detalhes desses fluxos estão em
[`../droga-nonimo-categories-screen/front-end.md`](../droga-nonimo-categories-screen/front-end.md).

## Validação

A implementação foi compilada e as changes OpenSpec foram validadas. Não foi
feito teste interativo de gravação no Xano `live`.

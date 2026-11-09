# category-search-shortcuts Specification

## Purpose

Define como as telas de Gestão de Estoque e Vendas filtram produtos pelas
categorias persistidas no Xano e combinam esse filtro com a busca textual.

## Requirements

### Requirement: Filtrar produtos por categoria persistida

As telas de Gestão de Estoque e Vendas MUST oferecer as categorias ativas
carregadas do Xano como filtros de produtos. A filtragem MUST usar o vínculo
persistido `produto.categoria_id`; selecionar um departamento MUST incluir os
produtos vinculados às suas subcategorias. A busca textual MUST continuar
localizando nome ou código de barras sem diferenciar maiúsculas de minúsculas
ou acentos.

#### Scenario: Selecionar uma subcategoria

- **WHEN** o funcionário seleciona uma subcategoria no filtro
- **THEN** Estoque e Vendas exibem produtos associados à categoria selecionada

#### Scenario: Selecionar um departamento

- **WHEN** o funcionário seleciona um departamento no filtro
- **THEN** Estoque e Vendas exibem produtos associados ao departamento ou a
  qualquer uma de suas subcategorias

#### Scenario: Combinar filtro categórico e busca textual

- **WHEN** o funcionário seleciona uma categoria e informa texto de busca
- **THEN** somente produtos que correspondem à categoria e ao texto são exibidos
- **AND** a busca textual considera nome e código de barras sem diferenciar
  caixa ou acentuação

### Requirement: Mostrar somente vínculos categóricos explícitos

A interface MUST usar a associação `produto.categoria_id` carregada do Xano e
MUST NOT inferir ou apresentar uma categoria como dado oficial de um produto
sem vínculo explícito.

#### Scenario: Filtrar produtos sem inferir categorias

- **WHEN** o funcionário aplica um filtro categórico
- **THEN** a lista considera somente os IDs de categoria associados aos
  produtos no Xano
- **AND** produtos sem associação não são classificados por nome ou código

### Requirement: Manter os filtros nas telas operacionais

Os filtros de categoria MUST estar disponíveis nas telas de Gestão de Estoque
e Vendas, sem exigir uma rota independente de gerenciamento de categorias.

#### Scenario: Filtrar produtos sem navegar para outra tela

- **WHEN** o funcionário consulta o estoque ou o catálogo de vendas
- **THEN** pode carregar as categorias ativas e filtrar os produtos na mesma
  tela operacional

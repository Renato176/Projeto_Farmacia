# Filtros de categoria em Estoque e Vendas

## Motivo

A tela independente de categorias adicionava uma etapa desnecessária para
localizar produtos. Os filtros por departamento e subcategoria devem estar
diretamente nas telas de Gestão de Estoque e Vendas e usar o vínculo de
categoria persistido no produto.

## O que muda

- Disponibilizar categorias ativas como opções de filtro nas telas de Gestão
  de Estoque e Vendas.
- Filtrar pela associação persistida `produto.categoria_id`; selecionar um
  departamento inclui produtos vinculados às suas subcategorias.
- Manter a busca textual de produtos por nome ou código de barras, sem
  diferenciar maiúsculas de minúsculas ou acentos.

O gerenciamento de categorias não exige uma tela independente: os filtros
usam as categorias carregadas do Xano nas telas operacionais.

## Limites

Esta mudança não cria uma tela independente de categorias e não classifica
produtos por inferência. O filtro só considera a associação explícita
`produto.categoria_id` retornada pelo Xano; a busca textual continua limitada
ao nome e ao código de barras.

## Estado

Implementada. As telas de Estoque e Vendas carregam categorias ativas do Xano
e filtram produtos pela categoria associada, incluindo subcategorias quando
um departamento é selecionado. A busca textual por nome ou código de barras
permanece disponível e ignora caixa e acentuação.

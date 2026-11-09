# Reorganização visual do catálogo de categorias

## Motivo

A primeira versão da tela `/categorias` apresentava poucos grupos em cartões
simples. Para facilitar a navegação por um catálogo de farmácia mais amplo, a
organização foi expandida para departamentos e subcategorias, usando como
referência visual a página pública de
[categorias da Drogasil](https://www.drogasil.com.br/categorias).

## O que muda

- Organizar o conteúdo por departamentos, com descrição e subcategorias.
- Incluir Saúde, Medicamentos, Vitaminas e Suplementos, Mamãe & Bebê, Beleza,
  Beleza Premium, Cuidados Diários, Pet e Marcas Exclusivas.
- Preservar grupos já previstos neste projeto, como Remédios, Fraldas, Bebidas
  e Produtos de Higiene, como subcategorias.
- Permitir busca local por departamento, descrição ou subcategoria, filtrando
  subcategorias e atualizando as contagens exibidas.
- Apresentar os departamentos em cartões responsivos, mantendo navegação e
  proteção da rota existentes.
- Oferecer no frontend o cadastro, a edição, a ativação/desativação e a
  exclusão de departamentos e subcategorias usando os endpoints autenticados
  do Xano.

## Limites

A referência é somente de organização. A taxonomia foi adaptada ao projeto e
não implica vínculo, afiliação ou integração com a Drogasil. A exclusão de
categorias ainda associadas a produtos ou subcategorias depende das regras de
integridade do Xano e deve exibir a falha retornada pela API.

## Estado

A reorganização visual, a busca hierárquica e os estados de resultado estão
implementados na tela protegida `/categorias`. Após a confirmação do schema e
dos contratos no Xano, o catálogo foi persistido, carregado pela aplicação e
integrado à associação e aos filtros de produtos em Estoque e Vendas. O estado
atual da integração, incluindo a interface de gerenciamento, está documentado em
[`docs/catalogo-categorias.md`](../../../docs/catalogo-categorias.md).

## Front-end

A implementação visual e os fluxos da interface estão descritos em
[`front-end.md`](./front-end.md). O código Reflex está em
[`farmacia/farmacia.py`](../../../farmacia/farmacia.py).

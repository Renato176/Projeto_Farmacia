## ADDED Requirements

### Requirement: Organizar categorias por departamento

A tela `/categorias` MUST organizar as opções em departamentos com descrição e
subcategorias. A organização MUST incluir Saúde, Medicamentos, Vitaminas e
Suplementos, Mamãe & Bebê, Beleza, Beleza Premium, Cuidados Diários, Pet e
Marcas Exclusivas. MUST preservar Remédios, Fraldas, Bebidas e Produtos de
Higiene na taxonomia do projeto.

#### Scenario: Consultar departamentos

- **WHEN** o usuário abre a tela de categorias
- **THEN** cada departamento é apresentado com descrição e subcategorias em um
  layout responsivo
- **AND** as categorias já previstas pelo projeto permanecem encontráveis

### Requirement: Pesquisar a hierarquia de categorias

A busca MUST considerar nome e descrição de departamentos e nome de
subcategorias, sem diferenciar maiúsculas de minúsculas ou acentos. Quando o
termo corresponder ao departamento, seus subgrupos são apresentados; quando
corresponder apenas a subcategorias, somente os itens correspondentes são
apresentados dentro de seus departamentos. As contagens devem refletir os
resultados atuais.

#### Scenario: Encontrar um departamento

- **WHEN** o usuário busca por um nome ou descrição de departamento
- **THEN** o departamento correspondente aparece com suas subcategorias

#### Scenario: Encontrar subcategorias

- **WHEN** o usuário busca por um nome de subcategoria
- **THEN** a tela apresenta os departamentos correspondentes apenas com as
  subcategorias encontradas
- **AND** as contagens exibidas correspondem ao resultado filtrado

#### Scenario: Busca sem correspondência

- **WHEN** a busca não encontra departamento ou subcategoria
- **THEN** a tela apresenta o estado vazio

### Requirement: Identificar a origem da taxonomia

A taxonomia inspirada em referência pública MUST ser adaptada ao projeto. A
interface MUST NOT sugerir afiliação ou sincronização com a referência. Os
registros apresentados MUST ser carregados do Xano, e não de uma taxonomia
estática local apresentada como persistida.

#### Scenario: Consultar catálogo persistido

- **WHEN** o usuário visualiza as categorias
- **THEN** a interface consulta o endpoint autenticado `GET /categoria` e
  apresenta os departamentos e subcategorias com seus respectivos status
- **AND** a interface identifica a referência visual sem alegar afiliação com
  o site usado como inspiração

#### Scenario: Falha ao consultar o catálogo

- **WHEN** o endpoint de categorias falha ou retorna dados inválidos
- **THEN** a tela informa o erro e não apresenta a taxonomia local como se
  tivesse sido carregada do Xano

### Requirement: Associar categorias aos produtos

O formulário de produto MUST permitir selecionar uma categoria ativa ou
deixar o produto sem categoria. A aplicação MUST enviar a referência
`categoria_id` ao criar e editar produtos. O filtro por departamento MUST
incluir produtos associados às suas subcategorias.

#### Scenario: Criar ou editar produto com categoria

- **WHEN** o funcionário salva um produto com uma categoria selecionada
- **THEN** a aplicação envia o ID da categoria no campo `categoria_id`
- **AND** a API persiste a associação usando a referência opcional no schema

#### Scenario: Filtrar produtos por departamento

- **WHEN** o funcionário seleciona um departamento como filtro
- **THEN** a lista de produtos inclui aqueles associados ao departamento ou a
  qualquer subcategoria desse departamento

### Requirement: Gerenciar o catálogo pela interface

Funcionários autenticados MUST poder criar e editar departamentos e
subcategorias, ativar/desativar registros e solicitar sua exclusão pela tela
`/categorias`. A aplicação MUST persistir as alterações nos endpoints
autenticados do Xano, validar campos obrigatórios e apresentar erros retornados
pela API sem indicar sucesso indevido. A exclusão MUST exigir confirmação.

#### Scenario: Criar e editar categorias

- **WHEN** o usuário informa os dados de um departamento ou subcategoria e
  salva
- **THEN** a aplicação chama `POST /categoria` ou
  `PATCH /categoria/{categoria_id}`
- **AND** atualiza a lista usando `GET /categoria` após sucesso

#### Scenario: Excluir categoria

- **WHEN** o usuário confirma a exclusão de um registro
- **THEN** a aplicação chama `DELETE /categoria/{categoria_id}`
- **AND** atualiza a lista somente após uma resposta de sucesso
- **WHEN** o Xano rejeita a exclusão por vínculos ou outro erro
- **THEN** a aplicação mantém o registro e informa a falha

## ADDED Requirements

### Requirement: Exibir o catálogo persistido de categorias

A rota protegida `/categorias` MUST carregar as categorias do Xano e apresentar
os registros agrupados por departamento e subcategoria, identificando
categorias ativas e inativas. A tela MUST exibir estados de carregamento, erro
e lista vazia sem substituir falhas por um catálogo local apresentado como se
viesse do backend.

#### Scenario: Abrir a tela autenticado

- **WHEN** um funcionário autenticado abre `/categorias`
- **THEN** a aplicação consulta o endpoint autenticado `GET /categoria`
- **AND** apresenta os departamentos e suas subcategorias com seus status

#### Scenario: Falha ao carregar o catálogo

- **WHEN** a consulta ao Xano falha ou retorna dados inválidos
- **THEN** a tela informa o erro e não apresenta dados locais como persistidos

#### Scenario: Acessar sem sessão

- **WHEN** uma pessoa sem sessão abre `/categorias`
- **THEN** a aplicação redireciona para a página de login

### Requirement: Pesquisar o catálogo de categorias

A busca MUST considerar nomes e descrições dos departamentos e nomes das
subcategorias carregadas. Os resultados e as contagens exibidas MUST
corresponder aos registros encontrados. Quando a consulta não tiver
correspondências, a página MUST apresentar um estado vazio.

#### Scenario: Pesquisar departamento ou subcategoria

- **WHEN** o funcionário informa um termo que corresponde a um departamento
- **THEN** a lista apresenta o departamento e suas subcategorias
- **WHEN** o termo corresponde apenas a subcategorias
- **THEN** a lista apresenta os departamentos correspondentes com somente as
  subcategorias encontradas
- **WHEN** nenhuma categoria corresponde ao termo
- **THEN** a página informa que nenhuma categoria foi encontrada

### Requirement: Associar categorias aos produtos

O formulário de produto MUST permitir selecionar uma categoria ativa ou
deixar o produto sem categoria. A aplicação MUST persistir o vínculo em
`produto.categoria_id` ao criar e editar produtos. O filtro por departamento
MUST incluir produtos associados ao departamento ou a uma de suas
subcategorias.

#### Scenario: Salvar produto classificado

- **WHEN** o funcionário cria ou edita um produto com uma categoria selecionada
- **THEN** a aplicação envia o ID da categoria no campo `categoria_id`
- **AND** os filtros de Estoque e Vendas usam o vínculo persistido

#### Scenario: Filtrar departamento

- **WHEN** o funcionário seleciona um departamento no filtro de produtos
- **THEN** a lista inclui produtos associados ao departamento e às suas
  subcategorias

### Requirement: Gerenciar categorias pelo frontend

Funcionários autenticados MUST poder criar e editar departamentos e
subcategorias, ativar/desativar registros e solicitar sua exclusão pela tela
`/categorias`. A aplicação MUST persistir as alterações nos endpoints
autenticados do Xano, validar campos obrigatórios e apresentar erros retornados
pela API sem indicar sucesso indevido. A exclusão MUST exigir confirmação.

#### Scenario: Criar ou editar categoria

- **WHEN** o funcionário preenche o nome, descrição, departamento pai, status
  e cor e salva a categoria
- **THEN** a aplicação envia os campos para `POST /categoria` ou
  `PATCH /categoria/{categoria_id}`
- **AND** recarrega o catálogo do Xano após uma resposta de sucesso

#### Scenario: Rejeitar dados inválidos

- **WHEN** o funcionário salva uma categoria sem nome ou com cor hexadecimal
  inválida
- **THEN** a aplicação apresenta uma mensagem de validação e não envia a
  requisição

#### Scenario: Excluir categoria

- **WHEN** o funcionário solicita a exclusão de um registro e confirma a ação
- **THEN** a aplicação chama `DELETE /categoria/{categoria_id}`
- **AND** remove o registro da tela somente após confirmação do Xano
- **WHEN** o Xano rejeita a exclusão por vínculos ou outro erro
- **THEN** a aplicação mantém o registro e apresenta a mensagem de erro

# Front-end: gerenciamento de categorias

## Localização

- Rota protegida: `/categorias`.
- Implementação Reflex: [`farmacia/farmacia.py`](../../../farmacia/farmacia.py).
- Estado, validações e chamadas à API: `LoginState`.
- Composição da tela: `categories_page()`.

## Interface

A página apresenta departamentos em cartões responsivos, com descrição,
indicador de status e subcategorias exibidas como etiquetas. Departamentos e
subcategorias mostram ações para editar ou excluir. A ação **Nova categoria**
abre o formulário para criar um departamento ou uma subcategoria.

O formulário permite informar nome, descrição, departamento-pai, status
(ativa/inativa) e cor hexadecimal. Categorias inativas permanecem visíveis na
tela de gerenciamento para que possam ser editadas ou reativadas. A exclusão
solicita confirmação antes de chamar a API.

## Comportamento

- A página autenticada carrega a lista persistida em `GET /categoria`.
- A criação envia os dados para `POST /categoria`.
- A edição envia os dados para `PATCH /categoria/{categoria_id}`.
- A exclusão confirmada chama `DELETE /categoria/{categoria_id}`.
- Após uma gravação bem-sucedida, o catálogo é recarregado do Xano.
- Nome vazio, cor inválida e departamento-pai indisponível são rejeitados no
  formulário, antes do envio.
- Erros de conexão, respostas inválidas e recusas do Xano são apresentados sem
  indicar sucesso nem remover dados que continuam persistidos.
- A rota exige sessão autenticada; sem sessão, o usuário é redirecionado para
  o login.

## Integração com produtos

Os formulários de produto oferecem categorias ativas e permitem manter o
produto sem categoria. A aplicação persiste a referência opcional
`produto.categoria_id`; os filtros de Estoque e Vendas também consideram esse
vínculo e incluem as subcategorias ao filtrar por um departamento.

## Validação

A interface e as chamadas ao Xano foram compiladas e validadas no projeto. A
compilação não representa um teste interativo de gravação no workspace `live`;
nenhum registro de teste foi criado nesse ambiente.

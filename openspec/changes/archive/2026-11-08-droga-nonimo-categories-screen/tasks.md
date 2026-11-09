# Tarefas

- [x] Adicionar rota protegida `/categorias` e ligá-la à navegação.
- [x] Organizar departamentos e subcategorias em cartões responsivos.
- [x] Implementar pesquisa por nome e descrição e estados sem resultados.
- [x] Usar a taxonomia de referência adaptada ao projeto.
- [x] Criar a tabela `categoria` no Xano e importar 9 departamentos e
      49 subcategorias.
- [x] Configurar `produto.categoria_id` como referência opcional a
      `categoria`.
- [x] Criar e publicar os endpoints autenticados de consulta, criação,
      atualização e exclusão de categorias no grupo `Farmacia`.
- [x] Corrigir o mapeamento do `POST /categoria`, incluindo os cinco campos e
      o tipo booleano de `ativo`; publicar somente esse endpoint.
- [x] Carregar categorias do Xano na tela `/categorias` e nos formulários e
      filtros de Estoque e Vendas.
- [x] Enviar `categoria_id` ao criar e editar produtos e incluir as
      subcategorias no filtro por departamento.
- [x] Implementar no frontend o cadastro, a edição, a ativação/desativação e
      a exclusão de departamentos e subcategorias usando os endpoints
      autenticados do Xano.
- [x] Validar campos, exibir erros e atualizar o catálogo após operações
      confirmadas pelo backend.
- [x] Documentar a interface implementada em `front-end.md` nesta change.
- [x] Corrigir e publicar o mapeamento de `categoria_id` no `POST /produto`;
      manter intactos os drafts não relacionados.
- [x] Atualizar a documentação do catálogo e do workspace Xano.

## Interface

A tela `/categorias` oferece os formulários de criação/edição e a confirmação
de exclusão; as alterações são persistidas nos endpoints do Xano.

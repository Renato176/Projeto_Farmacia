# Tarefas

- [x] Levantar os departamentos e exemplos de subcategorias da página pública
      de categorias usada como referência.
- [x] Adaptar a taxonomia ao contexto do projeto, preservando Remédios,
      Fraldas, Bebidas e Produtos de Higiene.
- [x] Apresentar departamentos, descrições e subcategorias em cartões
      responsivos.
- [x] Filtrar por nome ou descrição de departamento e por nome de
      subcategoria.
- [x] Mostrar apenas subcategorias correspondentes quando a busca localizar
      itens em um departamento.
- [x] Atualizar as contagens de departamentos e subcategorias conforme os
      resultados filtrados.
- [x] Criar a tabela `categoria` no Xano e importar os departamentos e
      subcategorias do catálogo.
- [x] Publicar os endpoints autenticados de leitura e escrita de categoria e
      confirmar seus contratos no workspace `169234-0`, branch `v1`, fonte
      `live`.
- [x] Configurar `produto.categoria_id` como referência opcional à tabela
      `categoria`.
- [x] Carregar e validar os registros de categoria do Xano na tela protegida
      `/categorias`, agrupando subcategorias pelo ID da categoria-pai.
- [x] Integrar a seleção de categoria à criação e edição de produtos, enviando
      `categoria_id` pelos endpoints `POST /produto` e
      `PATCH /produto/{produto_id}`.
- [x] Filtrar produtos em Estoque e Vendas pelo vínculo persistido, incluindo
      as subcategorias ao selecionar um departamento.
- [x] Construir a interface frontend para criar, editar, ativar/desativar e
      excluir departamentos e subcategorias pelos endpoints autenticados.
- [x] Validar os dados de categoria no formulário, confirmar exclusões,
      apresentar falhas do Xano e recarregar a lista após sucesso.
- [x] Documentar a interface visual e a integração frontend em `front-end.md`
      nesta change.
- [x] Corrigir os mapeamentos e publicar `POST /categoria` e `POST /produto`
      após confirmar os campos do schema e preservar drafts não relacionados.
- [x] Atualizar a documentação do catálogo e do relatório do Xano.

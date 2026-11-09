# Tarefas

- [x] Registrar as tabelas do Xano `cliente`, `produto`, `venda` e
      `item_venda` e seus campos conforme o relatório do projeto.
- [x] Registrar `produto.imagem_url` e sua configuração nos endpoints de
      criação e atualização de produto.
- [x] Registrar `venda.forma_pagamento` com as opções `dinheiro`, `pix`,
      `credito` e `debito`.
- [x] Registrar as rotas do Xano usadas para produtos, clientes e histórico.
- [x] Carregar produtos do Xano na tela autenticada de estoque.
- [x] Criar e editar produtos com nome, código de barras, preço, quantidade e
      `imagem_url`.
- [x] Validar campos obrigatórios, valores não negativos e URLs HTTP(S) da foto.
- [x] Recarregar o produto após salvar e sinalizar quando `imagem_url` não for
      persistida pelo Xano.
- [x] Carregar vendas, produtos e clientes para a tela de vendas.
- [x] Permitir busca no catálogo e controlar quantidades do carrinho sem
      ultrapassar o estoque carregado.
- [x] Cadastrar cliente com nome, CPF de 11 dígitos e telefone, evitando CPF
      duplicado na lista carregada.
- [x] Calcular e exibir desconto demonstrativo de 14% para cliente cadastrado.
- [x] Exibir histórico de vendas e opções demonstrativas de forma de pagamento.
- [x] Registrar as mudanças visuais do estoque, do catálogo de vendas, do
      carrinho, do cadastro de clientes e do histórico.
- [x] Confirmar no schema Xano as referências `venda.usuario_id` → `user`,
      `venda.cliente_id` → `cliente`, `item_venda.venda_id` → `venda` e
      `item_venda.produto_id` → `produto`.
- [x] Preparar a chamada frontend de `POST /venda/finalizar`; exigir uma
      resposta confirmada com `success` e `venda.id`, preservar o carrinho
      em falhas e atualizar catálogo/histórico após sucesso confirmado.
- [x] Documentar a interface e os limites atuais da integração em
      `front-end.md` nesta change.
- [ ] Definir e disponibilizar no Xano uma operação autenticada e atômica para
      gravar venda e itens e baixar o estoque; falhas de saldo não podem deixar
      gravações parciais. O endpoint `4119638` existe apenas como draft vazio e
      não foi publicado.
- [ ] Validar a integração de ponta a ponta com o endpoint publicado, incluindo
      atualização de catálogo/histórico após sucesso e preservação do carrinho
      em falha.
- [ ] Validar no ambiente Xano a persistência de `imagem_url` em criação e
      edição, além de rollback e concorrência na finalização.
- [ ] Executar testes ponta a ponta com dados de teste para estoque, cadastro
      de cliente, carrinho e finalização.

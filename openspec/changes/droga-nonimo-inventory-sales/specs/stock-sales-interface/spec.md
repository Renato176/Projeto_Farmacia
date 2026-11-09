## ADDED Requirements

### Requirement: Apresentar gestão de estoque com fotos

A tela autenticada `/estoque` MUST permitir localizar produtos por nome ou
código de barras e apresentar foto (ou espaço reservado), nome, código,
quantidade, preço e ação de edição. Quantidades iguais ou inferiores a cinco
devem ser sinalizadas como estoque baixo. Cadastro e edição MUST usar um
formulário visual próprio com os campos do produto e pré-visualização da foto
quando a URL for válida.

#### Scenario: Exibir produto com ou sem foto

- **WHEN** a lista de estoque apresenta um produto com `imagem_url`
- **THEN** a tela exibe a foto do produto
- **WHEN** o produto não tem foto
- **THEN** a tela exibe um espaço reservado sem quebrar a listagem

#### Scenario: Indicar estoque baixo

- **WHEN** a quantidade do produto é cinco ou menor
- **THEN** a tela identifica o produto como `Estoque baixo`
- **WHEN** a quantidade é maior que cinco
- **THEN** a tela identifica o produto como disponível

### Requirement: Apresentar catálogo e histórico de vendas

A tela autenticada `/vendas` MUST apresentar produtos em cartões com foto ou
ícone substituto, preço, quantidade disponível e ação para adicionar ao
carrinho. A busca deve aceitar nome ou código de barras. O histórico deve
abrir em uma janela separada e mostrar identificador da venda, cliente, total,
forma de pagamento e data.

#### Scenario: Consultar catálogo

- **WHEN** o funcionário abre vendas e pesquisa pelo nome ou código de barras
- **THEN** a grade de produtos mostra os resultados correspondentes
- **AND** cada cartão informa preço e disponibilidade atual

#### Scenario: Abrir histórico

- **WHEN** o funcionário escolhe `Histórico`
- **THEN** o histórico aparece em uma janela própria, separada do catálogo
- **AND** pode ser atualizado sem substituir a tela de vendas

### Requirement: Exibir carrinho e identificação do cliente

Quando houver itens no carrinho, a tela MUST mostrar um botão flutuante com
total e quantidade de itens. Esse botão abre o carrinho, no qual o funcionário
pode alterar ou remover quantidades, continuar sem cliente ou escolher um
cliente cadastrado. O cadastro de cliente deve ser apresentado em formulário
separado. O resumo deve apresentar subtotal, desconto e total final.

#### Scenario: Abrir o carrinho

- **WHEN** o funcionário adiciona um ou mais produtos
- **THEN** o botão flutuante exibe o total e a quantidade de itens
- **AND** ao abrir o carrinho são mostradas as linhas de produtos e os
  controles de quantidade

#### Scenario: Selecionar ou cadastrar cliente

- **WHEN** o funcionário opta por identificar o cliente
- **THEN** a tela permite selecionar um cliente existente ou abrir o formulário
  de cadastro
- **AND** o resumo mostra o desconto demonstrativo de 14% apenas para cliente
  cadastrado selecionado

#### Scenario: Finalização ainda não disponível

- **WHEN** o endpoint transacional ainda não foi implementado e validado
- **THEN** a tela deixa claro que a finalização está pendente e não apresenta
  o carrinho como venda concluída

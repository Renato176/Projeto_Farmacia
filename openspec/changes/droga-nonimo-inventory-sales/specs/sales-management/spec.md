## ADDED Requirements

### Requirement: Carregar catálogo e histórico de vendas

O frontend MUST exigir uma sessão autenticada para abrir `/vendas` e carregar
as vendas, os produtos e os clientes usando `GET /venda`, `GET /produto` e
`GET /cliente`. Falhas HTTP, de rede ou de formato MUST ser apresentadas ao
funcionário.

#### Scenario: Carregar dados da tela

- **WHEN** um funcionário autenticado abre `/vendas`
- **THEN** catálogo, clientes e histórico são carregados do Xano
- **AND** o histórico pode ser atualizado sem sair da tela
- **WHEN** uma das consultas falha
- **THEN** a tela informa a falha em vez de apresentar os dados como atualizados

### Requirement: Montar carrinho respeitando o estoque

O frontend MUST permitir pesquisar produtos e adicionar ao carrinho apenas
produtos com saldo disponível. O funcionário MUST poder alterar ou remover
quantidades, sem que a quantidade de um item ultrapasse o estoque carregado.

#### Scenario: Adicionar produto disponível

- **WHEN** o funcionário adiciona um produto com estoque disponível
- **THEN** o carrinho inclui o produto e inicia a quantidade em um
- **AND** uma nova adição incrementa a quantidade sem exceder o saldo

#### Scenario: Produto sem saldo ou quantidade excedente

- **WHEN** o produto não tem saldo ou a quantidade solicitada excede o saldo
- **THEN** o carrinho não ultrapassa o estoque disponível e a tela informa o
  motivo

### Requirement: Identificar ou cadastrar cliente no carrinho

O funcionário MUST poder continuar sem identificar um cliente ou selecionar
um cliente carregado. O cadastro de cliente MUST enviar nome, CPF com 11
dígitos e telefone para `POST /cliente`, usando `esta_registrado: true`.
Cliente com CPF já presente na lista carregada MUST ser recusado antes do
envio.

#### Scenario: Cadastrar cliente

- **GIVEN** que nome, CPF e telefone são válidos e o CPF ainda não está na lista
- **WHEN** o funcionário confirma o cadastro
- **THEN** o frontend cria o cliente no Xano, atualiza a lista e seleciona o
  cliente no carrinho

#### Scenario: Dados inválidos ou CPF duplicado

- **WHEN** o nome ou telefone estiver vazio, o CPF não tiver 11 dígitos ou o
  CPF já estiver na lista carregada
- **THEN** a aplicação informa o erro e não envia o cadastro

### Requirement: Calcular valores demonstrativos do carrinho

O frontend MUST calcular o subtotal com base nos preços e quantidades do
carrinho. Quando houver cliente cadastrado selecionado, MUST exibir o desconto
demonstrativo de 14% e o total resultante. Sem cliente cadastrado selecionado,
o desconto MUST ser zero. A escolha de forma de pagamento MUST permanecer
explicitamente demonstrativa até que uma integração de pagamento seja definida.

#### Scenario: Cliente cadastrado selecionado

- **WHEN** há itens no carrinho e um cliente cadastrado está selecionado
- **THEN** a interface exibe o desconto de 14% e o total após o desconto

#### Scenario: Venda sem cliente

- **WHEN** há itens no carrinho sem cliente cadastrado selecionado
- **THEN** a interface exibe desconto zero e mantém o subtotal como total

### Requirement: Finalizar venda e baixar estoque

Antes de habilitar a finalização, o sistema MUST oferecer uma operação
autenticada que grave a venda e seus itens e baixe o estoque de forma atômica.
Se qualquer item não tiver saldo suficiente ou a gravação falhar, nenhuma
gravação parcial poderá permanecer. A interface MUST limpar o carrinho e
atualizar catálogo e histórico somente após sucesso; em caso de falha, MUST
preservar o carrinho e informar o erro.

#### Scenario: Finalização concluída

- **GIVEN** que o carrinho contém itens válidos e o Xano confirma a operação
- **WHEN** o funcionário finaliza a venda
- **THEN** a venda e seus itens são persistidos, o estoque é atualizado e o
  histórico reflete a nova venda

#### Scenario: Saldo insuficiente ou falha na gravação

- **WHEN** o estoque não comporta algum item ou a operação no Xano falha
- **THEN** nenhuma venda ou item parcial é persistido
- **AND** o carrinho permanece disponível e a tela informa a falha

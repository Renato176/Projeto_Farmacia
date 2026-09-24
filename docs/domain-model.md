Domain Model — Sistema de Farmácia



Este documento descreve os conceitos fundamentais do domínio do sistema de farmácia e como eles se relacionam. Ele é conceitual — não é o modelo físico do banco (para isso, ver as tabelas já modeladas no Xano).



Visão geral dos conceitos

text

Categoria

&#x20;  │

&#x20;  └── Produto

&#x20;          │

&#x20;          └── ItemVenda ── Venda ── Cliente (opcional)

&#x20;                                │

&#x20;                                └── Funcionario

Cliente



Representa uma pessoa cadastrada na farmácia, que pode receber desconto nas compras.



Principais informações

nome

CPF

contato (e-mail, telefone)

status ativo/inativo

Relacionamentos

Um cliente pode realizar várias vendas.

Uma venda pode pertencer a um único cliente, ou a nenhum (venda sem cadastro).

Regras estruturais importantes

Só clientes ativos têm direito ao desconto.

Categoria



Agrupa produtos por tipo (ex.: Medicamentos, Higiene, Vitaminas, Cosméticos).



Principais informações

nome

descrição

Relacionamentos

Uma categoria pode possuir vários produtos.

Um produto pertence a exatamente uma categoria.

Produto



Representa um item vendido pela farmácia.



Principais informações

nome

descrição

preço

estoque

status ativo/inativo

Relacionamentos

Um produto pertence a uma categoria.

Um produto pode aparecer em vários itens de venda (em vendas diferentes).

Funcionário



Representa a pessoa que registra a venda.



Principais informações

nome

cargo

status ativo/inativo

Relacionamentos

Um funcionário pode registrar várias vendas.

Uma venda é registrada por exatamente um funcionário.

Regras estruturais importantes

Não há necessidade de modelar permissões ou login — o funcionário é apenas identificado na venda.

Venda



É o conceito central do sistema: representa uma transação de venda concluída.



Principais informações

data da venda

subtotal

percentual de desconto aplicado

valor do desconto

valor total

forma de pagamento escolhida (simulação visual apenas)

Relacionamentos

Uma venda pode pertencer a um cliente, ou a nenhum.

Uma venda pertence a exatamente um funcionário.

Uma venda possui vários itens de venda.

Regras estruturais importantes

O desconto é determinado no momento da venda, com base no cliente informado (10% se cadastrado e ativo, 0% caso contrário).

valor\_desconto = subtotal × percentual\_desconto / 100

valor\_total = subtotal - valor\_desconto

ItemVenda



Representa um produto (e sua quantidade) dentro de uma venda específica.



Principais informações

quantidade

preço unitário no momento da venda

subtotal do item

Relacionamentos

Um item de venda pertence a exatamente uma venda.

Um item de venda referencia exatamente um produto.

Regras estruturais importantes

subtotal\_item = preco\_unitario × quantidade

O subtotal da venda é a soma dos subtotal\_item de todos os seus itens.

Resumo dos relacionamentos

Categoria 1:N Produto

Produto 1:N ItemVenda

Venda 1:N ItemVenda

Cliente 1:N Venda (opcional)

Funcionario 1:N Venda


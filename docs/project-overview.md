Project Overview — Sistema de Farmácia

1\. Visão geral



Sistema acadêmico que representa o funcionamento básico de uma farmácia: cadastro de clientes, produtos e funcionários, e registro de vendas com aplicação automática de desconto para clientes cadastrados. O objetivo é demonstrar, de forma didática, banco de dados, relacionamentos, regras de negócio e integração entre back-end e front-end.



2\. Problema



Uma farmácia quer simular digitalmente o registro de suas vendas, sabendo quais produtos foram vendidos, para quem, por qual funcionário, e aplicando um benefício (desconto) para clientes já cadastrados — sem precisar de nenhum sistema financeiro ou de pagamento real.



3\. Objetivos

Demonstrar a modelagem de um banco de dados relacional simples com 6 tabelas.

Implementar uma regra de negócio central (desconto para cliente cadastrado e ativo).

Expor essa lógica através de APIs (Xano/XanoScript).

Consumir essas APIs em uma interface visual (Reflex) que simula o fluxo de uma venda, incluindo a escolha da forma de pagamento (sem processá-la).

4\. Público-alvo / usuários

Funcionário da farmácia: registra vendas, escolhe produtos e quantidade, informa (ou não) o cliente.

Cliente cadastrado: identificado no momento da venda para receber o desconto.

Não há, neste projeto, um usuário "administrador" com permissões diferenciadas — não é necessário sistema de login ou permissões complexas.

5\. Escopo



Dentro do escopo:



Cadastro de clientes, categorias, produtos e funcionários.

Registro de vendas e dos itens de cada venda.

Cálculo automático de subtotal, desconto e valor total.

Simulação visual da forma de pagamento no front-end.



Fora do escopo (ver também AGENTS.md):



Controle de fornecedores e compras.

Notas fiscais e integração com a Receita Federal.

Convênios e prescrição médica.

Medicamentos controlados.

Qualquer gateway de pagamento real (PIX, cartão, boleto, Mercado Pago, Stripe etc.).

Sistema financeiro complexo.

6\. Principais funcionalidades

Cadastro de clientes, com CPF, contato e status ativo/inativo.

Cadastro de categorias e produtos (com preço e estoque).

Cadastro simples de funcionários.

Tela de venda: seleção de produtos e quantidades, seleção opcional de cliente, escolha visual da forma de pagamento.

Cálculo automático de desconto: 10% para cliente cadastrado e ativo, 0% caso contrário.

Registro da venda e dos itens vendidos.

7\. Requisitos e restrições importantes

O cálculo de desconto e de totais deve sempre ocorrer no back-end (Xano), nunca só no front-end.

Uma venda pode ocorrer sem cliente cadastrado (cliente\_id é opcional).

O pagamento não é funcional — é somente uma escolha visual, opcionalmente armazenada como texto.

8\. Arquitetura tecnológica

Back-end e lógica de negócio: Xano, escrito em XanoScript.

Banco de dados: Xano (banco nativo da plataforma).

Front-end: Reflex (framework Python para interfaces web).

Comunicação entre front-end e back-end via chamadas HTTP às APIs do Xano.

9\. Princípios de desenvolvimento

Desenvolvimento incremental, guiado por OpenSpec (Explore → Propose → Review → Apply → Archive).

Projeto acadêmico: priorizar simplicidade e clareza sobre completude.

Evitar introduzir complexidade que não sirva diretamente aos objetivos de ensino do projeto.

10\. Segurança e integridade

Toda regra de negócio (especialmente o desconto) é responsabilidade do back-end.

Não há necessidade de autenticação/login de usuários neste projeto.

11\. Estratégia de desenvolvimento

Modelar primeiro o domínio (ver domain-model.md) e as 6 tabelas no Xano.

Implementar as APIs de consulta (produtos, clientes) antes da API de venda.

Implementar a API de venda (com a lógica de desconto) como uma change própria.

Construir a interface Reflex consumindo as APIs já existentes.

12\. Fonte de verdade e documentação

Este documento e docs/domain-model.md são a fonte de verdade sobre o que é o projeto e seu domínio.

O comportamento efetivamente implementado é registrado em openspec/specs/, conforme as changes forem aplicadas e arquivadas.


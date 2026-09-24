AGENTS.md — Sistema de Farmácia

Este arquivo contém instruções para agentes de IA que trabalham neste projeto. Ele complementa (e não substitui) docs/project-overview.md e docs/domain-model.md, que devem ser consultados para entender o projeto em si.



Documentação

Antes de propor ou implementar qualquer mudança significativa, consultar docs/project-overview.md e docs/domain-model.md.

Se uma decisão de negócio ou de domínio não estiver clara nesses documentos, perguntar ao grupo em vez de assumir.

Arquitetura

Back-end e banco de dados: Xano (lógica escrita em XanoScript).

Front-end: Reflex (framework Python).

Não introduzir outra linguagem, framework ou banco de dados sem justificativa explícita e aprovação do grupo.

Toda regra de negócio (especialmente o cálculo de desconto) deve ser implementada no back-end (Xano), nunca apenas no front-end.

Escopo

O pagamento é apenas uma simulação visual no front-end (Reflex). Não implementar integração real com PIX, cartão, boleto, Mercado Pago, Stripe ou qualquer gateway.

Não adicionar funcionalidades fora do escopo acadêmico definido: fornecedores, compras, notas fiscais, convênios, prescrição médica, medicamentos controlados, sistema financeiro complexo.

Se uma nova ideia surgir durante o desenvolvimento, avaliar primeiro se ela pertence ao escopo antes de implementar.

Código

Reutilizar tabelas, endpoints e componentes já existentes quando possível.

Evitar duplicar lógica de cálculo (desconto, subtotal, total) em mais de um lugar.

Não modificar funcionalidades não relacionadas à mudança atual sem justificativa.

Segurança

Regras de autorização e de cálculo (ex.: desconto) devem ser aplicadas no back-end (Xano). O front-end (Reflex) não deve ser tratado como mecanismo de segurança.

Desenvolvimento

Mudanças devem ser conduzidas usando o OpenSpec (Explore → Propose → Review → Apply → Archive).

Não implementar uma funcionalidade inteira de uma vez sem antes passar por uma change revisada pelo grupo.

Testes

Toda mudança que envolva cálculo de valores (subtotal, desconto, total) deve ser verificada com pelo menos um cenário de cliente cadastrado ativo, um de cliente não cadastrado, e (quando fizer sentido) um de cliente cadastrado inativo.

Idioma

Escrever documentação, artefatos do OpenSpec e comentários de código em português brasileiro.


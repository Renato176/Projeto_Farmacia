# Modelo de Domínio e Regras de Negócio
**Projeto:** Sistema de Gestão de Farmácia  

---

## 0. Mapeamento físico no Xano

As entidades e campos abaixo são os nomes lógicos do domínio. No workspace Xano compartilhado, os objetos desta aplicação são isolados com o prefixo `farmacia_final_`: `funcionario` → `farmacia_final_funcionario`, `cargo` → `farmacia_final_cargo`, `cliente` → `farmacia_final_cliente`, `categorias` → `farmacia_final_categorias`, `produtos` → `farmacia_final_produtos`, `pedido` → `farmacia_final_pedido` e `item_pedido` → `farmacia_final_item_pedido`. As APIs novas usam o prefixo de rota `/farmacia-final/`. Não alterar nem migrar tabelas legadas de outras aplicações.

## 1. Dicionário de Dados (Estrutura de Entidades)

### 1.1. Tabela: `funcionario`
| Campo | Tipo de Dado | Restrições / Chaves | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto Increment | Identificador único do funcionário |
| `nome` | String | Not Null | Nome completo do funcionário |
| `email` | String | Unique, Not Null | E-mail corporativo utilizado para login |
| `senha_hash` | String | Not Null | Hash da palavra-passe de acesso |
| `cargo` | String | Nullable | Cargo descritivo do funcionário; não concede permissões |
| `ativo` | Boolean | Default `true` | Permite bloquear autenticação de funcionários inativos |
| `created_at` | Timestamp | Default NOW | Data e hora de criação |

`cargo` é opcional para manter compatibilidade com funcionários existentes; novos cadastros pela API exigem esse campo. O valor é descritivo e não determina permissões. O endpoint público de autocadastro define `ativo=true` no backend e não aceita que o visitante controle esse estado. Como não há aprovação ou verificação de e-mail neste fluxo, qualquer pessoa pode criar uma conta ativa; esta exposição é um risco operacional conhecido.

### 1.2. Tabela: `cargo`
| Campo | Tipo de Dado | Restrições / Chaves | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto Increment | Identificador único do cargo |
| `nome` | String | Unique, Not Null | Nome apresentado como opção de cadastro |
| `ativo` | Boolean | Default `true` | Indica se o cargo pode ser escolhido em novos cadastros |
| `created_at` | Timestamp | Default NOW | Data e hora de criação |

Valores iniciais: `Atendente`, `Farmacêutico`, `Gerente`, `Repositor`, `Caixa` e `Estagiário`. O nome do cargo é copiado para `funcionario.cargo`, que permanece texto para compatibilidade. Cargo é descritivo e não concede permissões.

API pública associada: `GET /farmacia-final/cargos` retorna `{ "cargos": [{ "id": 1, "nome": "Atendente" }] }`, ordenados pelo nome e limitados a registros com `ativo=true`. O cadastro público deve aceitar somente um nome correspondente a um cargo ativo.

### 1.3. Tabela: `cliente`
| Campo | Tipo de Dado | Restrições / Chaves | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto Increment | Identificador único do cliente |
| `nome` | String | Not Null | Nome do cliente |
| `cpf` | String | Unique, Not Null | Documento de identificação (11 dígitos numéricos) |
| `created_at` | Timestamp | Default NOW | Data de registo do cliente |

### 1.4. Tabela: `categorias`
| Campo | Tipo de Dado | Restrições / Chaves | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto Increment | Identificador da categoria |
| `nome` | String | Unique, Not Null | Nome da categoria. Categorias predefinidas: *Remédios*, *Bebidas*, *Fraldas*, *Produtos de Higiene* |
| `descricao` | String | Nullable | Descrição opcional da categoria |
| `ativo` | Boolean | Default `true` | Indica se a categoria está disponível para uso |

### 1.5. Tabela: `produtos`
| Campo | Tipo de Dado | Restrições / Chaves | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto Increment | Identificador único do produto |
| `categoria_id` | Integer | FK (`categorias.id`), Not Null | Categoria a que o produto pertence |
| `nome` | String | Not Null | Nome comercial do produto |
| `descricao` | String | Nullable | Descrição opcional do produto |
| `preco` | Decimal(10,2) | Not Null, $\ge 0$ | Preço atual em Reais (R$) |
| `estoque` | Integer | Not Null, $\ge 0$ | Quantidade física disponível |
| `ativo` | Boolean | Opcional, Default `true` | Indica se o produto é listado para venda no PDV |

### 1.6. Tabela: `pedido`
| Campo | Tipo de Dado | Restrições / Chaves | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto Increment | Número/Código do pedido |
| `funcionario_id`| Integer | FK (`funcionario.id`), Not Null | Funcionário que realizou a venda |
| `cliente_id` | Integer | FK (`cliente.id`), Nullable | Cliente associado (Null se não identificado) |
| `subtotal` | Decimal(10,2) | Not Null | Valor bruto dos produtos |
| `desconto` | Decimal(10,2) | Default 0.00 | Valor total de desconto aplicado |
| `total` | Decimal(10,2) | Not Null | Valor líquido final (`subtotal - desconto`) |
| `status` | Enum | Not Null | `rascunho`, `concluido`, `cancelado` |
| `created_at` | Timestamp | Default NOW | Data/hora exata do encerramento da venda |

### 1.7. Tabela: `item_pedido`
| Campo | Tipo de Dado | Restrições / Chaves | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto Increment | Identificador único do item |
| `pedido_id` | Integer | FK (`pedido.id`), Not Null | Pedido correspondente |
| `produto_id` | Integer | FK (`produto.id`), Not Null | Produto selecionado |
| `quantidade` | Integer | Not Null, $> 0$ | Quantidade comprada |
| `preco_unitario`| Decimal(10,2) | Not Null | Preço congelado no momento da compra |

---

## 2. Cardinalidade e Mapeamento de Relacionamentos
- **`funcionario` $\to$ `pedido`:** $1 : N$ (Um funcionário pode realizar múltiplos pedidos; cada pedido pertence a exatamente um funcionário).
- **`cliente` $\to$ `pedido`:** $1 : N$ (Um cliente pode realizar vários pedidos; um pedido pode ter $0$ ou $1$ cliente associado).
- **`categorias` $\to$ `produtos`:** $1 : N$ (Uma categoria contém múltiplos produtos; cada produto pertence a $1$ categoria).
- **`pedido` $\to$ `produto`:** $N : M$ (Intermediado pela tabela associativa `item_pedido`).

---

## 3. Especificação das Regras de Negócio (RN)

### **RN01: Validação do Desconto de Fidelidade**
- **Gatilho:** Momento de calcular/fechar o pedido no backend.
- **Condição Necessária:** `pedido.cliente_id IS NOT NULL` **E** `pedido.subtotal > 100.00`.
- **Fórmula Matemática:**
  $$\text{desconto} = \text{subtotal} \times 0{,}15$$
  $$\text{total} = \text{subtotal} - \text{desconto}$$
- **Exceção (Sem Desconto):** Se o cliente não for cadastrado (`cliente_id IS NULL`) OU se o subtotal for menor ou igual a R$ 100,00 (`subtotal` $\le 100{,}00$), o campo `desconto` será obrigatoriamente $0{,}00$ e o `total` será igual ao `subtotal`.

### **RN02: Validação e Abatimento de Estoque**
- Antes de concluir o pedido, o sistema deve validar se `produto.estoque >= item_pedido.quantidade` para todos os itens do carrinho.
- Se o estoque for suficiente, executa-se a atualização:
  $$\text{estoque}_{\text{novo}} = \text{estoque}_{\text{atual}} - \text{quantidade}_{\text{comprada}}$$
- Caso o estoque seja insuficiente, lança uma exceção HTTP 400 com a mensagem `"Estoque insuficiente para o produto [Nome]"`.

### **RN03: Unicidade do CPF do Cliente**
- Não podem existir dois clientes com o mesmo CPF cadastrados na base de dados. O campo deve ser validado no Backend.

### **RN04: Consolidação de Métricas de Venda**
- Os relatórios consideram apenas pedidos com status `concluido`:
  - **Diário:** $\sum \text{total}$ onde $\text{DATE}(\text{created\_at}) = \text{CURRENT\_DATE}$.
  - **Semanal:** $\sum \text{total}$ nos últimos 7 dias a partir da data atual.
  - **Mensal:** $\sum \text{total}$ onde o mês e ano de $\text{created\_at}$ coincidem com o mês e ano correntes.
  
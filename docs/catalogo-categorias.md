# Catálogo de categorias e atalhos de busca

O catálogo hierárquico é persistido no Xano e exibido na tela protegida
**Categorias** (`/categorias`). As páginas de **Gestão de Estoque** e
**Vendas** também permitem filtrar produtos pela categoria associada. A
organização visual toma como referência a página pública de
[categorias da Drogasil](https://www.drogasil.com.br/categorias), com nomes
adaptados ao projeto.

## Persistência no Xano

No workspace `169234-0`, branch `v1`, fonte `live`:

- A tabela `categoria` (`913434`) armazena nome, descrição, categoria-pai,
  status ativo e cor.
- O catálogo importado contém 58 registros: 9 departamentos e 49
  subcategorias.
- `produto.categoria_id` é uma referência opcional à tabela `categoria`.
- Os cinco endpoints abaixo exigem autenticação de usuário e estão publicados
  no grupo `Farmacia` (`437376`):

| Método e rota | ID no Xano | Uso |
|---|---:|---|
| `GET /categoria` | `4119595` | Listar categorias |
| `POST /categoria` | `4119596` | Criar categoria |
| `GET /categoria/{categoria_id}` | `4119594` | Consultar categoria |
| `PATCH /categoria/{categoria_id}` | `4119597` | Atualizar categoria |
| `DELETE /categoria/{categoria_id}` | `4119593` | Excluir categoria |

O `POST /categoria` grava `nome`, `descricao`, `categoria_pai_id`, `ativo` e
`cor`; `ativo` é mapeado como booleano. A tela `/categorias` carrega e pesquisa
categorias ativas e inativas, agrupando subcategorias pelo ID do departamento.
O frontend permite criar, editar, ativar/desativar e excluir registros pelos
endpoints autenticados.

O formulário exige nome e cor hexadecimal válida, permite definir descrição,
departamento pai e status. A exclusão exige confirmação; se o Xano rejeitar a
operação por referências existentes, a interface preserva o registro e exibe
o erro retornado.

## Associação aos produtos

O formulário de produto permite selecionar uma categoria ou deixar o produto
sem classificação. A associação é enviada como `categoria_id` tanto na criação
quanto na edição. O `POST /produto` (`4103434`) foi atualizado e publicado para
gravar também `categoria_id` e `imagem_url`; a atualização usada pelo frontend
é `PATCH /produto/{produto_id}` (`4103437`), que já aceita `categoria_id`.

Em Estoque e Vendas, o filtro usa o vínculo persistido do produto. Ao escolher
um departamento, também inclui produtos associados às suas subcategorias. A
busca textual por nome e código de barras continua disponível.

## Limites e validação

Os mapeamentos dos endpoints foram conferidos no XanoScript de revisão antes
da publicação. Não foi feita uma gravação de teste no banco `live`; nenhum
registro temporário foi criado durante a validação desta integração.

As referências de `venda.usuario_id`, `venda.cliente_id`,
`item_venda.venda_id` e `item_venda.produto_id` também foram configuradas e
verificadas no Xano. A referência e os índices estão documentados em
[`relatorio_xano_droga_nonimo.md`](./relatorio_xano_droga_nonimo.md). Isso não
representa a implementação do checkout transacional, que permanece fora do
escopo desta integração de categorias.

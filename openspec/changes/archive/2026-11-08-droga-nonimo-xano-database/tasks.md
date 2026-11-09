# Tasks

- [x] Inspect the Xano workspace and document its pre-existing `user` and `event_log` tables.
- [x] Create the `cliente` table in Xano (table ID `908187`).
- [x] Create the `produto` table in Xano (table ID `908189`).
- [x] Create the `venda` table in Xano (table ID `908190`).
- [x] Create the `item_venda` table in Xano (table ID `908192`).
- [x] Generate three fictitious product records in Xano for initial UI testing.
- [x] Preserve the existing `user` and `event_log` tables and their data.
- [x] Write the implementation report at `docs/relatorio_xano_droga_nonimo.md`.
- [x] Record in the initial schema audit that the four relationship fields were
      integer fields without table-reference indicators.
- [x] Create the `categoria` table in Xano (table ID `913434`) and import the
      catalog of 9 departments and 49 subcategories.
- [x] Configure the optional `produto.categoria_id` table reference to
      `categoria`.
- [x] Create and publish the five authenticated category endpoints in the
      `Farmacia` API group.
- [x] Map `POST /categoria` to `nome`, `descricao`, `categoria_pai_id`,
      `ativo` (boolean), and `cor`; publish only this endpoint.
- [x] Map and publish `categoria_id` in `POST /produto`; preserve its existing
      field mappings and leave unrelated drafts unchanged.
- [x] Configure `venda.usuario_id` as a table reference to `user`.
- [x] Configure `venda.cliente_id` as a table reference to `cliente`.
- [x] Configure `item_venda.venda_id` as a table reference to `venda`.
- [x] Configure `item_venda.produto_id` as a table reference to `produto`.
- [x] Verify each final reference target in the active `v1` / `live` Xano schema.
- [x] Restore and verify ascending indexes on all four relationship fields.
- [x] Document the frontend data contract and the limits of the current sales workflow in `front-end.md`.

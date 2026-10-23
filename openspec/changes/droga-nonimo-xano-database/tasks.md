# Tasks

- [x] Inspect the Xano workspace and document its pre-existing `user` and `event_log` tables.
- [x] Create the `cliente` table in Xano (table ID `908187`).
- [x] Create the `produto` table in Xano (table ID `908189`).
- [x] Create the `venda` table in Xano (table ID `908190`).
- [x] Create the `item_venda` table in Xano (table ID `908192`).
- [x] Generate three fictitious product records in Xano for initial UI testing.
- [x] Preserve the existing `user` and `event_log` tables and their data.
- [x] Write the implementation report at `docs/relatorio_xano_droga_nonimo.md`.
- [ ] Configure `venda.usuario_id` as a table reference to `user`.
- [ ] Configure `venda.cliente_id` as a table reference to `cliente`.
- [ ] Configure `item_venda.venda_id` as a table reference to `venda`.
- [ ] Configure `item_venda.produto_id` as a table reference to `produto`.
- [ ] Verify the final references in the Xano schema after configuration.

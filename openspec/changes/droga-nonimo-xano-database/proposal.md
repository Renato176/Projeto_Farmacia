# DROGA-NONIMO pharmacy database in Xano

## Why

The pharmacy project specification identifies Xano as the backend and describes its core data model, but the workspace initially contained only the default `user` and `event_log` tables. The project needs pharmacy tables in Xano so the frontend can later display and use pharmacy data.

## What changes

- Add `cliente`, `produto`, `venda`, and `item_venda` to the Xano workspace.
- Reuse the existing Xano `user` table for staff and `event_log` for activity records; do not replace or duplicate these tables.
- Add three generated, fictitious product records for initial UI testing.
- Configure table-reference fields between sales, users, customers, and sale items as a follow-up. They currently exist as integer columns because the workspace rejected the attempted XanoScript reference syntax.
- Record actual workspace table IDs, preserved data, and outstanding work in the project report.

## Status

The four tables and three test products have already been created in workspace `169234-0`, branch `v1`, data source `live`. Existing records in `user` were preserved. Table-reference configuration remains incomplete; do not treat the integer ID columns as enforced relationships.

## Out of scope

- Replacing or modifying the existing authentication table or endpoints.
- Creating pharmacy APIs or connecting frontend screens to the new tables.
- Using real customer or health data for test records.

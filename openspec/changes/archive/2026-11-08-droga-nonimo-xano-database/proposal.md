# DROGA-NONIMO pharmacy database in Xano

## Why

The pharmacy project specification identifies Xano as the backend and describes its core data model, but the workspace initially contained only the default `user` and `event_log` tables. The project needs pharmacy tables and verified relationships for its existing catalog and sales screens.

## What changes

- Add `cliente`, `produto`, `venda`, and `item_venda` to the Xano workspace.
- Reuse the existing Xano `user` table for staff and `event_log` for activity records; do not replace or duplicate these tables.
- Add three generated, fictitious product records for initial UI testing.
- Configure and verify the Xano table references between sales, users, customers, products, and sale items.
- Restore ascending indexes on the four relationship fields after configuring their references.
- Document the frontend impact and the remaining limits of the sales workflow.
- Record actual workspace table IDs, preserved data, and remaining work in the project report.

## Status

The four tables and three test products exist in workspace `169234-0`, branch `v1`, data source `live`. Existing records in `user` were preserved. All four relationship fields are now Xano table references to their intended tables, and their ascending indexes are present. No sale or sale-item records were created or changed. This schema change does not implement transactional sale checkout or inventory deduction.

## Out of scope

- Replacing or modifying the existing authentication table or endpoints.
- Implementing transactional sale checkout or inventory deduction.
- Using real customer or health data for test records.

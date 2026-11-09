# pharmacy-database Specification

## Purpose
TBD - created by archiving change droga-nonimo-xano-database. Update Purpose after archive.

## Requirements

### Requirement: Store pharmacy records in Xano

The DROGA-NONIMO backend MUST store pharmacy data in the project's Xano workspace. It MUST provide `cliente`, `produto`, `venda`, and `item_venda` tables with the fields documented in the project specification and the implementation report. Each table MUST use an Xano-generated integer `id` primary key.

#### Scenario: Pharmacy tables are available

- **WHEN** a developer opens the Xano database for workspace `169234-0`
- **THEN** the `cliente`, `produto`, `venda`, and `item_venda` tables are available
- **AND** each table has its documented domain fields and generated `id`

### Requirement: Preserve Xano's existing authentication and event tables

The pharmacy schema MUST reuse the existing Xano `user` table for user records and the existing `event_log` table for event records. Creating pharmacy tables MUST NOT delete or replace either table or its existing records.

#### Scenario: Pharmacy schema is added to an initialized workspace

- **GIVEN** the workspace already contains `user` and `event_log`
- **WHEN** the pharmacy database tables are created
- **THEN** both existing tables and their records remain intact
- **AND** no duplicate `usuario` or `registro_de_evento` table is created

### Requirement: Enforce relationships with Xano table references

The relationship fields MUST be configured as Xano Table Reference fields, not plain integer fields:

- `venda.usuario_id` references `user`
- `venda.cliente_id` references `cliente`
- `item_venda.venda_id` references `venda`
- `item_venda.produto_id` references `produto`

#### Scenario: Relationship fields are configured

- **WHEN** the pharmacy database schema is ready for use
- **THEN** each relationship field is a Table Reference to its specified table
- **AND** Xano identifies the related records through the configured reference fields

### Requirement: Provide fictitious products for initial UI testing

The initial Xano catalog MAY contain three generated, fictitious products for UI testing. Test data MUST NOT contain real customer, personal, or health information.

#### Scenario: Initial product catalog is tested

- **WHEN** the initial test data is generated
- **THEN** three fictitious records are available in `produto`
- **AND** no real customer records are added as part of this setup

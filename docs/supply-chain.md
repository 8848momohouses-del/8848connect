# Supply Chain & Fulfilment

## Overview
8848 Connect manages the complete supply chain natively within Odoo 19, encompassing Supplier Management, Factory Production, Warehouse Quality Assurance, and Driver Route Completion.

## Strict Quantity Validations
Delivery Routes cannot be completed without explicit `quantity` entries against the `stock.picking` moves. 
If a picking lacks quantities, the delivery validation raises an operational blocker.
If a partial quantity is provided, the standard Odoo 19 backorder wizard (`stock.backorder.confirmation`) is intercepted and automatically processed to ensure physical state matches the system state without hanging the completion loop.

## Invoicing
Invoices are generated idempotently upon successful delivery route completion. If an invoice fails to generate (e.g., due to account locking), the delivery remains intact, its `invoice_status` is marked as `failed`, and it can be safely retried by an Accounts Manager or Operations Manager.

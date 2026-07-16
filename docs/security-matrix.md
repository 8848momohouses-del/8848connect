# Security Matrix

## Broad Visibility vs Strict Write Access
8848 Connect applies a collaborative security principle:
- **CEO & General Manager (GM):** Broad read visibility across all models (Supply Chain, Franchises, Deliveries). Destructive actions require explicit roles.
- **Operations Manager:** Can approve Franchise Sales Orders and forcefully complete deliveries or retry failed invoices.
- **Warehouse/Factory User:** Only users in these groups can mark a `stock.picking` as 'Packed'.
- **Driver:** Record-level rules restrict drivers to see *only* their assigned routes (`8848_delivery.route`).

These roles are strictly enforced at the Python method level (e.g., `check_access_rights`, manual `has_group` validations) rather than just UI button hiding.

DROP VIEW IF EXISTS public.ord_status;
CREATE OR REPLACE VIEW ord_status AS (
    SELECT
            'A' as ord_status_idx,
            'Complete Shipment' as ord_status
    UNION ALL
    SELECT
            'B' as ord_status_idx,
            'Partial Shipment' as ord_status
    UNION ALL
    SELECT
            'C' as ord_status_idx,
            'Cancelled Order' as ord_status
    UNION ALL
    SELECT
            'D' as ord_status_idx,
            'Pending Shipment' as ord_status
    UNION ALL
    SELECT
            'E' as ord_status_idx,
            'Quote' as ord_status
    UNION ALL
    SELECT
            'F' as ord_status_idx,
            'Cancelled Quote' as ord_status
    UNION ALL
    SELECT
            'G' as ord_status_idx,
            'Waiting for Backorder' as ord_status
    UNION ALL
    SELECT
            'H' as ord_status_idx,
            'Waiting for Backorder Authorization' as ord_status
    UNION ALL
    SELECT
            'I' as ord_status_idx,
            'Invoiced' as ord_status
)
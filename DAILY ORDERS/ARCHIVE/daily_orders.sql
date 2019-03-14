DROP VIEW IF EXISTS daily_orders;
CREATE OR REPLACE VIEW daily_orders AS (
        SELECT c.cli_name1,
        ol.ord_no,
        ol.prt_no,
        ol.prt_desc,
        oh.ord_date,
        ol.orl_quantity,
        s.sal_name
        FROM order_header AS oh
        JOIN order_line AS ol ON ol.ord_id = oh.ord_id
        JOIN part AS p ON p.prt_id = ol.prt_id
        JOIN part_group AS pg ON pg.pgr_id = p.pgr_id
        JOIN client AS c ON c.cli_id = oh.cli_id
        JOIN salesman s ON c.sal_id = s.sal_id
        WHERE oh.ord_date = now()::DATE
        ORDER BY ord_no
)
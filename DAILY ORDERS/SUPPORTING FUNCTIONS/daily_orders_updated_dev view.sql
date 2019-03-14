-- DROP VIEW IF EXISTS daily_orders_updated;
-- CREATE OR REPLACE VIEW daily_orders_updated AS (
    SELECT
    ol.orl_id,
    ol.ord_no,
    oh.ord_date,
    TRIM(oh.ord_cli_ord_no) AS ord_cli_ord_no,
    TRIM(s.sal_name) AS sal_name,

    CASE    
        WHEN oh.ord_type = 1 THEN (SELECT TRIM(orc_type1) FROM order_config)
        WHEN oh.ord_type = 2 THEN (SELECT TRIM(orc_type2) FROM order_config)
        WHEN oh.ord_type = 3 THEN (SELECT TRIM(orc_type3) FROM order_config)
        WHEN oh.ord_type = 4 THEN (SELECT TRIM(orc_type4) FROM order_config)
        WHEN oh.ord_type = 5 THEN (SELECT TRIM(orc_type5) FROM order_config)
        WHEN oh.ord_type = 6 THEN (SELECT TRIM(orc_type6) FROM order_config)
        WHEN oh.ord_type = 7 THEN (SELECT TRIM(orc_type7) FROM order_config)
        WHEN oh.ord_type = 8 THEN (SELECT TRIM(orc_type8) FROM order_config)
        WHEN oh.ord_type = 9 THEN (SELECT TRIM(orc_type9) FROM order_config)
        WHEN oh.ord_type = 10 THEN (SELECT TRIM(orc_type10) FROM order_config)
    END AS ord_type,

    CASE    
        WHEN oh.ord_status = 'A' THEN 'Complete Shipment'
        WHEN oh.ord_status = 'B' THEN 'Partial Shipment'
        WHEN oh.ord_status = 'C' THEN 'Cancelled Order'
        WHEN oh.ord_status = 'D' THEN 'Pending Shipment'
        WHEN oh.ord_status = 'E' THEN 'Quote'
        WHEN oh.ord_status = 'F' THEN 'Cancelled Quote'
        WHEN oh.ord_status = 'G' THEN 'Waiting for Backorder'
        WHEN oh.ord_status = 'H' THEN 'Waiting for Backorder Authorization'
        WHEN oh.ord_status = 'I' THEN 'Invoiced'
    END AS ord_status,

    TRIM(oh.ord_pmt_term_desc) AS ord_pmt_term_desc,
    (SELECT cur_name FROM currency WHERE c.cli_currency = cur_id),
    TRIM(oh.ord_ship_term_desc) AS ord_ship_term_desc,
    TRIM(oh.car_name) AS car_name,

    CASE    
        WHEN oh.inv_cli_id = 0 THEN TRIM(c.cli_no)
        WHEN oh.inv_cli_id <> 0 THEN (SELECT TRIM(cli_no) FROM client WHERE cli_id = inv_cli_id) 
    END AS inv_cli_no,
    TRIM(oh.inv_name1) AS inv_name1,
    TRIM(oh.inv_name2) AS inv_name2,
    TRIM(oh.inv_addr) AS inv_addr,
    TRIM(oh.inv_city) AS inv_city,
    TRIM(oh.inv_pc) AS inv_pc,
    TRIM(oh.inv_phone) AS inv_phone,

    TRIM(c.cli_no) AS del_cli_no,
    TRIM(oh.cli_del_name1) AS del_name1,
    TRIM(oh.cli_del_name2) AS del_name2,
    TRIM(oh.cli_del_addr) AS del_addr,
    TRIM(oh.cli_del_city) AS del_city,
    TRIM(oh.cli_del_pc) AS del_pc,
    TRIM(oh.cli_phone1) AS del_phone,

    TRIM(oh.ord_note1) AS ord_note1,
    TRIM(oh.ord_note2) AS ord_note2,
    TRIM(oh.ord_note3) AS ord_note3,
    TRIM(oh.ord_note4) AS ord_note4,

    ol.prt_no,
    ol.prt_desc,
    ol.orl_quantity,
    ol.orl_req_dt,
    (SELECT prt_price FROM client_contracts WHERE c.cli_no = client_contracts.cli_no AND p.prt_no = client_contracts.prt_no LIMIT 1)::NUMERIC(17,2) AS con_price,
    (SELECT ppr_price FROM part_price WHERE ol.prt_id = prt_id AND c.cli_price_level = ppr_sort_idx),
    ol.orl_price::NUMERIC(17,2),
    
    CASE
        WHEN ol.orl_price = (SELECT prt_price FROM client_contracts WHERE c.cli_no = client_contracts.cli_no AND p.prt_no = client_contracts.prt_no LIMIT 1) THEN 'Contract'
        WHEN ol.orl_price = (SELECT ppr_price FROM part_price WHERE ol.prt_id = prt_id AND c.cli_price_level = ppr_sort_idx) THEN 'List'
        ELSE 'Manual'
    END AS price_type,
    
    (c.cli_dscnt / 100)::NUMERIC(17,2) AS cli_dscnt,
    CASE 
        WHEN (SELECT (prt_dscnt / 100) FROM client_contracts WHERE c.cli_no = client_contracts.cli_no AND p.prt_no = client_contracts.prt_no LIMIT 1)::NUMERIC(17,2) is NULL THEN 0.00 
        ELSE (SELECT (prt_dscnt / 100) FROM client_contracts WHERE c.cli_no = client_contracts.cli_no AND p.prt_no = client_contracts.prt_no LIMIT 1)::NUMERIC(17,2) 
    END AS con_dscnt,
    (ol.prt_dscnt / 100)::NUMERIC(17,2) AS prt_dscnt,
    
    CASE
        WHEN ol.prt_dscnt = 0 THEN NULL
        WHEN ol.prt_dscnt = (SELECT prt_dscnt FROM client_contracts WHERE c.cli_no = client_contracts.cli_no AND p.prt_no = client_contracts.prt_no LIMIT 1) THEN 'Contract Part'
        WHEN ol.prt_dscnt = (SELECT pgr_dscnt FROM contract_group_line WHERE contract_group_line.con_id IN (SELECT con_id FROM client_contract WHERE client_contract.cli_id = c.cli_id) AND p.pgr_id = contract_group_line.pgr_id) THEN 'Contract Group'
        WHEN ol.prt_dscnt = c.cli_dscnt THEN 'Client File'
        ELSE 'Manual'
    END AS dscnt_type,

    (ol.orl_price * (1 - ol.prt_dscnt / 100))::NUMERIC(17,2) AS orl_net_price,
    (ol.orl_price * (1 - ol.prt_dscnt / 100) * ol.orl_quantity)::NUMERIC(17,2) AS orl_total_price,

    oh.ord_pkg_cost,
    oh.ord_tship_rate,
    oh.ord_ttax1_amnt,
    oh.ord_ttax2_amnt,
    
    CASE
        WHEN (SELECT ppr_price FROM part_price WHERE ol.prt_id = prt_id AND c.cli_price_level = ppr_sort_idx) <> 0 THEN (1 - (ol.orl_price * (1 - ol.prt_dscnt / 100))::NUMERIC(17,2) / (SELECT ppr_price FROM part_price WHERE ol.prt_id = prt_id AND c.cli_price_level = ppr_sort_idx))
        ELSE (ol.prt_dscnt / 100)::NUMERIC(17,2)
    END AS net_dscnt,
    
    CASE
        WHEN EXISTS (
            SELECT ord_no 
            FROM dblink(
                'dbname=LOG hostaddr=192.168.0.57 port=5493 user=SIGM', 
                'SELECT change_type, ord_no, orl_id FROM daily_orders_updated'
            ) AS t1(
                    change_type text, 
                    ord_no INTEGER, 
                    orl_id INTEGER
                ) 
            WHERE ord_no = oh.ord_no
            AND change_type = 'CONVERTED QUOTE'
        ) THEN TRUE ELSE FALSE 
    END AS converted_quote,
    
    CASE
        WHEN EXISTS (
            SELECT ord_no 
            FROM dblink(
                'dbname=LOG hostaddr=192.168.0.57 port=5493 user=SIGM', 
                'SELECT change_type, ord_no, orl_id FROM daily_orders_updated'
            ) AS t1(
                    change_type text, 
                    ord_no INTEGER, 
                    orl_id INTEGER
                ) 
            WHERE ord_no = oh.ord_no
            AND orl_no = ol.ord_no
            AND change_type = 'ADDED PART'
        ) THEN TRUE ELSE FALSE 
    END AS added_part,
    
    CASE
        WHEN EXISTS (
            SELECT ord_no 
            FROM dblink(
                'dbname=LOG hostaddr=192.168.0.57 port=5493 user=SIGM', 
                'SELECT change_type, ord_no, orl_id FROM daily_orders_updated'
            ) AS t1(
                    change_type text, 
                    ord_no INTEGER, 
                    orl_id INTEGER
                ) 
            WHERE ord_no = oh.ord_no
            AND orl_no = ol.ord_no
            AND change_type = 'PRICE CHANGED'
        ) THEN TRUE ELSE FALSE 
    END AS price_changed,
    
    CASE
        WHEN EXISTS (
            SELECT ord_no 
            FROM dblink(
                'dbname=LOG hostaddr=192.168.0.57 port=5493 user=SIGM', 
                'SELECT change_type, ord_no, orl_id FROM daily_orders_updated'
            ) AS t1(
                    change_type text, 
                    ord_no INTEGER, 
                    orl_id INTEGER
                ) 
            WHERE ord_no = oh.ord_no
            AND orl_no = ol.ord_no
            AND change_type = 'REMOVED PART'
        ) THEN TRUE ELSE FALSE 
    END AS removed_part

    FROM order_header AS oh
    JOIN order_line AS ol ON ol.ord_id = oh.ord_id
    JOIN part AS p ON p.prt_id = ol.prt_id
    JOIN part_group AS pg ON pg.pgr_id = p.pgr_id
    JOIN client AS c ON c.cli_id = oh.cli_id
    JOIN salesman s ON c.sal_id = s.sal_id
    WHERE orl_kitmaster_id = 0
    AND oh.ord_no IN (SELECT * FROM dblink('dbname=LOG hostaddr=192.168.0.57 port=5493 user=SIGM', 'SELECT ord_no FROM daily_orders_updated') AS t1(ord_no integer))
    AND ol.prt_id NOT IN (
        SELECT prt_id
        FROM order_line
        WHERE prt_id IN (
            SELECT prt_id 
            FROM part_kit
            WHERE pkt_master_prt_id IN (
                SELECT prt_id 
                FROM order_line 
                WHERE order_line.ord_no = oh.ord_no
            )
        )
    )        
    ORDER BY sal_name, oh.ord_no
-- )
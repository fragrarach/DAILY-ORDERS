DROP VIEW IF EXISTS daily_orders_updated;
CREATE OR REPLACE VIEW daily_orders_updated AS (
    SELECT
    ol.orl_id,
    ol.ord_no,
    oh.ord_date,
    trim(oh.ord_cli_ord_no) AS ord_cli_ord_no,
    trim(s.sal_name) AS sal_name,

    CASE    WHEN oh.ord_type = 1 then (select trim(orc_type1) from order_config)
            WHEN oh.ord_type = 2 then (select trim(orc_type2) from order_config)
            WHEN oh.ord_type = 3 then (select trim(orc_type3) from order_config)
            WHEN oh.ord_type = 4 then (select trim(orc_type4) from order_config)
            WHEN oh.ord_type = 5 then (select trim(orc_type5) from order_config)
            WHEN oh.ord_type = 6 then (select trim(orc_type6) from order_config)
            WHEN oh.ord_type = 7 then (select trim(orc_type7) from order_config)
            WHEN oh.ord_type = 8 then (select trim(orc_type8) from order_config)
            WHEN oh.ord_type = 9 then (select trim(orc_type9) from order_config)
            WHEN oh.ord_type = 10 then (select trim(orc_type10) from order_config)
    END as ord_type,

    CASE    WHEN oh.ord_status = 'A' then 'Complete Shipment'
            WHEN oh.ord_status = 'B' then 'Partial Shipment'
            WHEN oh.ord_status = 'C' then 'Cancelled Order'
            WHEN oh.ord_status = 'D' then 'Pending Shipment'
            WHEN oh.ord_status = 'E' then 'Quote'
            WHEN oh.ord_status = 'F' then 'Cancelled Quote'
            WHEN oh.ord_status = 'G' then 'Waiting for Backorder'
            WHEN oh.ord_status = 'H' then 'Waiting for Backorder Authorization'
            WHEN oh.ord_status = 'I' then 'Invoiced'
    END as ord_status,

    trim(oh.ord_pmt_term_desc) as ord_pmt_term_desc,
    (SELECT cur_name FROM currency WHERE c.cli_currency = cur_id),
    trim(oh.ord_ship_term_desc) as ord_ship_term_desc,
    trim(oh.car_name) as car_name,

    CASE    WHEN oh.inv_cli_id = 0 THEN trim(c.cli_no)
            WHEN oh.inv_cli_id <> 0 THEN (select trim(cli_no) from client where cli_id = inv_cli_id) 
    END AS inv_cli_no,
    trim(oh.inv_name1) as inv_name1,
    trim(oh.inv_name2) as inv_name2,
    trim(oh.inv_addr) as inv_addr,
    CASE
        WHEN inv_cli_id = 0 THEN (
            trim(oh.inv_city) || ', ' ||
            (
                SELECT cc_code_char 
                FROM vw_client_country 
                WHERE cc_code_num IN (
                    SELECT DISTINCT cli_cntry 
                    FROM client 
                    WHERE client.cli_id = oh.cli_id
                )
            )
        )
        WHEN inv_cli_id <> 0 THEN (
            trim(oh.inv_city) || ', ' ||
            (
                SELECT cc_code_char 
                FROM vw_client_country 
                WHERE cc_code_num IN (
                    SELECT DISTINCT cli_cntry 
                    FROM client 
                    WHERE client.cli_id = oh.inv_cli_id
                )
            )
        )
    END AS inv_city,
    trim(oh.inv_pc) as inv_pc,
    trim(oh.inv_phone) as inv_phone,

    trim(c.cli_no) AS del_cli_no,
    trim(oh.cli_del_name1) as del_name1,
    trim(oh.cli_del_name2) as del_name2,
    trim(oh.cli_del_addr) as del_addr,
    
    trim(oh.cli_del_city) || ', ' ||
    (
        SELECT cc_code_char 
        FROM vw_client_country 
        WHERE cc_code_num IN (
            SELECT DISTINCT cli_cntry 
            FROM client 
            WHERE client.cli_id = oh.cli_id
        )
    ) AS del_city,
    
    -- trim(oh.cli_del_city) as del_city,
    
    trim(oh.cli_del_pc) as del_pc,
    trim(oh.cli_phone1) as del_phone,

    trim(oh.ord_note1) as ord_note1,
    trim(oh.ord_note2) as ord_note2,
    trim(oh.ord_note3) as ord_note3,
    trim(oh.ord_note4) as ord_note4,

    ol.prt_no,
    ol.prt_desc,
    ol.orl_quantity,
    ol.orl_req_dt,
    (select prt_price from client_contracts where c.cli_no = client_contracts.cli_no and p.prt_no = client_contracts.prt_no LIMIT 1)::numeric(17,2) as con_price,
    (select ppr_price from part_price where ol.prt_id = prt_id and c.cli_price_level = ppr_sort_idx),
    ol.orl_price::numeric(17,2),
    
    CASE
    when ol.orl_price = (select prt_price from client_contracts where c.cli_no = client_contracts.cli_no and p.prt_no = client_contracts.prt_no LIMIT 1) then 'Contract'
    WHEN ol.orl_price = (select ppr_price from part_price where ol.prt_id = prt_id and c.cli_price_level = ppr_sort_idx) then 'List'
    ELSE 'Manual'
    end as price_type,
    
    (c.cli_dscnt / 100)::numeric(17,2) as cli_dscnt,
    CASE 
    WHEN (select (prt_dscnt / 100) from client_contracts where c.cli_no = client_contracts.cli_no and p.prt_no = client_contracts.prt_no LIMIT 1)::numeric(17,2) is null then 0.00 
    else (select (prt_dscnt / 100) from client_contracts where c.cli_no = client_contracts.cli_no and p.prt_no = client_contracts.prt_no LIMIT 1)::numeric(17,2) 
    end as con_dscnt,
    (ol.prt_dscnt / 100)::numeric(17,2) as prt_dscnt,
    
    CASE
    WHEN ol.prt_dscnt = 0 then null
    WHEN ol.prt_dscnt = (select prt_dscnt from client_contracts where c.cli_no = client_contracts.cli_no and p.prt_no = client_contracts.prt_no LIMIT 1) THEN 'Contract Part'
    when ol.prt_dscnt = (SELECT pgr_dscnt FROM contract_group_line where contract_group_line.con_id IN (SELECT con_id from client_contract where client_contract.cli_id = c.cli_id) and p.pgr_id = contract_group_line.pgr_id) THEN 'Contract Group'
    when ol.prt_dscnt = c.cli_dscnt then 'Client File'
    ELSE 'Manual'
    end as dscnt_type,

    (ol.orl_price * (1 - ol.prt_dscnt / 100))::numeric(17,2) as orl_net_price,
    (ol.orl_price * (1 - ol.prt_dscnt / 100) * ol.orl_quantity)::numeric(17,2) as orl_total_price,

    oh.ord_pkg_cost,
    oh.ord_tship_rate,
    oh.ord_ttax1_amnt,
    oh.ord_ttax2_amnt,
    
    CASE
    WHEN (select ppr_price from part_price where ol.prt_id = prt_id and c.cli_price_level = ppr_sort_idx) <> 0 THEN (1 - (ol.orl_price * (1 - ol.prt_dscnt / 100))::numeric(17,2) / (select ppr_price from part_price where ol.prt_id = prt_id and c.cli_price_level = ppr_sort_idx))
    ELSE (ol.prt_dscnt / 100)::numeric(17,2)
    END as net_dscnt
    
    FROM order_header AS oh
    JOIN order_line AS ol ON ol.ord_id = oh.ord_id
    JOIN part AS p ON p.prt_id = ol.prt_id
    JOIN part_group AS pg ON pg.pgr_id = p.pgr_id
    JOIN client AS c ON c.cli_id = oh.cli_id
    JOIN salesman s ON c.sal_id = s.sal_id
    WHERE orl_kitmaster_id = 0
    and oh.ord_no in (SELECT * from dblink('dbname=LOG hostaddr=192.168.0.250 port=5493 user=SIGM', 'select ord_no from daily_orders_updated') as t1(ord_no integer))
    AND ol.prt_id NOT IN (
        SELECT prt_id
        FROM order_line
        WHERE prt_id IN (
            SELECT prt_id 
            from part_kit
            WHERE pkt_master_prt_id IN (
                SELECT prt_id 
                FROM order_line 
                WHERE order_line.ord_no = oh.ord_no
            )
        )
    )        
    ORDER BY sal_name, oh.ord_no
)
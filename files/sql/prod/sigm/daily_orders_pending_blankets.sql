DROP VIEW IF EXISTS public.daily_orders_pending_blankets;
CREATE OR REPLACE VIEW daily_orders_pending_blankets AS (
    SELECT
    --Line reference
    ol.orl_id,

    --Header body

    --Header column 1
    ol.ord_no,
    TRIM(oh.ord_pmt_term_desc) AS ord_pmt_term_desc,

    --Header column 2
    oh.ord_date,
    TRIM(oh.ord_ship_term_desc) AS ord_ship_term_desc,

    --Header column 3
    TRIM(oh.ord_cli_ord_no) AS ord_cli_ord_no,
    TRIM(oh.car_name) AS car_name,

    --Header column 4
    TRIM(s.sal_name) AS sal_name,
    (
        SELECT cur_name
        FROM currency
        WHERE c.cli_currency = cur_id
    ) AS cur_name,
    oc.ord_type,

    --Header column 5
    os.ord_status,

    --Shipping body

    --Invoicing column
    CASE
        WHEN
            oh.inv_cli_id = 0
        THEN
            TRIM(c.cli_no)

        WHEN
            oh.inv_cli_id <> 0
        THEN
            (
                SELECT TRIM(cli_no)
                FROM client
                WHERE cli_id = inv_cli_id
            )
    END AS inv_cli_no,
    CASE
        WHEN
            oh.inv_cli_id = 0
        THEN
            (
                SELECT string_agg(TRIM(cgr_desc), ', ')
                FROM client_grouping
                WHERE cgr_no LIKE '0%'
                AND cgr_id IN (
                    SELECT cgr_id
                    FROM client_grouping_line
                    WHERE cli_id = oh.cli_id
                )
            )
        WHEN
            oh.inv_cli_id <> 0
        THEN
            (
                SELECT string_agg(TRIM(cgr_desc), ', ')
                FROM client_grouping
                WHERE cgr_no LIKE '0%'
                AND cgr_id IN (
                    SELECT cgr_id
                    FROM client_grouping_line
                    WHERE cli_id = oh.inv_cli_id
                )
            )
    END AS inv_cli_type,
    CASE
        WHEN
            oh.inv_cli_id = 0
        THEN
            (
                SELECT string_agg(TRIM(cgr_desc), ', ')
                FROM client_grouping
                WHERE cgr_no LIKE '1%'
                AND cgr_id IN (
                    SELECT cgr_id
                    FROM client_grouping_line
                    WHERE cli_id = oh.cli_id
                )
            )
        WHEN
            oh.inv_cli_id <> 0
        THEN
            (
                SELECT string_agg(TRIM(cgr_desc), ', ')
                FROM client_grouping
                WHERE cgr_no LIKE '1%'
                AND cgr_id IN (
                    SELECT cgr_id
                    FROM client_grouping_line
                    WHERE cli_id = oh.inv_cli_id
                )
            )
    END AS inv_cli_ind,
    TRIM(oh.inv_name1) AS inv_name1,
    TRIM(oh.inv_name2) AS inv_name2,
    TRIM(oh.inv_addr) AS inv_addr,
    CASE
        WHEN
            inv_cli_id = 0
        THEN
            (
                TRIM(oh.inv_city) || ', ' ||
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
        WHEN
            inv_cli_id <> 0
        THEN
        (
            TRIM(oh.inv_city) || ', ' ||
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
    TRIM(oh.inv_pc) AS inv_pc,
    TRIM(oh.inv_phone) AS inv_phone,

    --Shipping column
    TRIM(c.cli_no) AS del_cli_no,
    (
        SELECT string_agg(TRIM(cgr_desc), ', ')
        FROM client_grouping
        WHERE cgr_no LIKE '0%'
        AND cgr_id IN (
            SELECT cgr_id
            FROM client_grouping_line
            WHERE cli_id = oh.cli_id
        )
    ) AS cli_type,
    (
        SELECT string_agg(TRIM(cgr_desc), ', ')
        FROM client_grouping
        WHERE cgr_no LIKE '1%'
        AND cgr_id IN (
            SELECT cgr_id
            FROM client_grouping_line
            WHERE cli_id = oh.cli_id
        )
    ) AS cli_ind,
    TRIM(oh.cli_del_name1) AS del_name1,
    TRIM(oh.cli_del_name2) AS del_name2,
    TRIM(oh.cli_del_addr) AS del_addr,
    TRIM(oh.cli_del_city) || ', ' ||
    (
        SELECT cc_code_char
        FROM vw_client_country
        WHERE cc_code_num IN (
            SELECT DISTINCT cli_cntry
            FROM client
            WHERE client.cli_id = oh.cli_id
        )
    ) AS del_city,
    TRIM(oh.cli_del_pc) AS del_pc,
    TRIM(oh.cli_phone1) AS del_phone,

    --Notes column
    TRIM(oh.ord_note1) AS ord_note1,
    TRIM(oh.ord_note2) AS ord_note2,
    TRIM(oh.ord_note3) AS ord_note3,
    TRIM(oh.ord_note4) AS ord_note4,

    --Order line body

    --Order line row
    ol.orl_sort_idx,
    CASE
        WHEN
            ol.orl_quantity > 0
            AND ol.orl_active = 'I'
        THEN
            'Invoiced'

        ELSE
            ''
     END AS orl_active,
    ol.prt_no,
    ol.prt_desc,
    ol.orl_quantity,
    ol.orl_reserved_qty,
    ol.orl_req_dt,
    (
        SELECT prt_price
        FROM client_contracts
        WHERE c.cli_no = client_contracts.cli_no
        AND p.prt_no = client_contracts.prt_no LIMIT 1
    )::NUMERIC(17,2) AS con_price,
    ol.orl_price::NUMERIC(17,2),
    CASE
        WHEN
            ol.orl_price = (
                SELECT prt_price
                FROM client_contracts
                WHERE c.cli_no = client_contracts.cli_no
                AND p.prt_no = client_contracts.prt_no LIMIT 1
            )
        THEN
            'Contract'

        WHEN
            ol.orl_price = (
                SELECT ppr_price
                FROM part_price
                WHERE ol.prt_id = prt_id
                AND c.cli_price_level = ppr_sort_idx
            )
        THEN
            'List'

        ELSE
            'Manual'
    END AS price_type,
    (c.cli_dscnt / 100)::NUMERIC(17,2) AS cli_dscnt,
    CASE
        WHEN
            (
                SELECT (prt_dscnt / 100)
                FROM client_contracts
                WHERE c.cli_no = client_contracts.cli_no
                AND p.prt_no = client_contracts.prt_no LIMIT 1
            )::NUMERIC(17,2) IS NULL
        THEN
            0.00

        ELSE
            (
                SELECT (prt_dscnt / 100)
                FROM client_contracts
                WHERE c.cli_no = client_contracts.cli_no
                AND p.prt_no = client_contracts.prt_no LIMIT 1
            )::NUMERIC(17,2)
    END AS con_dscnt,
    (ol.prt_dscnt / 100)::NUMERIC(17,2) AS prt_dscnt,
    CASE
        WHEN
            ol.prt_dscnt = 0
        THEN
            NULL

        WHEN
            ol.prt_dscnt = (
                SELECT prt_dscnt
                FROM client_contracts
                WHERE c.cli_no = client_contracts.cli_no
                AND p.prt_no = client_contracts.prt_no LIMIT 1
            )
        THEN
            'Contract Part'

        WHEN
            ol.prt_dscnt = (
                SELECT pgr_dscnt
                FROM contract_group_line
                WHERE contract_group_line.con_id IN (
                    SELECT con_id
                    FROM client_contract
                    WHERE client_contract.cli_id = c.cli_id
                )
                AND p.pgr_id = contract_group_line.pgr_id
            )
        THEN
            'Contract Group'

        WHEN
            ol.prt_dscnt = c.cli_dscnt
        THEN
            'Client File'

        ELSE
            'Manual'
    END AS dscnt_type,
    (ol.orl_price * (1 - ol.prt_dscnt / 100))::NUMERIC(17,2) AS orl_net_price,
    (ol.orl_price * (1 - ol.prt_dscnt / 100) * ol.orl_quantity)::NUMERIC(17,2) AS orl_total_price,
    CASE
        WHEN
            (
                SELECT ppr_price
                FROM part_price
                WHERE ol.prt_id = prt_id
                AND c.cli_price_level = ppr_sort_idx
            ) <> 0
        THEN
            (
                1 - (ol.orl_price * (1 - ol.prt_dscnt / 100))::NUMERIC(17,2) / (
                    SELECT ppr_price
                    FROM part_price
                    WHERE ol.prt_id = prt_id
                    AND c.cli_price_level = ppr_sort_idx
                )
            )
        ELSE
            (ol.prt_dscnt / 100)::NUMERIC(17,2)
    END AS net_dscnt,

    --Order total footer
    oh.ord_pkg_cost,
    oh.ord_tship_rate,
    oh.ord_ttax1_amnt,
    oh.ord_ttax2_amnt
    --TODO : Remove sub total and grand total statements from VBA, place them here


    FROM order_header AS oh
    JOIN order_line AS ol ON ol.ord_id = oh.ord_id
    JOIN part AS p ON p.prt_id = ol.prt_id
    JOIN part_group AS pg ON pg.pgr_id = p.pgr_id
    JOIN client AS c ON c.cli_id = oh.cli_id
    JOIN salesman s ON c.sal_id = s.sal_id
    JOIN orc_type oc ON oc.orc_type_idx = oh.ord_type
    JOIN ord_status os ON os.ord_status_idx = oh.ord_status

    WHERE orl_kitmaster_id = 0
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
    AND oh.ord_status = 'D'
    AND oc.ord_type = 'Blanket Order'
    ORDER BY sal_name, ord_no, orl_sort_idx
)
DROP VIEW IF EXISTS client_contracts;
CREATE OR REPLACE VIEW client_contracts AS (
 SELECT c.cli_no,
    co.con_no,
    p.prt_no,
        CASE
            WHEN cpl.prt_price = (-1)::numeric THEN NULL::numeric
            ELSE cpl.prt_price
        END AS prt_price,
        CASE
            WHEN cpl.prt_dscnt = (-1)::numeric THEN NULL::numeric
            WHEN cpl.prt_dscnt = 0::numeric THEN NULL::numeric
            ELSE cpl.prt_dscnt
        END AS prt_dscnt
   FROM client_contract cc
   JOIN client c ON c.cli_id = cc.cli_id
   JOIN contract co ON co.con_id = cc.con_id
   LEFT JOIN contract_part_line cpl ON cpl.con_id = co.con_id
   LEFT JOIN part p ON p.prt_id = cpl.prt_id
)
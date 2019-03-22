CREATE OR REPLACE FUNCTION description_notes_dev(integer, bigint)
  RETURNS TABLE(start_idx bigint, end_idx bigint) AS
$BODY$ 
BEGIN
RETURN QUERY
WITH temp_cte AS (
        SELECT * 
        FROM order_line 
        WHERE ord_no = $1
        AND orl_id = $2
)

SELECT (
        SELECT ol.orl_sort_idx
        FROM order_line ol
        WHERE ol.ord_no = temp_cte.ord_no
        AND temp_cte.orl_sort_idx < ol.orl_sort_idx 
        AND ol.orl_kitmaster_id = 0
        AND prt_no = ''
        order by ol.orl_sort_idx asc
        LIMIT 1
) AS start_idx,
CASE 
    WHEN EXISTS (
        SELECT order_line.prt_no 
        FROM order_line 
        JOIN temp_cte ON order_line.ord_no = temp_cte.ord_no 
        WHERE order_line.ord_no = temp_cte.ord_no
        and temp_cte.orl_sort_idx < order_line.orl_sort_idx 
        AND order_line.prt_no <> ''
    ) THEN (
        SELECT
        CASE WHEN (
            SELECT ol.orl_sort_idx
            FROM order_line ol
            JOIN temp_cte ON ol.ord_no = temp_cte.ord_no
            WHERE ol.ord_no = temp_cte.ord_no
            AND ol.orl_sort_idx 
            BETWEEN temp_cte.orl_sort_idx + 1 and (
                SELECT orl_sort_idx 
                from order_line ol2 
                WHERE ord_no = temp_cte.ord_no
                and temp_cte.orl_sort_idx < ol2.orl_sort_idx 
                AND prt_no <> ''
                order by orl_id ASC LIMIT 1
            ) - 1
            AND ol.prt_desc <> ''
            order by ol.orl_sort_idx DESC
            LIMIT 1
        ) IS NULL THEN (
            SELECT ol.orl_sort_idx
            FROM order_line ol 
            JOIN temp_cte ON ol.ord_no = temp_cte.ord_no 
            WHERE ol.ord_no = temp_cte.ord_no
                AND ol.orl_kitmaster_id = 0
                AND ol.prt_no = ''
            ORDER BY ol.orl_sort_idx DESC
            LIMIT 1
        ) ELSE (
            SELECT ol.orl_sort_idx
            FROM order_line ol
            JOIN temp_cte ON ol.ord_no = temp_cte.ord_no
            WHERE ol.ord_no = temp_cte.ord_no
            AND ol.orl_sort_idx 
            BETWEEN temp_cte.orl_sort_idx + 1 and (
                SELECT orl_sort_idx 
                from order_line ol2 
                WHERE ord_no = temp_cte.ord_no
                and temp_cte.orl_sort_idx < ol2.orl_sort_idx 
                AND prt_no <> ''
                order by orl_id DESC LIMIT 1
            ) - 1
            AND ol.prt_desc <> ''
            order by ol.orl_sort_idx DESC
            LIMIT 1
        ) END
    ) ELSE (
        SELECT ol.orl_sort_idx
        FROM order_line ol
        JOIN temp_cte ON ol.ord_no = temp_cte.ord_no
        WHERE ol.ord_no = temp_cte.ord_no
        AND ol.orl_sort_idx 
        BETWEEN temp_cte.orl_sort_idx + 1 and (
            SELECT ol2.orl_sort_idx 
            from order_line ol2 
            WHERE ol2.ord_no = temp_cte.ord_no
            and temp_cte.orl_sort_idx < ol2.orl_sort_idx 
            AND ol2.prt_desc <> ''
            order by ol2.orl_sort_idx DESC LIMIT 1
        )
        order by ol.orl_sort_idx DESC
        LIMIT 1
    )
END AS end_idx
FROM temp_cte
;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE


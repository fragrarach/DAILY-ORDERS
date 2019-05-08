CREATE OR REPLACE FUNCTION description_notes(integer, bigint)
  RETURNS TABLE(start_idx bigint, end_idx bigint) AS
$BODY$ 
BEGIN
RETURN QUERY
SELECT
(
    SELECT orl_sort_idx 
    FROM order_line 
    WHERE ord_no = $1
    AND prt_no = ''
    AND orl_sort_idx > (
        SELECT orl_sort_idx 
        FROM order_line 
        WHERE orl_id = $2
    )
    ORDER BY orl_sort_idx ASC
    LIMIT 1
)::bigint as start_idx,

(
SELECT CASE
    WHEN EXISTS (
        SELECT orl_sort_idx 
        FROM order_line 
        WHERE ord_no = $1
        AND prt_no = ''
        AND orl_sort_idx > (
            SELECT orl_sort_idx 
            FROM order_line 
            WHERE orl_id = $2
        )
    ) 
    AND EXISTS (
        SELECT orl_sort_idx 
        FROM order_line 
        WHERE ord_no = $1
        AND prt_no <> ''
        AND orl_sort_idx > (
            SELECT orl_sort_idx 
            FROM order_line 
            WHERE orl_id = $2
        )
    )
    THEN (
        SELECT orl_sort_idx - 1
        FROM order_line 
        WHERE ord_no = $1
        AND prt_no <> ''
        AND orl_sort_idx > (
            SELECT orl_sort_idx 
            FROM order_line 
            WHERE orl_id = $2
        )
        ORDER BY orl_sort_idx ASC
        LIMIT 1
    )

    ELSE (
        SELECT orl_sort_idx
        FROM order_line 
        WHERE ord_no = $1
        AND prt_no = ''
        AND orl_sort_idx > (
            SELECT orl_sort_idx 
            FROM order_line 
            WHERE orl_id = $2
        )
        ORDER BY orl_sort_idx DESC
        LIMIT 1
    )
END
)::bigint AS end_idx
;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE


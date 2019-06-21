CREATE OR REPLACE FUNCTION daily_orders_notify()
  RETURNS trigger AS
$BODY$
BEGIN

IF
    tg_table_name = 'order_header'
THEN

    IF 
        tg_op = 'UPDATE' 
        AND (
            NEW.ord_date <> now()::DATE 
            OR NEW.ord_no IN (
                SELECT ord_no 
                FROM dblink('dbname=LOG hostaddr=192.168.0.250 port=5493 user=SIGM', 'select * from daily_orders') AS t1(ord_no INTEGER)
            )
        )
    THEN
        IF 
            OLD.ord_status = 'E'
            AND NEW.ord_status NOT IN ('C', 'E', 'F')
        THEN
            PERFORM pg_notify(
                'daily_orders', '['
                || 'CONVERTED QUOTE' || '], ['
                || NEW.ord_no || ']'
            );
        ELSIF
            OLD.ord_status = 'D'
            AND NEW.ord_status IN ('A', 'B')
        THEN
            PERFORM pg_notify(
                'daily_orders', '['
                || 'CONVERTED PENDING' || '], ['
                || NEW.ord_no || ']'
            );
        ELSIF
            OLD.ord_status <> 'C'
            AND NEW.ord_status = 'C'
        THEN
            PERFORM pg_notify(
                'daily_orders', '['
                || 'CANCELLED ORDER' || '], ['
                || NEW.ord_no || ']'
            );
        END IF;
    END IF;
    
ELSIF
    tg_table_name = 'order_line'
THEN

    IF 
        tg_op = 'UPDATE' 
        AND (
            EXISTS (
                SELECT ord_id 
                FROM order_header 
                WHERE order_header.ord_no = NEW.ord_no 
                AND order_header.ord_date <> now()::DATE
            )
            OR NEW.ord_no IN (
                SELECT ord_no 
                FROM dblink('dbname=LOG hostaddr=192.168.0.250 port=5493 user=SIGM', 'select * from daily_orders') AS t1(ord_no INTEGER)
            )
        )
    THEN
        IF 
            OLD.prt_no = ''
            AND NEW.prt_no <> ''
        THEN
            PERFORM pg_notify(
                'daily_orders', '['
                || 'ADDED PART' || '], ['
                || NEW.ord_no || '], ['
                || NEW.orl_id || ']'
            );
        END IF;
        
        IF 
            OLD.orl_price <> NEW.orl_price
        THEN
            PERFORM pg_notify(
                'daily_orders', '['
                || 'PRICE CHANGED' || '], ['
                || NEW.ord_no || '], ['
                || NEW.orl_id || '], ['
                || OLD.orl_price || ']'
            );
        END IF;
        
    ELSIF
        tg_op = 'DELETE'
        AND (
            EXISTS (
                SELECT ord_id 
                FROM order_header 
                WHERE order_header.ord_no = OLD.ord_no 
                AND order_header.ord_date <> now()::DATE
            )
            OR OLD.ord_no IN (
                SELECT ord_no 
                FROM dblink('dbname=LOG hostaddr=192.168.0.250 port=5493 user=SIGM', 'select * from daily_orders') AS t1(ord_no INTEGER)
            )
        )
    THEN
        IF OLD.prt_no <> '' THEN
            PERFORM pg_notify(
                'daily_orders', '['
                || 'REMOVED PART' || '], ['
                || OLD.ord_no || '], ['
                || OLD.orl_id || '], ['
                || OLD.orl_price || '], ['
                || OLD.prt_no || '], ['
                || OLD.orl_quantity || '], ['
                || OLD.prt_dscnt || ']'
            );
        END IF;
    END IF;
END IF;

RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION daily_orders_notify()
  OWNER TO "SIGM";
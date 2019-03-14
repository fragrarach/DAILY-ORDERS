DROP TRIGGER IF EXISTS daily_orders_notify ON order_header;
CREATE TRIGGER daily_orders_notify
  AFTER UPDATE OR INSERT OR DELETE
  ON order_header
  FOR EACH ROW
  EXECUTE PROCEDURE daily_orders_notify();
  
DROP TRIGGER IF EXISTS daily_orders_notify ON order_line;
CREATE TRIGGER daily_orders_notify
  AFTER UPDATE OR INSERT OR DELETE
  ON order_line
  FOR EACH ROW
  EXECUTE PROCEDURE daily_orders_notify();
  

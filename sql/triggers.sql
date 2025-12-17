-- 1. Функция, которая будет выполнять логику
CREATE OR REPLACE FUNCTION extend_auction_time()
RETURNS TRIGGER AS $$
DECLARE
    time_left INTERVAL;
BEGIN
    -- Считаем, сколько времени осталось до конца аукциона
    SELECT (end_time - NEW.bid_time) INTO time_left
    FROM auctions
    WHERE auction_id = NEW.auction_id;

    -- Если осталось меньше 5 минут (300 секунд)
    IF time_left < INTERVAL '5 minutes' THEN
        -- Продлеваем на 10 минут
        UPDATE auctions
        SET end_time = end_time + INTERVAL '10 minutes'
        WHERE auction_id = NEW.auction_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Сам триггер, который срабатывает ПОСЛЕ вставки ставки
CREATE TRIGGER trg_extend_auction
AFTER INSERT ON bids
FOR EACH ROW
EXECUTE FUNCTION extend_auction_time();


CREATE OR REPLACE FUNCTION update_auction_price()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE auctions
    SET current_price = NEW.amount
    WHERE auction_id = NEW.auction_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_price
AFTER INSERT ON bids
FOR EACH ROW
EXECUTE FUNCTION update_auction_price();

-- 1. Создаем универсальную функцию для записи логов
CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER AS $$
DECLARE
    current_user_id VARCHAR;
    old_data TEXT;
    new_data TEXT;
BEGIN
    current_user_id := 'system';

    -- Конвертируем данные в JSON
    IF (TG_OP = 'DELETE') THEN
        old_data := row_to_json(OLD)::TEXT;
        new_data := NULL;
    ELSIF (TG_OP = 'INSERT') THEN
        old_data := NULL;
        new_data := row_to_json(NEW)::TEXT;
    ELSE -- UPDATE
        old_data := row_to_json(OLD)::TEXT;
        new_data := row_to_json(NEW)::TEXT;
    END IF;

    -- Вставляем запись. В record_id пишем 0, чтобы не вызывать ошибку "нет такого столбца"
    -- Вся информация (включая ID) всё равно лежит внутри old_value/new_value
    INSERT INTO audit_log (table_name, operation_type, record_id, old_value, new_value, changed_by)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        0, -- БЕЗОПАСНАЯ ЗАГЛУШКА
        old_data,
        new_data,
        current_user_id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Заново вешаем триггеры
CREATE TRIGGER audit_users_changes
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION log_changes();

CREATE TRIGGER audit_items_changes
AFTER INSERT OR UPDATE OR DELETE ON items
FOR EACH ROW EXECUTE FUNCTION log_changes();

CREATE TRIGGER audit_auctions_changes
AFTER INSERT OR UPDATE OR DELETE ON auctions
FOR EACH ROW EXECUTE FUNCTION log_changes();
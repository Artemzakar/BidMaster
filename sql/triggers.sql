-- 1. Снайперская защита: если ставка сделана менее чем за 5 минут до конца,
-- продлеваем аукцион еще на 10 минут.
CREATE OR REPLACE FUNCTION extend_auction_time()
RETURNS TRIGGER AS $$
DECLARE
    time_left INTERVAL;
BEGIN
    -- Вычисляем разницу между окончанием и временем новой ставки
    SELECT (end_time - NEW.bid_time) INTO time_left
    FROM auctions
    WHERE auction_id = NEW.auction_id;

    IF time_left < INTERVAL '5 minutes' THEN
        UPDATE auctions
        SET end_time = end_time + INTERVAL '10 minutes'
        WHERE auction_id = NEW.auction_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_extend_auction
AFTER INSERT ON bids
FOR EACH ROW
EXECUTE FUNCTION extend_auction_time();


-- 2. Синхронизация цены: при каждой новой ставке обновляем current_price в таблице auctions.
-- Это избавляет от необходимости делать тяжелые агрегатные запросы (MAX) при каждом просмотре лота.
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


-- 3. Универсальный аудит изменений.
-- Используем row_to_json, чтобы функция могла работать с любой таблицей.
CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER AS $$
DECLARE
    old_data TEXT;
    new_data TEXT;
BEGIN
    -- Проверяем тип операции через системную переменную TG_OP
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

    -- Записываем изменения в общую таблицу логов
    INSERT INTO audit_log (table_name, operation_type, record_id, old_value, new_value, changed_by)
    VALUES (
        TG_TABLE_NAME, -- Системная переменная (имя таблицы)
        TG_OP,         -- Тип операции (INSERT/UPDATE/DELETE)
        0,             -- Заглушка для ID (так как структура таблиц разная)
        old_data,
        new_data,
        'system'
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Вешаем аудит на основные таблицы
CREATE TRIGGER audit_users_changes
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION log_changes();

CREATE TRIGGER audit_items_changes
AFTER INSERT OR UPDATE OR DELETE ON items
FOR EACH ROW EXECUTE FUNCTION log_changes();

CREATE TRIGGER audit_auctions_changes
AFTER INSERT OR UPDATE OR DELETE ON auctions
FOR EACH ROW EXECUTE FUNCTION log_changes();
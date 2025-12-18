CREATE OR REPLACE FUNCTION get_user_activity_score(target_user_id INT)
RETURNS DECIMAL(10, 2) AS $$
DECLARE
    total_bids INT;
    total_spent DECIMAL(15, 2);
    score DECIMAL(10, 2);
BEGIN
    -- Считаем количество ставок
    SELECT COUNT(*), COALESCE(SUM(amount), 0)
    INTO total_bids, total_spent
    FROM bids
    WHERE user_id = target_user_id;

    -- Формула рейтинга: (Кол-во ставок * 10) + (1% от суммы ставок)
    score := (total_bids * 10) + (total_spent * 0.01);

    RETURN score;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_auction_stats(start_date TIMESTAMP, end_date TIMESTAMP)
RETURNS TABLE (
    auction_status VARCHAR,
    total_count BIGINT,
    total_money DECIMAL(15, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        status::VARCHAR,
        COUNT(*),
        COALESCE(SUM(current_price), 0)
    FROM auctions
    WHERE start_time BETWEEN start_date AND end_date
    GROUP BY status;
END;
$$ LANGUAGE plpgsql;
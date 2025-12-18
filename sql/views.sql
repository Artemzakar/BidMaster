-- VIEW 1: Витрина активных лотов (Сложный JOIN)
-- Показывает лот, текущую цену, имя продавца и категорию одной строкой
CREATE OR REPLACE VIEW v_active_lots_details AS
SELECT
    a.auction_id,
    i.title AS item_title,
    i.description,
    u.username AS seller_name,
    a.current_price,
    a.end_time,
    (SELECT COUNT(*) FROM bids b WHERE b.auction_id = a.auction_id) AS total_bids
FROM auctions a
JOIN items i ON a.item_id = i.item_id
JOIN users u ON i.owner_id = u.user_id
WHERE a.status = 'active';

-- VIEW 2: Статистика продаж по категориям (Агрегация)
-- Показывает, какая категория приносит больше всего денег
CREATE OR REPLACE VIEW v_category_sales AS
SELECT
    c.name AS category_name,
    COUNT(a.auction_id) AS lots_sold,
    COALESCE(SUM(a.current_price), 0) AS total_revenue
FROM categories c
JOIN item_categories ic ON c.category_id = ic.category_id
JOIN items i ON ic.item_id = i.item_id
JOIN auctions a ON i.item_id = a.item_id
WHERE a.status IN ('finished', 'active') -- Учитываем активные и завершенные
GROUP BY c.name
ORDER BY total_revenue DESC;

-- VIEW 3: Рейтинг активности пользователей (Аналитика)
-- Кто больше всех тратит и делает ставок
CREATE OR REPLACE VIEW v_top_bidders AS
SELECT
    u.username,
    COUNT(b.bid_id) AS bids_count,
    MAX(b.amount) AS max_bid_amount,
    -- Используем нашу скалярную функцию, которую создали раньше!
    get_user_activity_score(u.user_id) AS activity_score
FROM users u
JOIN bids b ON u.user_id = b.user_id
GROUP BY u.user_id, u.username
ORDER BY activity_score DESC;
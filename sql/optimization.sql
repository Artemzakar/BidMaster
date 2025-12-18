-- Сценарий: Пользователь заходит в ЛК и хочет увидеть свои крупные ставки,
-- отсортированные от новых к старым.

-- Запускаем с EXPLAIN ANALYZE, чтобы увидеть реальное время выполнения
EXPLAIN ANALYZE
SELECT bid_id, amount, bid_time
FROM bids
WHERE user_id = 55
  AND amount > 1000
ORDER BY bid_time DESC;

-- Создаем составной B-Tree индекс.
-- Он покрывает сразу три поля:
-- 1. user_id (для быстрого поиска владельца)
-- 2. amount (для фильтрации по цене)
-- 3. bid_time (для мгновенной сортировки)

CREATE INDEX idx_bids_user_amount_time
ON bids(user_id, amount, bid_time DESC);

-- Проверка после оптимизации

EXPLAIN ANALYZE
SELECT bid_id, amount, bid_time
FROM bids
WHERE user_id = 55
  AND amount > 1000
ORDER BY bid_time DESC;

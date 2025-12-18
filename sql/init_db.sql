-- 1. Таблица пользователей (Покупатели, Продавцы, Эксперты)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Храним хэш, а не пароль
    role VARCHAR(20) CHECK (role IN ('admin', 'user', 'expert')) DEFAULT 'user',
    balance DECIMAL(15, 2) DEFAULT 0.00 CHECK (balance >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Категории искусства (Живопись, Скульптура и т.д.)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- 3. Предметы искусства (Лоты)
CREATE TABLE items (
    item_id SERIAL PRIMARY KEY,
    owner_id INT REFERENCES users(user_id) ON DELETE CASCADE, -- Если удалят юзера, удалятся и его предметы
    title VARCHAR(150) NOT NULL,
    description TEXT,
    year_created INT,
    is_verified BOOLEAN DEFAULT FALSE, -- Подтверждено ли экспертом
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Связь Многие-ко-Многим: Предметы и Категории
CREATE TABLE item_categories (
    item_id INT REFERENCES items(item_id) ON DELETE CASCADE,
    category_id INT REFERENCES categories(category_id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, category_id)
);

-- 5. Заключения экспертов
CREATE TABLE expert_reviews (
    review_id SERIAL PRIMARY KEY,
    item_id INT REFERENCES items(item_id) ON DELETE CASCADE,
    expert_id INT REFERENCES users(user_id),
    verdict VARCHAR(20) CHECK (verdict IN ('authentic', 'fake', 'suspicious')),
    comments TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Аукционы (Торги)
CREATE TABLE auctions (
    auction_id SERIAL PRIMARY KEY,
    item_id INT UNIQUE REFERENCES items(item_id), -- Один предмет торгуется только в одном активном аукционе
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    start_price DECIMAL(12, 2) NOT NULL CHECK (start_price > 0),
    current_price DECIMAL(12, 2) DEFAULT 0,
    status VARCHAR(20) CHECK (status IN ('planned', 'active', 'finished', 'cancelled')) DEFAULT 'planned',
    CONSTRAINT check_dates CHECK (end_time > start_time) -- Дата окончания должна быть позже начала
);

-- 7. Ставки (Транзакционная таблица)
CREATE TABLE bids (
    bid_id SERIAL PRIMARY KEY,
    auction_id INT REFERENCES auctions(auction_id) ON DELETE CASCADE,
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL, -- Если юзер удалился, история ставок остается
    amount DECIMAL(12, 2) NOT NULL,
    bid_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Авто-биддинг (Робот)
CREATE TABLE auto_bids (
    auto_bid_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    auction_id INT REFERENCES auctions(auction_id) ON DELETE CASCADE,
    max_limit DECIMAL(12, 2) NOT NULL, -- До какой суммы робот может торговаться
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, auction_id) -- Один робот на один аукцион от одного юзера
);

-- 9. Депонирование средств (Финансовая защита)
CREATE TABLE escrow_accounts (
    escrow_id SERIAL PRIMARY KEY,
    auction_id INT REFERENCES auctions(auction_id),
    buyer_id INT REFERENCES users(user_id),
    amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('held', 'released', 'refunded')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Журнал аудита (Кто и что менял)
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation_type VARCHAR(10), -- INSERT, UPDATE, DELETE
    record_id INT,
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(50), -- Имя пользователя или 'system'
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Системные логи (для батчевой загрузки и ошибок)
CREATE TABLE system_logs (
    log_id SERIAL PRIMARY KEY,
    level VARCHAR(10) CHECK (level IN ('INFO', 'WARNING', 'ERROR')),
    source VARCHAR(50),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
import csv
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# --- КОНФИГУРАЦИЯ ---
NUM_USERS = 1000
NUM_CATEGORIES = 10
NUM_ITEMS = 2000
NUM_AUCTIONS = 1500
NUM_BIDS = 200000
NUM_REVIEWS = 500
NUM_LOGS = 1000
NUM_AUTO_BIDS = 3000  # Новая таблица
NUM_ESCROWS = 400  # Новая таблица

output_dir = "data_import"
os.makedirs(output_dir, exist_ok=True)


def generate_users():
    print("1. Users...")
    with open(f"{output_dir}/users.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "email", "password_hash", "role", "balance"])
        for i in range(NUM_USERS):
            username = f"{fake.user_name()}_{i}"
            email = f"{username}@example.com"
            role = "expert" if random.random() < 0.05 else "user"
            balance = round(random.uniform(0, 1000000), 2)
            writer.writerow([username, email, "hashed_secret", role, balance])


def generate_categories():
    print("2. Categories...")
    with open(f"{output_dir}/categories.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "description"])
        cats = ["Живопись", "Скульптура", "Графика", "Фотография", "Нумизматика",
                "Мебель", "Ювелирка", "Керамика", "Книги", "Часы"]
        for c in cats:
            writer.writerow([c, fake.sentence()])


def generate_items():
    print("3. Items...")
    with open(f"{output_dir}/items.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["owner_id", "title", "description", "year_created", "is_verified"])
        for _ in range(NUM_ITEMS):
            owner_id = random.randint(1, NUM_USERS)
            title = fake.catch_phrase()
            desc = fake.text(max_nb_chars=100).replace("\n", " ")
            year = random.randint(1800, 2023)
            is_ver = random.choice([True, False])
            writer.writerow([owner_id, title, desc, year, is_ver])


def generate_item_categories():
    print("4. Item Categories...")
    with open(f"{output_dir}/item_categories.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "category_id"])
        for item_id in range(1, NUM_ITEMS + 1):
            cat_id = random.randint(1, NUM_CATEGORIES)
            writer.writerow([item_id, cat_id])


def generate_auctions():
    print("5. Auctions...")
    with open(f"{output_dir}/auctions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "start_time", "end_time", "start_price", "current_price", "status"])
        for i in range(1, NUM_AUCTIONS + 1):
            item_id = i
            start_time = fake.date_time_between(start_date='-60d', end_date='now')
            end_time = start_time + timedelta(days=random.randint(1, 14))
            if end_time < datetime.now():
                status = 'finished'
            else:
                status = 'active'
            price = round(random.uniform(100, 5000), 2)
            writer.writerow([item_id, start_time, end_time, price, price, status])


def generate_bids():
    print("6. Bids...")
    with open(f"{output_dir}/bids.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["auction_id", "user_id", "amount", "bid_time"])
        for _ in range(NUM_BIDS):
            auc_id = random.randint(1, NUM_AUCTIONS)
            u_id = random.randint(1, NUM_USERS)
            amt = round(random.uniform(100, 50000), 2)
            created = fake.date_time_between(start_date='-30d', end_date='now')
            writer.writerow([auc_id, u_id, amt, created])


def generate_expert_reviews():
    print("7. Expert Reviews...")
    with open(f"{output_dir}/expert_reviews.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "expert_id", "verdict", "comments", "review_date"])
        for _ in range(NUM_REVIEWS):
            item_id = random.randint(1, NUM_ITEMS)
            expert_id = random.randint(1, NUM_USERS)
            verdict = random.choice(["authentic", "fake", "suspicious"])
            comments = fake.sentence()
            created_at = fake.date_time_between(start_date='-60d', end_date='now')
            writer.writerow([item_id, expert_id, verdict, comments, created_at])


def generate_auto_bids():
    print("8. Auto Bids...")
    # Здесь важно соблюсти UNIQUE(user_id, auction_id)
    seen_pairs = set()
    with open(f"{output_dir}/auto_bids.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "auction_id", "max_limit", "created_at"])

        count = 0
        while count < NUM_AUTO_BIDS:
            u_id = random.randint(1, NUM_USERS)
            auc_id = random.randint(1, NUM_AUCTIONS)

            if (u_id, auc_id) in seen_pairs:
                continue  # Пропускаем дубликаты

            seen_pairs.add((u_id, auc_id))
            max_limit = round(random.uniform(5000, 100000), 2)
            created = fake.date_time_between(start_date='-30d', end_date='now')
            writer.writerow([u_id, auc_id, max_limit, created])
            count += 1


def generate_escrow_accounts():
    print("9. Escrow Accounts...")
    with open(f"{output_dir}/escrow_accounts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["auction_id", "buyer_id", "amount", "status", "updated_at"])
        for _ in range(NUM_ESCROWS):
            auc_id = random.randint(1, NUM_AUCTIONS)
            buyer_id = random.randint(1, NUM_USERS)
            amount = round(random.uniform(1000, 50000), 2)
            status = random.choice(['held', 'released', 'refunded'])
            updated = fake.date_time_between(start_date='-10d', end_date='now')
            writer.writerow([auc_id, buyer_id, amount, status, updated])


def generate_audit_log():
    print("10. Audit Log...")
    with open(f"{output_dir}/audit_log.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["table_name", "operation_type", "record_id", "changed_at", "changed_by"])
        for _ in range(NUM_LOGS):
            tbl = random.choice(["users", "items", "auctions"])
            op = random.choice(["INSERT", "UPDATE"])
            rec_id = random.randint(1, 1000)
            at = fake.date_time_between(start_date='-10d', end_date='now')
            by = str(random.randint(1, NUM_USERS))
            writer.writerow([tbl, op, rec_id, at, by])


if __name__ == "__main__":
    generate_users()
    generate_categories()
    generate_items()
    generate_item_categories()
    generate_auctions()
    generate_bids()
    generate_expert_reviews()
    generate_auto_bids()
    generate_escrow_accounts()
    generate_audit_log()
    print(f"\n✅ Файлы обновлены в {output_dir}/. Все 11 таблиц!")
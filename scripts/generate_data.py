import csv
import random
import os
from faker import Faker

fake = Faker()
# Количество данных для генерации
NUM_USERS = 1000
NUM_CATEGORIES = 10
NUM_ITEMS = 2000

# Создаем папку для данных, если нет
os.makedirs("data_import", exist_ok=True)


def generate_users():
    print(f"Генерируем {NUM_USERS} пользователей...")
    with open("data_import/users.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "email", "password_hash", "role", "balance"])

        for _ in range(NUM_USERS):
            profile = fake.simple_profile()
            username = profile["username"] + str(random.randint(1, 9999))
            email = fake.unique.email()
            password = "hashed_password_example"
            role = random.choices(["user", "expert"], weights=[95, 5])[0]  # 5% экспертов
            balance = round(random.uniform(0, 100000), 2)

            writer.writerow([username, email, password, role, balance])


def generate_categories():
    print(f"Генерируем {NUM_CATEGORIES} категорий...")
    categories = [
        "Живопись", "Скульптура", "Графика", "Фотография",
        "Нумизматика", "Антикварная мебель", "Ювелирные изделия",
        "Керамика", "Редкие книги", "Часы"
    ]
    with open("data_import/categories.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "description"])
        for cat in categories:
            writer.writerow([cat, fake.sentence()])


def generate_items():
    print(f"Генерируем {NUM_ITEMS} предметов...")
    # Нам нужно знать ID пользователей, но так как мы их еще не загрузили в БД,
    # будем считать, что ID идут от 1 до NUM_USERS (так работает SERIAL в Postgres)

    with open("data_import/items.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["owner_id", "title", "description", "year_created", "is_verified"])

        for _ in range(NUM_ITEMS):
            owner_id = random.randint(1, NUM_USERS)
            title = fake.catch_phrase()
            description = fake.text(max_nb_chars=200).replace("\n", " ")
            year = random.randint(1700, 2023)
            is_verified = random.choice([True, False])

            writer.writerow([owner_id, title, description, year, is_verified])


if __name__ == "__main__":
    generate_users()
    generate_categories()
    generate_items()
    print("Генерация завершена! Файлы лежат в папке data_import/")
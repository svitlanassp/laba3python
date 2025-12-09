import os
import sys
from decimal import Decimal
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_library.settings')
django.setup()

from faker import Faker
from datetime import timedelta, datetime, time
from django.utils import timezone
import random
from library_app.models import *

fake = Faker()

NUM_USERS = 600
NUM_GAMES = 200
NUM_DEV_PUB = 50
NUM_BIG_DEV = 10


def cleanup_data():
    Review.objects.all().delete()
    LibraryGame.objects.all().delete()
    OrderGame.objects.all().delete()
    Order.objects.all().delete()
    GameGenre.objects.all().delete()

    Game.objects.all().delete()
    Developer.objects.all().delete()
    Publisher.objects.all().delete()
    Genre.objects.all().delete()

    User.objects.filter(is_superuser=False).delete()

def game_title():
    generators = [
        lambda: " ".join(fake.word().title() for _ in range(random.randint(1, 3))),
        lambda: fake.color_name().title() + " " + fake.word().title(),
        lambda: fake.company().split()[0].title() + " " + fake.word().title(),
        lambda: fake.job().split()[0].title() + " " + fake.word().title(),
    ]
    title = random.choice(generators)()

    if random.random() < 0.25:
        title += ": " + " ".join(fake.word().title() for _ in range(random.randint(1, 3)))

    if random.random() < 0.25:
        title += f" {random.choice(['II','III','IV','V', str(fake.random_int(2, 9))])}"

    return title


def create_entities():
    genres_list = ["Action", "RPG", "Strategy", "Simulation", "Puzzle",
                   "Horror", "Sports", "Adventure", "Indie", "MMO", "Platformer",
                   "Survival", "Rogue-like"]

    for name in genres_list:
        Genre.objects.create(name=name)
    genres = list(Genre.objects.all())

    developers = []
    publishers = []
    for i in range(NUM_DEV_PUB):
        dev = Developer.objects.create(name=fake.company())
        developers.append(dev)
        publisher = Publisher.objects.create(name=fake.company())
        publishers.append(publisher)

    big_devs = developers[:NUM_BIG_DEV]
    big_pubs = publishers[:NUM_BIG_DEV]

    return genres, developers, publishers, big_devs, big_pubs

def create_users():
    users = []
    for i in range(NUM_USERS):
        user = User(
            username=fake.user_name() + str(i),
            email=fake.email(),
            balance=round(random.uniform(10, 5000), 2),
        )
        users.append(user)

    User.objects.bulk_create(users)
    return list(User.objects.all())

def create_games(developers,publishers,genres,big_devs,big_pubs):
    games = []
    game_genres_to_create = []

    try:
        indie_genre = next(g for g in genres if g.name == "Indie")
    except StopIteration:
        indie_genre = None

    for i in range(NUM_GAMES):
        is_big_studio_game = random.random() < 0.6

        if is_big_studio_game:
            developer_choice = random.choice(big_devs)
        else:
            developer_choice = random.choice(developers)

        if developer_choice in big_devs:
            price = round(random.uniform(39.99,69.99),2)
        else:
            price = round(random.uniform(15.99,39.99),2)

        if developer_choice in big_devs:
            publisher_choice = random.choice(big_pubs)
        else:
            publisher_choice = random.choice(publishers)

        game = Game(
            developer = developer_choice,
            publisher = publisher_choice,
            title = game_title(),
            price=price,
            release_date=timezone.now() - timedelta(days=random.randint(100, 1500))
        )
        games.append(game)

    Game.objects.bulk_create(games)
    games = list(Game.objects.all())

    for game in games:
        num_genres = random.randint(1,3)
        assigned_genres = random.sample(genres, min(num_genres,len(genres)))

        if game.developer in big_devs and indie_genre:
            assigned_genres = [g for g in assigned_genres if g != indie_genre]

            if not assigned_genres and len(genres) > 1:
                available_genres = [g for g in genres if g != indie_genre]
                assigned_genres.append(random.choice(available_genres))

        for genre in assigned_genres:
            game_genres_to_create.append(GameGenre(game=game,genre=genre))

    GameGenre.objects.bulk_create(game_genres_to_create)

    return games

def create_purchases(users,games):
    orders_to_create = []
    order_games_to_create = []
    library_games_to_create = []

    max_days_ago = 730
    NUM_ORDERS = random.randint(1500,2000)

    for i in range(NUM_ORDERS):
        user = random.choice(users)
        order_date = timezone.now() - timedelta(days=random.randint(1,max_days_ago))

        status_choice = random.choices(['complete','cancelled','pending'],weights=[0.90,0.05,0.05],k=1)[0]

        order = Order(
            user = user,
            total_amount = 0,
            status = status_choice,
            created_at = order_date,
        )
        orders_to_create.append(order)

    Order.objects.bulk_create(orders_to_create)
    orders = list(Order.objects.all())

    total_library_entries = 0

    for order in orders:
        num_games_in_order = random.randint(1,3)

        # Вибираємо випадкову кількість ігор з ПОВНОГО списку
        # Це збалансує вибірку, а не обмежить її лише найдорожчими
        selection_pool = games  # Використовуємо всі ігри

        # Вибираємо випадкову підмножину (наприклад, 20% ігор) для формування унікального замовлення
        temp_games = random.sample(selection_pool, min(int(len(selection_pool) * 0.2), len(selection_pool)))

        # Сортуємо тимчасовий пул за ціною, щоб іноді брати дорожчі
        # АБО просто беремо випадкові ігри

        selected_games = random.sample(temp_games, min(num_games_in_order, len(temp_games)))

        if selection_pool:
            selected_games = random.sample(selection_pool, min(num_games_in_order, len(selection_pool)))
        else:
            continue

        order_total = Decimal('0.00')

        for game in selected_games:
            original_price = game.price

            days_since_release = (order.created_at.date() - game.release_date).days

            discount_chance = 0.05
            max_discount = 0.20
            purchase_price = original_price

            if days_since_release > 180:
                discount_chance = 0.3
                max_discount = 0.8

            if random.random() < discount_chance:
                discount_rate = round(random.uniform(0.10, max_discount), 2)
                discount_rate_decimal = Decimal(str(discount_rate))
                purchase_price = round(original_price * (Decimal(1) - discount_rate_decimal), 2)
            else:
                purchase_price = original_price

            purchase_price = max(purchase_price, Decimal('1.99'))

            order_games_to_create.append(OrderGame(
                order=order,
                game=game,
                price_at_purchase=purchase_price
            ))
            order_total += purchase_price

            if order.status == 'complete':
                library_obj, created = Library.objects.get_or_create(user=order.user)
                is_popular_game = game.price > 40

                if is_popular_game:
                    weights = [0.40, 0.35, 0.15, 0.08, 0.02]
                    max_hours_for_hardcore = 1100
                else:
                    weights = [0.55, 0.30, 0.10, 0.04, 0.01]
                    max_hours_for_hardcore = 500

                playtime_range_choice = random.choices(
                    ['zero','low','medium','high','hardcore'],
                    weights = weights,
                    k=1
                )[0]

                if playtime_range_choice == 'zero':
                    playtime = 0
                elif playtime_range_choice == 'low':
                    playtime = random.randint(1,10)
                elif playtime_range_choice == 'medium':
                    playtime = random.randint(11,100)
                elif playtime_range_choice == 'high':
                    playtime = random.randint(101,max_hours_for_hardcore//4)
                elif playtime_range_choice == 'hardcore':
                    playtime = random.randint(max_hours_for_hardcore//4+1,max_hours_for_hardcore)

                library_games_to_create.append(LibraryGame(
                    library = library_obj,
                    game = game,
                    playtime_hours = playtime,
                    purchase_date = order.created_at,
                ))
                total_library_entries += 1

        order.total_amount = order_total
        order.save()

    OrderGame.objects.bulk_create(order_games_to_create)
    LibraryGame.objects.bulk_create(library_games_to_create,ignore_conflicts=True)

    print(
        f"Створено замовлень: {len(orders)}. Створено записів OrderGame: {len(order_games_to_create)}. Створено записів LibraryGame: {total_library_entries}")
    return list(LibraryGame.objects.all())

def create_reviews(library_games, all_games, big_devs):
    reviews_to_create = []
    sample_size = min(int(len(library_games)*0.9),3000)

    library_sample = random.sample(library_games, sample_size)

    for library_entry in library_sample:
        user = library_entry.library.user
        game = library_entry.game

        if game.developer in big_devs:
            rating = random.choices([4,5,3,2,1], weights=[0.40,0.40,0.15,0.04,0.01], k=1)[0]
        else:
            rating = random.choices([4,5,3,2,1], weights=[0.25,0.20,0.40,0.10,0.05], k=1)[0]

        if random.random() < 0.25:
            review_comment = None
        else:
            review_comment = fake.text(max_nb_chars=100)

        date_obj = library_entry.purchase_date
        naive_dt = datetime.combine(date_obj, time(0, 0))
        naive_dt_plus_days = naive_dt + timedelta(days=random.randint(1, 180))
        aware_date = timezone.make_aware(naive_dt_plus_days)

        review = Review(
            user = user,
            game = game,
            rating = rating,
            comment = review_comment,
            created_at=aware_date
        )
        reviews_to_create.append(review)

    Review.objects.bulk_create(reviews_to_create)
    print(f"Створено відгуків: {len(reviews_to_create)}")
    return reviews_to_create



def run_seeder():
    print("--- Початок наповнення бази даних ---")

    # Крок 0: Очищення
    # (Для чистоти, використовуйте зовнішній SQL TRUNCATE, але якщо тут DELETE, теж працює)
    cleanup_data()

    # Крок 1: Базові сутності (Жанри, Розробники, Видавці)
    genres, developers, publishers, big_devs, big_pubs = create_entities()
    print(f"Створено сутностей: Жанрів ({len(genres)}), Розробників ({len(developers)})")

    # Крок 2: Користувачі
    users = create_users()
    print(f"Створено користувачів: {len(users)}")

    # Крок 3: Ігри та зв'язки GameGenre
    games = create_games(developers, publishers, genres, big_devs, big_pubs)
    print(f"Створено ігор: {len(games)}")

    # Крок 4: Замовлення, Продажі та Бібліотеки
    # Цей крок повертає список створених LibraryGame
    library_games = create_purchases(users, games)
    # Виведення статистики відбувається всередині create_purchases

    # Крок 5: Створення Відгуків (ТЕПЕР АКТИВОВАНО!)
    # Передаємо LibraryGame для знаходження власників та Games/Devs для логіки рейтингу
    create_reviews(library_games, games, big_devs)

    print("\n--- Генерація даних завершена ---")

    return users, games, library_games

if __name__ == '__main__':
    run_seeder()
import pandas as pd
from sqlalchemy import URL, create_engine, text

# TODO: Uzupełnij dane do połączenia z bazą danych
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="1234",
    host="localhost",
    port=5432,
    database="dvdrental",
)

try:
    engine = create_engine(db_url)
    connection = engine.connect()
    print("Pomyślnie nawiązano połączenie z bazą danych.")
except Exception as e:
    print(f"Błąd podczas łączenia z bazą danych: {e}")

def number_films_in_category(category_id: int) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o ilość filmów w zadanej kategori przez id kategorii."""
    # Walidacja danych wejściowych
    if not isinstance(category_id, int) or category_id < 0:
        return None

    query = """
        SELECT c.name AS category, COUNT(fc.film_id) AS count
        FROM category c
        JOIN film_category fc ON c.category_id = fc.category_id
        WHERE c.category_id = %(category_id)s
        GROUP BY c.name;
    """

    try:
        df = pd.read_sql(query, engine, params={"category_id": category_id})
        return df if not df.empty else None
    except Exception:
        return None


def number_film_by_length(
    min_length: Union[int, float] = 0, max_length: Union[int, float] = 1e6
) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o ilość filmów dla poszczegulnych długości pomiędzy wartościami min_length a max_length."""
    # Walidacja danych wejściowych
    if not isinstance(min_length, (int, float)) or not isinstance(
        max_length, (int, float)
    ):
        return None
    if min_length > max_length or min_length < 0:
        return None

    query = """
        SELECT length, COUNT(film_id) AS count
        FROM film
        WHERE length BETWEEN %(min_length)s AND %(max_length)s
        GROUP BY length
        ORDER BY length;
    """

    try:
        df = pd.read_sql(
            query,
            engine,
            params={"min_length": min_length, "max_length": max_length},
        )
        return df if not df.empty else None
    except Exception:
        return None


def avg_amount_by_length(length: Union[int, float]) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o średnią wartość wypożyczenia filmów dla zadanej długości length."""
    # Walidacja danych wejściowych
    if not isinstance(length, (int, float)) or length < 0:
        return None

    # Łączymy film -> inventory -> rental -> payment, aby wyliczyć średnią kwotę (amount)
    query = """
        SELECT f.length, AVG(p.amount) AS avg
        FROM film f
        JOIN inventory i ON f.film_id = i.film_id
        JOIN rental r ON i.inventory_id = r.inventory_id
        JOIN payment p ON r.rental_id = p.rental_id
        WHERE f.length = %(length)s
        GROUP BY f.length;
    """

    try:
        df = pd.read_sql(query, engine, params={"length": length})
        return df if not df.empty else None
    except Exception:
        return None


def client_by_sum_length(sum_min: Union[int, float]) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o sumaryczny czas wypożyczonych filmów przez klientów powyżej zadanej wartości."""
    # Walidacja danych wejściowych
    if not isinstance(sum_min, (int, float)) or sum_min < 0:
        return None

    # Łączymy customer -> rental -> inventory -> film
    query = """
        SELECT c.first_name, c.last_name, SUM(f.length) AS sum
        FROM customer c
        JOIN rental r ON c.customer_id = r.customer_id
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film f ON i.film_id = f.film_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        HAVING SUM(f.length) > %(sum_min)s
        ORDER BY sum ASC, c.first_name ASC, c.last_name ASC;
    """

    try:
        df = pd.read_sql(query, engine, params={"sum_min": sum_min})
        return df if not df.empty else None
    except Exception:
        return None


def category_statistic_length(name: str) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o statystykę długości filmów w kategorii o zadanej nazwie."""
    # Walidacja danych wejściowych
    if not isinstance(name, str) or not name.strip():
        return None

    query = """
        SELECT 
            c.name AS category, 
            ROUND(AVG(f.length), 2) AS avg, 
            SUM(f.length) AS sum, 
            MIN(f.length) AS min, 
            MAX(f.length) AS max
        FROM category c
        JOIN film_category fc ON c.category_id = fc.category_id
        JOIN film f ON fc.film_id = f.film_id
        WHERE LOWER(c.name) = LOWER(%(name)s)
        GROUP BY c.name;
    """

    try:
        df = pd.read_sql(query, engine, params={"name": name})
        return df if not df.empty else None
    except Exception:
        return None

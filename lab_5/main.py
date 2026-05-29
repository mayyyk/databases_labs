import pandas as pd
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# TODO: Uzupełnij dane do połączenia z bazą danych
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="1234",
    host="localhost",
    port=5432,
    database="dvdrental",
)
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        print("[INFO] Successfully connected to the database.")
except SQLAlchemyError as e:
    print(f"[ERROR] Failed to connect to the database: {e}")


def customers_by_last_name(last_name: str) -> pd.DataFrame | None:
    """
    Zwraca klientów o podanym nazwisku.

    Parameters:
        last_name (str): Nazwisko klienta (np. 'Smith').

    Returns:
        pd.DataFrame: DataFrame (customer_id, first_name, last_name, email)
            posortowany alfabetycznie po imieniu, następnie po customer_id,
            lub `None` w razie błędu.
    """
    try:
        df = pd.read_sql(text("SELECT customer_id, first_name, last_name, email FROM customer WHERE last_name=:last_name ORDER BY first_name, customer_id"), con=engine, params={"last_name": last_name})
        return df
    except Exception as e:
        print(e)
        return None

def payments_above_amount(amount: float) -> pd.DataFrame | None:
    """
    Zwraca płatności przekraczające podaną kwotę wraz z danymi klienta.

    Parameters:
        amount (float): Minimalna kwota płatności (nieujemna).

    Returns:
        pd.DataFrame: DataFrame (first_name, last_name, amount, payment_date)
            posortowany malejąco po kwocie, następnie malejąco po dacie płatności,
            następnie malejąco po payment_id,
            lub `None` w razie błędu.
    """
    try:
        df = pd.read_sql(text("""
SELECT c.first_name, c.last_name, p.amount, p.payment_date 
            FROM payment p
            JOIN customer c ON p.customer_id = c.customer_id
            WHERE p.amount > :amount
            ORDER BY p.amount DESC, p.payment_date DESC, p.payment_id DESC
"""), con=engine, params={"amount": amount})
        return df
    except Exception as e:
        print(e)
        return None


def active_customers_in_store(store_id: int) -> pd.DataFrame | None:
    """
    Zwraca aktywnych klientów przypisanych do podanego sklepu.

    Parameters:
        store_id (int): Identyfikator sklepu (1 lub 2).

    Returns:
        pd.DataFrame: DataFrame (customer_id, first_name, last_name, email)
            posortowany alfabetycznie po nazwisku i imieniu, następnie po customer_id,
            lub `None` w razie błędu.
    """
    try:
        df = pd.read_sql(text("""
    SELECT customer_id, first_name, last_name, customer_id, email
            FROM customer 
            WHERE store_id=:store_id AND active = 1
            ORDER BY last_name, first_name, customer_id
"""), con=engine, params={"store_id": store_id})
        return df
    except Exception as e:
        print(e)
        return None



def unreturned_rentals() -> pd.DataFrame | None:
    """
    Zwraca wypożyczenia, które nie zostały jeszcze zwrócone (return_date IS NULL).

    Returns:
        pd.DataFrame: DataFrame (rental_id, customer_id, title, rental_date)
            posortowany rosnąco po dacie wypożyczenia, następnie po rental_id,
            lub `None` w razie błędu.
    """
    try:
        df = pd.read_sql(text("""
SELECT r.rental_id, r.customer_id, f.title, r.rental_date 
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            WHERE r.return_date IS NULL
            ORDER BY r.rental_date, r.rental_id
"""), con=engine)
        return df
    except Exception as e:
        print(e)
        return None


def customer_rentals_in_range(
    customer_id: int, start_date: str, end_date: str
) -> pd.DataFrame | None:
    """
    Zwraca wypożyczenia danego klienta w podanym przedziale dat.

    Parameters:
        customer_id (int): Identyfikator klienta (liczba całkowita dodatnia).
        start_date (str): Początek przedziału dat w formacie 'YYYY-MM-DD'.
        end_date (str): Koniec przedziału dat w formacie 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: DataFrame (rental_id, title, rental_date, return_date)
            posortowany rosnąco po dacie wypożyczenia, następnie po rental_id,
            lub `None` w razie błędu.
    """
    try:
        query = text("""
            SELECT r.rental_id, f.title, r.rental_date, r.return_date 
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            WHERE r.customer_id = :customer_id 
              AND r.rental_date BETWEEN :start_date AND :end_date
            ORDER BY r.rental_date, r.rental_id
        """)
        return pd.read_sql(query, con=engine, params={
            "customer_id": customer_id, 
            "start_date": start_date, 
            "end_date": end_date
        })
    except Exception:
        return None

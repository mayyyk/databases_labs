import pickle
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
import pandas.io.sql as psql
import sqlalchemy
from sqlalchemy import create_engine, text

connector = "postgresql"
user = "postgres"
password = "9731"
host = "localhost"
port = "5432"
dbname = "dvdrental"

db_string = f"{connector}://{user}:{password}@{host}:{port}/{dbname}"
db = create_engine(db_string)


def film_in_category(category_id: int) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego id kategorii.
    Przykład wynikowej tabeli:
    |   |title          |language    |category|
    |0	|Amadeus Holy	|English	|Action|

    Tabela wynikowa ma być posortowana po tylule filmu i języku.

    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.

    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie

    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    """
    if not isinstance(category_id, int) or not (category_id >= 0):
        return None

    query = text(
        """
        --sql
        SELECT f.title, l.name AS language, c.name AS category 
        FROM film f
        JOIN language l ON f.language_id = l.language_id
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE c.category_id = :cat_id
        ORDER BY f.title, l.name

    """
    )

    try:
        with db.connect() as conn:
            df = pd.read_sql(query, conn, params={"cat_id": category_id})
            return df
    except Exception as e:
        print(e)
        return None


def client_from_city(city: str) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o listę klientów z zadanego miasta przez wartość city.
    Przykład wynikowej tabeli:
    |   |city	    |first_name	|last_name
    |0	|Athenai	|Linda	    |Williams

    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.

    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.

    Parameters:
    city (str): nazwa miaste dla którego mamy sporządzić listę klientów

    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    """
    if not isinstance(city, str):
        return None
    query = text(
        """
    SELECT c.city as city, cus.first_name as first_name, cus.last_name as last_name 
    FROM customer cus
    JOIN address adr ON cus.address_id = adr.address_id
    JOIN city c ON adr.city_id = c.city_id
    WHERE c.city = :city
    ORDER BY last_name, first_name
"""
    )
    try:
        with db.connect() as conn:
            df = pd.read_sql(query, conn, params={"city": city})
            return df
    except Exception as e:
        print(e)
        return None


def actor_in_film(title: str) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o imię i nazwisko aktorów rających w filmie o zadanym tytule,
    Przykład wynikowej tabeli:
    |   |title          |first_name    |last_name|
    |0	|Amadeus Holy	|Val	       |Bolger|

    Tabela wynikowa ma być posortowana po last_name.

    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.

    Parameters:
    title (str): tytuł filmu dla którego następuje wyszukiwanie

    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    """
    if not isinstance(title, str):
        return None
    query = text(
        """
    SELECT film.title AS title, act.first_name AS name, act.last_name AS surname
    FROM actor act
    JOIN film_actor fact ON act.actor_id = fact.actor_id
    JOIN film ON fact.film_id = film.film_id
    WHERE film.title = :title
    ORDER BY last_name
"""
    )
    try:
        with db.connect() as conn:
            df = pd.read_sql(query, conn, params={"title": title})
            return df
    except Exception as e:
        print(e)
        return None


def film_in_language(language: str) -> pd.DataFrame:
    """Funkcja zwracająca wynik zapytania do bazy o tytuły filmów o  zadanym języku,
    Przykład wynikowej tabeli:
    |   |language       |title
    |0	|English        |Amadeus Holy

    Tabela wynikowa ma być posortowana po tytule.

    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.

    Parameters:
    title (str): tytuł filmu dla którego następuje wyszukiwanie

    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    """
    if not isinstance(language, str):
        return None
    query = text(
        """
    SELECT l.name AS language, f.title AS title
    FROM film f
    JOIN language l ON f.language_id = l.language_id
    WHERE l.name = :language
    ORDER BY f.title
    """
    )
    try:
        with db.connect() as conn:
            df = pd.read_sql(query, conn, params={"language": language})
            return df
    except Exception as e:
        print(e)
        return None


if __name__ == "__main__":
    pass

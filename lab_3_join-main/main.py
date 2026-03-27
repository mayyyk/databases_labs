import numpy as np
import pickle

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

from typing import Union, List, Tuple

host = "localhost"
port = "5432"
dbname = "dvdrental"
user = "postgres"
password = "9731"

connector = "postgresql"

connection = pg.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password,
)


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
    if not isinstance(category_id, int) or not (category_id > 1):
        return None
    command = """
    --sql
    select title, language, category from ... SORT BY title, language
    """
    df = pd.read_sql(command, con=connection)
    return df


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

    pass


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
    pass


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
    pass


if __name__ == "__main__":
    pass

# =================================  TESTY  ===================================
# Testy do tego pliku zostały podzielone na dwie kategorie:
#
#  1. `..._invalid_input`:
#     - Sprawdzające poprawną obsługę nieprawidłowych danych wejściowych.
#
#  2. `..._correct_solution`:
#     - Weryfikujące poprawność wyników dla prawidłowych danych wejściowych.
# =============================================================================
import pandas as pd
from sqlalchemy import URL, create_engine, text
import re

connector = "postgresql+psycopg2"
username = "postgres"
password = "9731"
host = "localhost"
port = 5432
dbname = "dvdrental"

db_url = URL.create(
    drivername=connector,
    username=username,
    password=password,
    host=host,
    port=port,
    database=dbname,
)
engine = create_engine(db_url)


def film_in_category(
    category: int | str, case_sensitive: bool = True
) -> pd.DataFrame | None:
    """Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz
    kategorię dla zadanego:
        - id: jeżeli `category` jest typu `int`
        - name: jeżeli `category` jest typu `str`

    Przykład wynikowej tabeli:
    |   |      title      | language | category |
    |---|-----------------|----------|----------|
    |0  |Amadeus Holy     |English   |Action    |
    |1  |American Circus  |English   |Action    |

    Tabela wynikowa powinna być posortowana w kolejności:
        - tytuł filmu (alfabetycznie),
        - język (alfabetycznie).

    Args:
        category (int | str): Nazwa lub id kategorii filmowej.
        case_sensitive (bool): Flaga informująca czy nazwa kategorii ma być
            czuła na wielkość liter (domyślnie `True`).

    Returns:
        pd.DataFrame: DataFrame zawierający wyniki zapytania.
        Jeżeli dane wejściowe są niepoprawne funkcja zwraca `None`.
    """
    if not isinstance(category, (str, int)) or not isinstance(case_sensitive, bool):
        return None
    if isinstance(category, int):
        sql_query = text(
            """--sql
        SELECT f.title, l.name, f_cat.category_id
        FROM film f
        JOIN language l ON f.language_id = l.language_id
        JOIN film_category f_cat ON f.film_id = f_cat.film_id
        WHERE category_id = :category
        ORDER BY f.title, l.name
    """
        )
    elif isinstance(category, str):
        method = "LIKE" if case_sensitive else "ILIKE"
        sql_query = text(
            f"""--sql
        SELECT f.title, l.name, c.name
        FROM film f
        JOIN language l ON f.language_id = l.language_id
        JOIN film_category f_cat ON f.film_id = f_cat.film_id
        JOIN category c ON f_cat.category_id = c.category_id 
        WHERE c.name {method} :category 
        ORDER BY f.title, l.name
    """
        )

    df = pd.read_sql(sql_query, con=engine, params={"category": category})
    return df


def film_cast(title: str) -> pd.DataFrame | None:
    """Funkcja zwracająca wynik zapytania do bazy o obsadę filmu o zadanym
    tytule.

    Przykład wynikowej tabeli:
    |   | first_name | last_name |
    |---|------------|-----------|
    |0	|Val         |Bolger     |
    |1  |Penelope    |Cronyn     |

    Tabela wynikowa powinna być posortowana w kolejności:
        - nazwisko aktora (alfabetycznie),
        - imię aktora (alfabetycznie).

    Args:
        title (str): Tytuł filmu.

    Returns:
        pd.DataFrame: DataFrame zawierający wyniki zapytania.
        Jeżeli dane wejściowe są niepoprawne funkcja zwraca `None`.
    """
    if not isinstance(title, str):
        return None
    sql_query = text(
        """--sql
        SELECT f.title, a.first_name, a.last_name
        FROM film f
        JOIN film_actor fa ON f.film_id = fa.film_id
        JOIN actor a ON fa.actor_id = a.actor_id
        WHERE f.title 'LIKE' :title
        ORDER BY a.last_name, a.first_name

    """
    )

    df = pd.read_sql(sql_query, con=engine, params={"title": title})
    return df


def film_title_case_insensitive(words: list[str]) -> pd.DataFrame | None:
    """Funkcja zwracająca wynik zapytania do bazy o tytuły filmów zawierających
    conajmniej jedno z podanych słów z listy `words`, bez uwzględniania
    wielkości liter.

    Przykład wynikowej tabeli:
    |   |    title    |
    |---|-------------|
    |0  |Amadeus Holy |
    |1  |Holy Tadpole |

    Tabela wynikowa powinna być posortowana w kolejności:
        - tytuł filmu (alfabetycznie).

    Args:
        words (list[str]): Lista wyrażeń do wyszukania w tytułach filmów.

    Returns:
        pd.DataFrame: DataFrame zawierający wyniki zapytania.
        Jeżeli dane wejściowe są niepoprawne funkcja zwraca `None`.

    """
    pass

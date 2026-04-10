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

db_url = URL.create(
    drivername="postgresql+psycopg2",
    username="wbauer_adb",
    password="adb2020",
    host="pgsql-196447.vipserv.org",
    port=5432,
    database="wbauer_adb_2023",
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
    pass


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
    pass


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

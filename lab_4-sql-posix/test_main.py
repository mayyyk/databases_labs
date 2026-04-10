import pickle
from typing import Any, List

import main
import pandas as pd
import pytest

try:
    with open("expected", "rb") as f:
        expected = pickle.load(f)
except FileNotFoundError:
    print(
        "Error: The 'expected' file was not found. Please ensure it is in the correct directory."
    )
    expected = {
        "film_in_category": [],
        "film_cast": [],
        "film_title_case_insensitive": [],
    }


# --- Przygotowanie danych ---

valid_film_in_category = [
    (cat, cs, res)
    for cat, cs, res in expected["film_in_category"]
    if res is not None
]
invalid_film_in_category = [
    (cat, cs, res)
    for cat, cs, res in expected["film_in_category"]
    if res is None
]

valid_film_cast = [
    (title, res) for title, res in expected["film_cast"] if res is not None
]
invalid_film_cast = [
    (title, res) for title, res in expected["film_cast"] if res is None
]

valid_film_title_case_insensitive = [
    (words, res)
    for words, res in expected["film_title_case_insensitive"]
    if res is not None
]
invalid_film_title_case_insensitive = [
    (words, res)
    for words, res in expected["film_title_case_insensitive"]
    if res is None
]


# --- Testy dla film_in_category ---


@pytest.mark.parametrize(
    "category, case_sensitive, expected_result", invalid_film_in_category
)
def test_film_in_category_invalid_input(
    category: Any, case_sensitive: bool, expected_result: None
):
    """Testuje, czy film_in_category poprawnie obsługuje nieprawidłowe dane wejściowe, zwracając None."""
    actual = main.film_in_category(category, case_sensitive)
    assert actual is None, (
        f"Dla nieprawidłowego wejścia ({category}, {case_sensitive}), "
        f"oczekiwano None, ale otrzymano wynik."
    )


@pytest.mark.parametrize(
    "category, case_sensitive, expected_result", valid_film_in_category
)
def test_film_in_category_correct_solution(
    category: int | str, case_sensitive: bool, expected_result: pd.DataFrame
):
    """Testuje, czy film_in_category zwraca poprawny DataFrame dla prawidłowych danych wejściowych."""
    actual_result = main.film_in_category(category, case_sensitive)
    assert isinstance(actual_result, pd.DataFrame), (
        f"Dla prawidłowego wejścia ({category}, {case_sensitive}), "
        f"oczekiwano DataFrame, ale otrzymano {type(actual_result)}."
    )
    pd.testing.assert_frame_equal(actual_result, expected_result)


# --- Testy dla film_cast ---


@pytest.mark.parametrize("title, expected_result", invalid_film_cast)
def test_film_cast_invalid_input(title: Any, expected_result: None):
    """Testuje, czy film_cast poprawnie obsługuje nieprawidłowe dane wejściowe, zwracając None."""
    actual = main.film_cast(title)
    assert actual is None, (
        f"Dla nieprawidłowego wejścia ({title}), oczekiwano None, ale otrzymano wynik."
    )


@pytest.mark.parametrize("title, expected_result", valid_film_cast)
def test_film_cast_correct_solution(title: str, expected_result: pd.DataFrame):
    """Testuje, czy film_cast zwraca poprawną obsadę filmu dla prawidłowych danych wejściowych."""
    actual_result = main.film_cast(title)
    assert isinstance(actual_result, pd.DataFrame), (
        f"Dla prawidłowego wejścia ({title}), oczekiwano DataFrame, "
        f"ale otrzymano {type(actual_result)}."
    )
    pd.testing.assert_frame_equal(actual_result, expected_result)


# --- Testy dla film_title_case_insensitive ---


@pytest.mark.parametrize("words, expected_result", invalid_film_title_case_insensitive)
def test_film_title_case_insensitive_invalid_input(words: Any, expected_result: None):
    """Testuje, czy film_title_case_insensitive poprawnie obsługuje nieprawidłowe dane wejściowe, zwracając None."""
    actual = main.film_title_case_insensitive(words)
    assert actual is None, (
        f"Dla nieprawidłowego wejścia ({words}), oczekiwano None, ale otrzymano wynik."
    )


@pytest.mark.parametrize("words, expected_result", valid_film_title_case_insensitive)
def test_film_title_case_insensitive_correct_solution(
    words: List[str], expected_result: pd.DataFrame
):
    """Testuje, czy film_title_case_insensitive zwraca poprawne tytuły filmów dla prawidłowych danych wejściowych."""
    actual_result = main.film_title_case_insensitive(words)
    assert isinstance(actual_result, pd.DataFrame), (
        f"Dla prawidłowego wejścia ({words}), oczekiwano DataFrame, "
        f"ale otrzymano {type(actual_result)}."
    )
    pd.testing.assert_frame_equal(actual_result, expected_result)
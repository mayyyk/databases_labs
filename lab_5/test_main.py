import pickle
from typing import Any

import main
import pandas as pd
import pytest

try:
    with open("expected", "rb") as f:
        expected = pickle.load(f)
except FileNotFoundError:
    print("[ERROR] Missing 'expected' file.")
    expected = {
        "customers_by_last_name": [],
        "payments_above_amount": [],
        "active_customers_in_store": [],
        "unreturned_rentals": None,
        "customer_rentals_in_range": [],
    }


# --- Przygotowanie danych ---

valid_customers_by_last_name = [
    (ln, res) for ln, res in expected["customers_by_last_name"] if res is not None
]
invalid_customers_by_last_name = [
    (ln, res) for ln, res in expected["customers_by_last_name"] if res is None
]

valid_payments_above = [
    (amount, res) for amount, res in expected["payments_above_amount"] if res is not None
]
invalid_payments_above = [
    (amount, res) for amount, res in expected["payments_above_amount"] if res is None
]

valid_active_in_store = [
    (sid, res) for sid, res in expected["active_customers_in_store"] if res is not None
]
invalid_active_in_store = [
    (sid, res) for sid, res in expected["active_customers_in_store"] if res is None
]

valid_rentals_in_range = [
    (cid, sd, ed, res)
    for cid, sd, ed, res in expected["customer_rentals_in_range"]
    if res is not None
]
invalid_rentals_in_range = [
    (cid, sd, ed, res)
    for cid, sd, ed, res in expected["customer_rentals_in_range"]
    if res is None
]


# --- Testy dla customers_by_last_name ---


@pytest.mark.parametrize("last_name, expected_result", invalid_customers_by_last_name)
def test_customers_by_last_name_invalid_input(last_name: Any, expected_result: None):
    """Sprawdza poprawną obsługę nieprawidłowych danych przez customers_by_last_name."""
    actual = main.customers_by_last_name(last_name)
    assert actual is None, (
        f"Dla nieprawidłowego wejścia oczekiwano None, otrzymano: {actual}."
    )


@pytest.mark.parametrize("last_name, expected_result", valid_customers_by_last_name)
def test_customers_by_last_name_correct_solution(last_name: str, expected_result: pd.DataFrame):
    """Sprawdza poprawność wyników funkcji customers_by_last_name."""
    actual = main.customers_by_last_name(last_name)
    pd.testing.assert_frame_equal(actual, expected_result)


# --- Testy dla payments_above_amount ---


@pytest.mark.parametrize("amount, expected_result", invalid_payments_above)
def test_payments_above_amount_invalid_input(amount: Any, expected_result: None):
    """Sprawdza poprawną obsługę nieprawidłowych danych przez payments_above_amount."""
    actual = main.payments_above_amount(amount)
    assert actual is None, (
        f"Dla nieprawidłowego wejścia oczekiwano None, otrzymano: {actual}."
    )


@pytest.mark.parametrize("amount, expected_result", valid_payments_above)
def test_payments_above_amount_correct_solution(amount: float, expected_result: pd.DataFrame):
    """Sprawdza poprawność wyników funkcji payments_above_amount."""
    actual = main.payments_above_amount(amount)
    pd.testing.assert_frame_equal(actual, expected_result)


# --- Testy dla active_customers_in_store ---


@pytest.mark.parametrize("store_id, expected_result", invalid_active_in_store)
def test_active_customers_in_store_invalid_input(store_id: Any, expected_result: None):
    """Sprawdza poprawną obsługę nieprawidłowych danych przez active_customers_in_store."""
    actual = main.active_customers_in_store(store_id)
    assert actual is None, (
        f"Dla nieprawidłowego wejścia oczekiwano None, otrzymano: {actual}."
    )


@pytest.mark.parametrize("store_id, expected_result", valid_active_in_store)
def test_active_customers_in_store_correct_solution(
    store_id: int, expected_result: pd.DataFrame
):
    """Sprawdza poprawność wyników funkcji active_customers_in_store."""
    actual = main.active_customers_in_store(store_id)
    pd.testing.assert_frame_equal(actual, expected_result)


# --- Testy dla unreturned_rentals ---


def test_unreturned_rentals():
    """Sprawdza poprawność wyników funkcji unreturned_rentals."""
    actual = main.unreturned_rentals()
    pd.testing.assert_frame_equal(actual, expected["unreturned_rentals"])


# --- Testy dla customer_rentals_in_range ---


@pytest.mark.parametrize(
    "customer_id, start_date, end_date, expected_result", invalid_rentals_in_range
)
def test_customer_rentals_in_range_invalid_input(
    customer_id: Any, start_date: Any, end_date: Any, expected_result: None
):
    """Sprawdza poprawną obsługę nieprawidłowych danych przez customer_rentals_in_range."""
    actual = main.customer_rentals_in_range(customer_id, start_date, end_date)
    assert actual is None, (
        f"Dla nieprawidłowego wejścia oczekiwano None, otrzymano: {actual}."
    )


@pytest.mark.parametrize(
    "customer_id, start_date, end_date, expected_result", valid_rentals_in_range
)
def test_customer_rentals_in_range_correct_solution(
    customer_id: int, start_date: str, end_date: str, expected_result: pd.DataFrame
):
    """Sprawdza poprawność wyników funkcji customer_rentals_in_range."""
    actual = main.customer_rentals_in_range(customer_id, start_date, end_date)
    pd.testing.assert_frame_equal(actual, expected_result)

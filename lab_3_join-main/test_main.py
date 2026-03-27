# -*- coding: utf-8 -*-

import pytest
import main
import pickle
import math
import numpy as np
import pandas as pd

from typing import Union, List, Tuple

expected = pickle.load(open('expected','rb'))

result_film_in_category = expected['film_in_category']
result_client_from_city = expected['client_from_city']  
result_actor_in_film = expected['actor_in_film'] 
result_film_in_language = expected['film_in_language'] 



@pytest.mark.parametrize("category_id,result", result_film_in_category)
def test_film_in_category(category_id:int, result):
    if result is None:
        assert main.film_in_category(category_id) is None, 'Spodziewany wynik: {0}, aktualny {1}. Błedy wejścia.'.format(result, main.film_in_category(category_id))
    else:
        test =  main.film_in_category(category_id)
        pd.testing.assert_frame_equal(result,test), 'Spodziewany wynik: {0}, aktualny {1}. Błędy implementacji.'.format(result, main.film_in_category(category_id))

@pytest.mark.parametrize("title,result", result_actor_in_film)
def test_actor_in_film(title:str, result):
    if result is None:
        assert main.actor_in_film(title) is None, 'Spodziewany wynik: {0}, aktualny {1}. Błedy wejścia.'.format(result, main.actor_in_film(title))
    else:
        test =  main.actor_in_film(title)
        pd.testing.assert_frame_equal(result,test), 'Spodziewany wynik: {0}, aktualny {1}. Błędy implementacji.'.format(result, main.actor_in_film(title))

@pytest.mark.parametrize("language,result", result_film_in_language)
def test_film_in_language(language:str, result):
    if result is None:
        assert main.film_in_language(language) is None, 'Spodziewany wynik: {0}, aktualny {1}. Błedy wejścia.'.format(result, main.film_in_language(language))
    else:
        test =  main.film_in_language(language)
        pd.testing.assert_frame_equal(result,test), 'Spodziewany wynik: {0}, aktualny {1}. Błędy implementacji.'.format(result, main.film_in_language(language))

@pytest.mark.parametrize("city,result", result_client_from_city)
def test_client_from_city(city:str, result):
    if result is None:
        assert main.client_from_city(city) is None, 'Spodziewany wynik: {0}, aktualny {1}. Błedy wejścia.'.format(result, main.client_from_city(city))
    else:
        test =  main.client_from_city(city)
        pd.testing.assert_frame_equal(result,test), 'Spodziewany wynik: {0}, aktualny {1}. Błędy implementacji.'.format(result, main.client_from_city(city))
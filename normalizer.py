"""
first_name, last_name, middle_name, birth_date, birth_month, birth_year

Vera -> ВЕРА
вера -> ВЕРА
Саня -> АЛЕКСАНДР

Если есть фамилия, то ее желательно также получить

Cпарсить сайт https://proizvodnye.ru/?ysclid=l5299y8ock429824501
"""
import pandas as pd
import numpy as np
import sys
import logging
import pymorphy2
from transliterate import translit
import click
from normalize_params import NormalizeParams, read_normalize_params


logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def read_dataset(file_path):
    """Функция чтения датасета"""
    logger.info(f'Чтение датасета {file_path}')
    return pd.read_excel(file_path)


def check_having_digits(string):
    """Функция проверки на наличие цифр в строке"""
    return any(map(str.isdigit, string))


def translate_string(string):
    """Функция перевода строки на русский язык"""
    return translit(string, language_code='ru')


def to_official_style(name, name_dict):
    """Фукнция преобразования имени к официальному стилю"""
    up_name = name.upper()
    if up_name in name_dict.keys():
        return name_dict[up_name]
    else:
        return up_name


def filter_name_only(name_splitted, morph, name_dict):
    """Функция для фильтрации датасета"""
    """Фильтруем, оставляя только строки без цифр"""
    if not check_having_digits(name_splitted):
        """Переводим на русский язык"""
        translated_name = translate_string(name_splitted)

        """Фильтруем от мусора, оставляя только имена"""
        for p in morph.parse(translated_name):
            if 'Name' in p.tag:
                """Переводим к официальной форме имени"""
                return to_official_style(translated_name, name_dict)

    return np.NaN


def normalize(dataset: pd.DataFrame, column_name):
    """Функция нормализации датасета"""

    logger.info(f'Удаляем строки без имени')
    dataset = dataset[dataset[column_name].notna()].copy()
    dataset.reset_index(drop=True, inplace=True)

    morph = pymorphy2.MorphAnalyzer()

    logger.info(f'Объявляем словарь для замены разговорной формы имени на официальное')
    short_name = ["САША", "САНЯ", "САНЕК"]
    name_dict = {name: "АЛЕКСАНДР" for name in short_name}
    name_dict["РОМА"] = "РОМАН"

    logger.info(f'Запуск процесса нормализации')
    for i, name in enumerate(dataset[column_name]):
        """Выбираем только строки"""
        if isinstance(name, str):
            """Выбираем только имена"""
            name_splitted = name.split()[0]
            """Выбираем имена и фамилии"""
            first_second_name = name.split()
            if len(first_second_name) == 2:
                """Фильтруем имя"""
                clear_name = filter_name_only(first_second_name[0], morph, name_dict)
                if isinstance(clear_name, str):
                    """Фильтруем фамилию"""
                    clear_surname = filter_name_only(first_second_name[1], morph, name_dict)
                    if isinstance(clear_surname, str):
                        if len(clear_surname) > 1:
                            name_and_surname = clear_name + " " + clear_surname
                        else:
                            name_and_surname = clear_name
                    else:
                        name_and_surname = clear_name
                else:
                    name_and_surname = np.NaN
                dataset[column_name].iloc[i] = name_and_surname

            elif len(first_second_name) == 1:
                """Фильтруем имя"""
                dataset[column_name].iloc[i] = filter_name_only(name_splitted, morph, name_dict)

        else:
            dataset[column_name].iloc[i] = np.NaN

    logger.info(f'Удаляем ненужные строки')
    dataset = dataset[dataset[column_name].notna()].copy()
    dataset.reset_index(drop=True, inplace=True)
    return dataset


def run_normalize(config_path: str, print_result: bool = False):
    """Главная функция, запускающая весь процесс предсказания"""
    normalize_params: NormalizeParams = read_normalize_params(config_path)
    logger.info('Запуск нормализации данных')
    dataset = read_dataset(normalize_params.input_data_path)
    result = normalize(dataset, normalize_params.column_name)
    logger.info('Нормализация данных закончена')
    logger.info('Запись результата в файл')
    pd.DataFrame(result, index=result.index).to_excel(normalize_params.result_path)
    if print_result:
        print(result)
        for i, name in enumerate(result[normalize_params.column_name]):
            print(i, name)


@click.command(name='run_predict')
@click.argument('config_path')
def run_normalize_command(config_path: str = "normalizerConfig.yaml"):
    """функция для запуска процесса предсказания"""
    run_normalize(config_path)


if __name__ == '__main__':
    run_normalize_command()

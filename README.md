# name_surname_normalizer
Script for normalization of first and last name

Запуск скрипта:
~~~
python normalizer.py normalizerConfig.yaml
~~~ 

input_data_path: "first_task_aton.xlsx" - путь до сырых данных
column_name: "name" - название столбца, который нужно нормализовать
result_path: "Normalized_Data.xlsx" - путь до нормализованных данных

Vera -> ВЕРА
вера -> ВЕРА
Саня -> АЛЕКСАНДР

Если есть фамилия, то ее желательно также получить

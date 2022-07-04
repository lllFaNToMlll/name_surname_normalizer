from dataclasses import dataclass
from marshmallow_dataclass import class_schema
import yaml


@dataclass()
class NormalizeParams:
    """Датакласс параметров для чтения конфига"""
    input_data_path: str
    column_name: str
    result_path: str


NormalizeParamsSchema = class_schema(NormalizeParams)


def read_normalize_params(path: str):
    """Функция для чтения параметров"""
    with open(path, 'r', encoding='utf-8') as input_stream:
        schema = NormalizeParamsSchema()
        return schema.load(yaml.safe_load(input_stream))
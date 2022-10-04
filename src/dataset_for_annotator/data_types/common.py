import datetime
from typing import Any, Callable
from enum import Enum, unique

JSON_ELM = list | dict | int | str | None

# データセットで使うタイムスタンプは, 日本時間で統一
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

def date_handler(obj: Any) -> Any:
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

@unique
class MissingValue(str, Enum):
    """欠損値を扱うやつ"""

    Unacquired = "unacquired"
    """未取得: これから取得を試みる場合"""

    Failed = "failed"
    """取得失敗: 取得を試みたが, なんらかの理由でエラーになった場合"""

    NotFound = "not_found"
    """見つからない: 現状見つかっていないが, 存在しない確証もない場合"""

    NotExist = "not_exist"
    """存在しない: 取得を試みた結果, 存在しないことが分かった場合"""

    @classmethod
    def has_value(cls, value) -> bool:
        if isinstance(value, str):
            return value in cls._value2member_map_
        else:
            return False

def json_to_missing_value_or_any(
    json_elm: JSON_ELM, constructor: Callable[[JSON_ELM], Any] = lambda x: x
) -> Any | MissingValue:
    if MissingValue.has_value(json_elm):
        return MissingValue(json_elm)
    else:
        return constructor(json_elm)


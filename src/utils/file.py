from ast import Call
from typing import Any, Callable
import json
import os

PathLike = str | bytes | os.PathLike

def load_json(json_path: PathLike) -> Any:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(json_path: PathLike, save_obj: Any, date_handler: Callable[[Any], Any] | None = None) -> None:
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(
            save_obj, f, ensure_ascii=False, indent=4, separators=(',', ': '),
            default=date_handler
        )

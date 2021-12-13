import csv
import json
from collections import OrderedDict
from itertools import filterfalse
from typing import List, Tuple, Any

all_fieldnames: list = []


def add_key(k: str):
    if k not in all_fieldnames:
        all_fieldnames.append(k)


def stringify_null(v: str):
    return v if v is not None else "null"


def flatten(data: Any, cur: str, is_root: bool) -> List[List[Tuple[str, Any]]]:
    if isinstance(data, dict):
        return [flatten_dict(data, cur)]
    elif isinstance(data, list):
        if is_root:
            return flatten_list(data, cur)
        else:
            return flatten_list(data, cur + "[]")
    else:
        add_key(cur)
        return [[(cur, stringify_null(data))]]


def flatten_dict(d: dict, cur: str) -> List[Tuple[str, Any]]:
    root: List[Tuple[str, Any]] = []
    sub: List[Tuple[str, Any]] = []
    for k in d:
        v = d[k]
        if cur == "":
            now = k
        else:
            now = f"{cur}.{k}"
        if isinstance(v, dict):
            sub += flatten_dict(v, now)
        elif isinstance(v, list):
            if len(v) == 0:
                add_key(now)
                root.append((now, "[]"))
            sub += flatten_list(v, now)
        else:
            add_key(now)
            root.append((now, stringify_null(v)))
    return root + sub


def flatten_list(l: list, cur: str) -> List[List[Tuple[str, Any]]]:
    return sum([flatten(v, cur, False) for v in l], [])


def is_list(field):
    return isinstance(field, list)


def writerow(writer, row):
    d = OrderedDict.fromkeys(all_fieldnames)
    non_list_fields = list(filterfalse(is_list, row))
    list_fields = list(filter(is_list, row))

    for field in non_list_fields:
        k, v = field
        d[k] = v
    if len(non_list_fields) != 0:
        writer.writerow(d)
    for field in list_fields:
        if isinstance(field, list):
            writerow(writer, field)


if __name__ == "__main__":
    with open('aa.csv', 'w', newline='', encoding="utf-8") as csv_file:
        j = json.loads(open("simple.json", "r", encoding="utf-8").read(), object_pairs_hook=OrderedDict)
        f = flatten(j, "", True)
        writer = csv.DictWriter(csv_file, fieldnames=all_fieldnames)
        writer.writeheader()
        for row in f:
            writerow(writer, row)

#!/usr/bin/python
from brownie import chain
import json
import os
from pathlib import Path
import time
from typing import Union

from dotenv import load_dotenv

load_dotenv()

OVERWRITE_LATEST = True
INPUT_DIR = Path("./scripts/inputs")
OUTPUT_DIR = Path("./scripts/outputs")


class JSONDict(dict):
    def read_addr(self, key):
        return self[key]


def _now() -> int:
    return int(time.time())


def _load_json(fp: Path) -> JSONDict:
    with open(fp, "r") as json_f:
        return JSONDict(json.load(json_f))


def load_inputs(name: str) -> JSONDict:
    fp = INPUT_DIR / str(chain.id) / f"{name}.json"
    return _load_json(fp)


def load_outputs(name: str) -> JSONDict:
    fp = OUTPUT_DIR / str(chain.id) / f"{name}-latest.json"
    return _load_json(fp)


def _update_key(fp: Path, key: str, value: Union[str, int, float]):
    data = {}
    if fp.exists():
        with open(fp, "r") as json_f:
            data = json.load(json_f)
    data[key] = value
    with open(fp, "w") as json_f:
        json.dump(data, json_f, indent=2)


def write_contract(name: str, key: str, addr: str):
    out_dir = OUTPUT_DIR / str(chain.id)
    os.makedirs(out_dir, exist_ok=True)

    # update timestamp versioned file
    fp = out_dir / f"{name}-{_now()}.json"
    _update_key(fp, key, addr)

    # update latest file
    if OVERWRITE_LATEST:
        latest_fp = out_dir / f"{name}-latest.json"
        _update_key(latest_fp, key, addr)

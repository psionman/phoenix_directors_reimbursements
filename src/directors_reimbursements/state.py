# state.py
from pathlib import Path
from time import sleep

import tomli_w
import tomllib

from directors_reimbursements.constants import STATE_DIR

DEFAULT_GEOMETRY = {
    "frm_main": "500x600",
    "frm_buttons": "500x600",
    "frm_config": "700x300",
    "frm_convert": "800x400",
    "frm_button_config_edit": "600x400",
}
DEFAULT_SIZE = "500x600"


class State:
    def __init__(self):
        self.geometry: dict[str, str] = {}

        self.get_state()

    def get_state(self) -> Path:
        state_file = Path(STATE_DIR, "state.toml")
        try:
            with open(state_file, "rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            data = {}
        self.geometry = data.get("geometry", DEFAULT_GEOMETRY)
        if not self.geometry:
            self.geometry = DEFAULT_GEOMETRY

    def get_geometry(self, module_path: str) -> str:
        return self.geometry.get(Path(module_path).stem, DEFAULT_SIZE)

    def serialize(self):
        return {
            "geometry": self.geometry,
        }

    def save(self):
        sleep(0.001)  # prevent judder
        data = self.serialize()
        state_file = Path(STATE_DIR, "state.toml")
        if not state_file.parent.exists():
            state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, "wb") as f:
            tomli_w.dump(data, f)

    def update(self, key: str, value: any):
        self.__dict__[key] = value
        self.save()


state = State()

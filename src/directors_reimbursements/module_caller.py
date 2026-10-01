# module_caller.py
"""Module caller for directors_reimbursements."""

from psiutils.module_caller import ModuleCaller as ModuleCallerBase

from directors_reimbursements.forms.frm_config import ConfigFrame


class ModuleCaller(ModuleCallerBase):
    def __init__(self, root, parsed_args: dict) -> None:
        self.modules = {
            "config": (self._config, None),
        }
        super().__init__(root, parsed_args)

    def _config(self) -> None:
        print("Calling... config")
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

from directors_reimbursements.forms.frm_config import ConfigFrame


class ModuleCaller():
    """Call a module  from command line."""
    def __init__(self, root, module) -> None:
        modules = {
            'config': self._config,
            }

        self.invalid = False
        if module == '-h':
            for key in sorted(list(modules.keys())+['main']):
                print(key)
            self.invalid = True
            return

        if module not in modules:
            if module != 'main':
                print(f'Invalid function name: {module}')
            self.invalid = True
            return

        self.root = root.root
        modules[module]()
        self.root.destroy()
        return

    def _config(self) -> None:
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

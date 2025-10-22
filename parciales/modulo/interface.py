import threading

class Interface:
    def __init__(self, core):
        self.core = core
        self._input = None
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while True:
            cmd = input("🧠 > ")
            self._input = cmd

    def has_input(self):
        return self._input is not None

    def get_input(self):
        cmd = self._input
        self._input = None
        return cmd

    def execute_command(self, cmd):
        self.core.logger.log(f"Ejecutando comando manual: {cmd}")

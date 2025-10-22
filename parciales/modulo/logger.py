import datetime, json, os

class Logger:
    def __init__(self, file="knowledge.json", max_logs=5000):
        self.file = file
        self.max_logs = max_logs
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("[Logger] ⚠️ Archivo knowledge.json dañado, reiniciando.")
        return {"logs": []}

    def log(self, msg):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"time": timestamp, "message": msg}
        print(f"[{timestamp}] {msg}")
        self.data["logs"].append(entry)

        # Evitar crecimiento infinito
        if len(self.data["logs"]) > self.max_logs:
            self.data["logs"] = self.data["logs"][-self.max_logs:]

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

import json
from django.contrib.auth.hashers import make_password


def main():
    with open(
        "/home/mugisa/Desktop/Tradeoasis/auth_app/fixtures/supplier.json"
    ) as file:
        data = json.load(file)

        for (idx, record) in enumerate(data):
            record["fields"]["password"] = make_password(
                record.get("fields").get("password")
            )
            record["fields"]["account_type"] = "SUPPLIER"
            data[idx] = record

        with open(
            "/home/mugisa/Desktop/Tradeoasis/auth_app/fixtures/supplier_.json", "w"
        ) as write_file:
            json.dump(data, write_file, indent=4, sort_keys=True)

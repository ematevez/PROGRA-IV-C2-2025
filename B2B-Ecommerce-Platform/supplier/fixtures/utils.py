import json
from django.conf import settings
from django.utils.text import slugify
import os


def main():
    with open(
        os.path.join(settings.BASE_DIR, "supplier/fixtures/supplier_fixtures.json")
    ) as file:
        data = json.load(file)

        for (idx, record) in enumerate(data):
            record["fields"]["slug"] = slugify(record.get("fields").get("name"))
            data[idx] = record

        with open(
            os.path.join(settings.BASE_DIR, "supplier/fixtures/supplier_fixtures.json"),
            "w",
        ) as write_file:
            json.dump(data, write_file, indent=4, sort_keys=True)

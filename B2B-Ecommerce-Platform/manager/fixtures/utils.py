import json
from django.conf import settings
from django.utils.text import slugify
import os
import uuid


def main():
    with open(
        os.path.join(settings.BASE_DIR, "manager/fixtures/manager_fixtures.json")
    ) as file:
        data = json.load(file)

        for (idx, record) in enumerate(data):
            record["fields"][
                "slug"
            ] = f'{slugify(record.get("fields").get("name"))}-{uuid.uuid4()}'[:50]
            data[idx] = record

        with open(
            os.path.join(settings.BASE_DIR, "manager/fixtures/manager_fixtures.json"),
            "w",
        ) as write_file:
            json.dump(data, write_file, indent=4, sort_keys=True)

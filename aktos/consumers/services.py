import csv
import io

import pyap
from django.db import transaction

from aktos.consumers.models import Consumer
from aktos.consumers.models import ConsumerAddress


@transaction.atomic
def consumers_ingest_csv_data(*, file: io.StringIO | io.TextIOWrapper):
    reader = csv.DictReader(file)
    row: dict
    for row in reader:
        parsed_address = pyap.parse(row["consumer address"], country="US")
        if parsed_address:
            parsed_address = parsed_address[0]

            consumer, created = Consumer.objects.update_or_create(
                ref_id=row.get("client reference no"),
                name=row.get("consumer name", ""),
                defaults={
                    "ssn": row.get("ssn"),
                    "status": row.get("status"),
                    "balance": float(row.get("balance")),
                },
            )
            if created:
                consumer.address = ConsumerAddress.objects.create(
                    address1=parsed_address.full_street,
                    city=parsed_address.city,
                    state=parsed_address.region1,
                    zip_code=parsed_address.postal_code,
                )
                consumer.save(update_fields=["address"])

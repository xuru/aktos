import io
from pathlib import Path

from django.core.management import BaseCommand

from aktos.consumers.services import consumers_ingest_csv_data


class Command(BaseCommand):
    help = "Injest a number of CSV files with consumer data"

    def add_arguments(self, parser):
        parser.add_argument("files", default=[], nargs="*", type=str)

    def handle(self, *args, **options):
        for filename in options["files"]:
            with Path(filename).open() as fp:
                consumers_ingest_csv_data(file=io.StringIO(fp.read()))

from django.core.management import BaseCommand

from wedge.common.fixtures import update_all_fixtures


class Command(BaseCommand):
    help = "Setup or ensure default fixtures in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Just show what migrations would be made; don't actually write them.",
        )

    def handle(self, *args, **options):
        update_all_fixtures(verbosity=options["verbosity"], dry_run=options["dry_run"])

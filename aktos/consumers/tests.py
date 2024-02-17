# Create your tests here.
import io
from unittest import TestCase

from aktos.consumers.models import Consumer
from aktos.consumers.selectors import consumers_get_consumers
from aktos.consumers.services import consumers_ingest_csv_data


class ConsumerTests(TestCase):
    def setUp(self):
        pass

    def test_consumers_ingest_csv_data(self):
        csv_data = "\n".join([
            'client reference no,balance,status,consumer name,consumer,address,ssn',
            'e69121a2-30a8-4962-b0f7-f76a5df3cb3d,79220.46,IN_COLLECTION,Dominique Santiago,"237 Andrews Meadows Apt. 439 South Madisonland, CA 20704",316-45-1317',
            'ca0766c5-e94c-4687-a0e7-4ad23084250a,22985.96,INACTIVE,Mark Henson,"780 Sean Brook North Christophershire, AR 30586",031-62-9960',
        ])

        Consumer.objects.all().delete()
        consumers_ingest_csv_data(file=io.StringIO(csv_data))
        consumers = consumers_get_consumers()
        assert consumers.count() == 2
        for consumer in consumers:
            assert consumer.ref_id in ["e69121a2-30a8-4962-b0f7-f76a5df3cb3d", "ca0766c5-e94c-4687-a0e7-4ad23084250a"]



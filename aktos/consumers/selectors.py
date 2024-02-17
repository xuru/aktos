from django.db.models import QuerySet

from aktos.consumers.filters import ConsumerFilter
from aktos.consumers.models import Consumer


def consumers_get_consumers(*, filters: dict = None) -> QuerySet:
    filters = filters or {}

    qs = Consumer.objects.all()

    # special case... big assumption that we are only dealing with first/last
    if filters.get("consumer_name"):
        for word in filters["consumer_name"].split():
            qs = qs.filter(name__icontains=word)

    if filters:
        qs = ConsumerFilter(data=filters, queryset=qs).qs

    return qs

from django_filters import rest_framework as filters

from aktos.consumers import models


class ConsumerFilter(filters.FilterSet):
    min_balance = filters.NumberFilter(field_name="balance", lookup_expr="gte")
    max_balance = filters.NumberFilter(field_name="balance", lookup_expr="lte")
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = models.Consumer
        fields = ["balance", "status", "name"]

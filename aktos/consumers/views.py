from io import TextIOWrapper

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import inline_serializer
from rest_framework import parsers
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aktos.common.pagination import PageNumberPagination
from aktos.common.pagination import get_paginated_response
from aktos.consumers.selectors import consumers_get_consumers
from aktos.consumers.services import consumers_ingest_csv_data


class ConsumerListApi(APIView):
    """
    List all consumers belonging to the same collection agency and same client
    """

    permission_classes = [IsAuthenticated]

    class FilterSerializer(serializers.Serializer):
        min_balance = serializers.IntegerField(required=False)
        max_balance = serializers.IntegerField(required=False)
        consumer_name = serializers.CharField(required=False)
        status = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        address = inline_serializer(
            "AddressSerializer",
            fields={
                "address1": serializers.CharField(),
                "address2": serializers.CharField(),
                "city": serializers.CharField(),
                "state": serializers.CharField(),
                "zip_code": serializers.CharField(),
            },
        )
        ref_id = serializers.UUIDField()
        ssn = serializers.CharField()
        name = serializers.CharField()
        status = serializers.CharField()
        balance = serializers.DecimalField(max_digits=18, decimal_places=2)

    @extend_schema(
        summary="List of consumers",
        description="List of consumers in the system.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="min_balance",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Minimum balance",
            ),
            OpenApiParameter(
                name="max_balance",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Maximum balance",
            ),
            OpenApiParameter(
                name="consumer_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Name of the consumer",
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Status of the consumer",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of items returned per page",
            ),
        ],
        responses=OutputSerializer,
    )
    def get(self, request: Request):
        # Using a serializer ensures we won't get a query param injection attack
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        params = filters_serializer.validated_data
        # TODO: assert min_balance <= max_balance

        qs = consumers_get_consumers(filters=params)

        return get_paginated_response(
            pagination_class=PageNumberPagination,
            serializer_class=self.OutputSerializer,
            queryset=qs,
            request=request,
            view=self,
        )


class ConsumerUploadApi(APIView):
    """
    Upload consumers belonging to the same collection agency and same client
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser]

    class CunsumersUploadSerializer(serializers.Serializer):
        """
        A Serializer for uploading a csv of consumers
        """

        content = serializers.FileField(
            help_text="A CSV file to upload.",
            required=True,
            write_only=True,
        )

    @extend_schema(
        summary="Upload consumers",
        description="Ingest consumers into the system.",
        request=inline_serializer(
            name="InlineFormSerializer",
            fields={
                "file": serializers.FileField(),
            },
        ),
        responses=None,
    )
    def post(self, request: Request):
        # Using a serializer ensures we won't get a query param injection attack

        if "file" not in request.FILES:
            raise serializers.ValidationError("No file provided")  # noqa

        file = TextIOWrapper(request.FILES["file"].file, encoding=request.encoding)
        consumers_ingest_csv_data(file=file)

        return Response(status=status.HTTP_201_CREATED)

from drf_spectacular import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter


class OpenAPISerializer(serializers.Serializer):
    @classmethod
    def as_openapi_params(cls) -> list[OpenApiParameter]:
        # FIXME: See openforms.validators.api.serializers.ValidatorsFilterSerializer
        instance = cls()
        ct_field = instance.fields["component_type"]
        return [
            OpenApiParameter(
                ct_field.field_name,
                OpenApiTypes.STR,
                description=str(ct_field.help_text),
            ),
        ]

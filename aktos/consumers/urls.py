from django.urls import path

from aktos.consumers.views import ConsumerListApi
from aktos.consumers.views import ConsumerUploadApi

urlpatterns = [
    path("", ConsumerListApi.as_view(), name="list"),
    path("upload", ConsumerUploadApi.as_view(), name="upload"),
]

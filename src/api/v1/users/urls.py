from django.urls import path

from api.v1.users.views import RegisrtyView


urlpatterns = [
    path("registry/",  RegisrtyView.as_view(), name="registry")
]

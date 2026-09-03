from django.urls import path

from . import views

app_name = "editions"

urlpatterns = [
    path("", views.edition_catalog, name="catalog"),
    path(
        "<slug:collection_slug>/<slug:photograph_slug>/",
        views.photograph_detail,
        name="photograph_detail",
    ),
]

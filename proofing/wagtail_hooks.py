from django.urls import path, reverse

from wagtail import hooks
from wagtail.admin.auth import require_admin_access
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem

from proofing.admin_views import proofing_dashboard


@hooks.register("register_admin_urls")
def register_proofing_admin_urls():
    return [
        path("proofing/", require_admin_access(proofing_dashboard), name="proofing_dashboard"),
    ]


@hooks.register("register_admin_menu_item")
def register_proofing_menu_item():
    proofing_menu = Menu(
        items=[
            MenuItem(
                "Proofing Galleries",
                reverse("proofing_dashboard"),
                icon_name="folder-open-inverse",
                order=10,
            ),
            MenuItem(
                "Clients",
                reverse("wagtailsnippets_proofing_client:list"),
                icon_name="user",
                order=20,
            ),
        ]
    )

    return SubmenuMenuItem(
        "Proofing",
        proofing_menu,
        name="proofing",
        icon_name="folder-open-1",
        order=350,
    )

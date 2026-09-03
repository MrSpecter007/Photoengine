"""Wagtail admin hooks for the Photoengine showroom."""

from django.template.loader import render_to_string

from wagtail import hooks
from wagtail.admin.ui.components import Component

from home.models import AdminExperienceSettings


def get_admin_experience():
    try:
        return AdminExperienceSettings.load()
    except Exception:
        return AdminExperienceSettings()


class AdminExperienceWelcomePanel(Component):
    name = "admin_experience_welcome"
    order = 40
    template_name = "home/wagtailadmin/admin_experience_welcome_panel.html"

    def get_context_data(self, parent_context=None):
        return {
            "admin_experience": get_admin_experience(),
        }


@hooks.register("insert_global_admin_css")
def admin_experience_css():
    return render_to_string(
        "home/wagtailadmin/admin_experience_css.html",
        {"admin_experience": get_admin_experience()},
    )


@hooks.register("insert_global_admin_js")
def admin_experience_js():
    return render_to_string(
        "home/wagtailadmin/admin_experience_js.html",
        {"admin_experience": get_admin_experience()},
    )


@hooks.register("construct_homepage_panels")
def add_admin_experience_welcome_panel(request, panels):
    panels.insert(0, AdminExperienceWelcomePanel())


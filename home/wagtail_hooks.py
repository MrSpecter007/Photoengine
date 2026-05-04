from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from wagtail import hooks
from wagtail.admin.ui.components import Component

from home.models import AdminExperienceSettings


def get_admin_experience_settings():
    return AdminExperienceSettings.load()


def render_admin_experience_css():
    return render_to_string(
        "home/wagtailadmin/admin_experience_css.html",
        {"admin_experience": get_admin_experience_settings()},
    )


def render_admin_experience_js():
    return render_to_string(
        "home/wagtailadmin/admin_experience_js.html",
        {"admin_experience": get_admin_experience_settings()},
    )


class AdminExperienceWelcomePanel(Component):
    order = 10

    def render_html(self, parent_context):
        return render_to_string(
            "home/wagtailadmin/admin_experience_welcome_panel.html",
            {"admin_experience": get_admin_experience_settings()},
        )


@hooks.register("insert_global_admin_css")
def insert_global_admin_css():
    return mark_safe(render_admin_experience_css())


@hooks.register("insert_global_admin_js")
def insert_global_admin_js():
    return mark_safe(render_admin_experience_js())


@hooks.register("construct_homepage_panels")
def add_admin_experience_panel(request, panels):
    panels.insert(0, AdminExperienceWelcomePanel())

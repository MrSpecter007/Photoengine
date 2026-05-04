from django import template
from django.db import IntegrityError
from wagtail.images.models import Filter

register = template.Library()


@register.simple_tag
def safe_rendition(image, spec):
    if not image:
        return None

    try:
        return image.get_rendition(spec)
    except IntegrityError:
        filter_obj = Filter(spec=spec)
        rendition_model = image.get_rendition_model()
        return rendition_model.objects.get(
            image=image,
            filter_spec=spec,
            focal_point_key=filter_obj.get_cache_key(image),
        )

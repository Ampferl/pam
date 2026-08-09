from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def nav_active(context, ns_view, active_class="active"):
    request = context.get("request")
    rm = getattr(request, "resolver_match", None)
    if not rm:
        return ""
    if ns_view.endswith('*'):
        return active_class if rm.view_name.startswith(ns_view[:-1]) else ""

    return active_class if rm.view_name == ns_view else ""


from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary in templates."""
    try:
        return dictionary.get(key) if isinstance(dictionary, dict) else None
    except:
        return None

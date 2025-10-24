from django import template

register = template.Library()

@register.filter
def star_types(rating, max_stars=5):
    """
    Return list berisi 'full', 'half', atau 'empty' sesuai rating.
    Contoh: rating=4.8 -> ['full','full','full','full','half']
    """
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        rating = 0

    stars = []
    for i in range(1, max_stars + 1):
        if rating >= i:
            stars.append("full")
        elif rating >= i - 0.5:
            stars.append("half")
        else:
            stars.append("empty")
    return stars

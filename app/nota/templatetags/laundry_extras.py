from django import template

register = template.Library()


@register.filter
def rupiah(value):
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        return "Rp 0"
    return f"Rp {number:,}".replace(",", ".")


@register.filter
def kg(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "0 kg"
    formatted = f"{number:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    return f"{formatted} kg"

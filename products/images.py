from pathlib import Path

from django.conf import settings

EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


def media_url(folder, name):
    name = (name or "").strip()
    if not name:
        return ""
    base = Path(settings.MEDIA_ROOT) / folder
    candidates = [name] + [f"{Path(name).stem}.{ext}" for ext in EXTENSIONS]
    for candidate in dict.fromkeys(candidates):
        if (base / candidate).is_file():
            return f"{settings.MEDIA_URL}{folder}/{candidate}"
    return ""

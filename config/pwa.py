from pathlib import Path

from django.conf import settings
from django.http import FileResponse


def service_worker(request):
    path = Path(settings.BASE_DIR) / "static" / "pwa" / "service-worker.js"
    response = FileResponse(path.open("rb"), content_type="application/javascript; charset=utf-8")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

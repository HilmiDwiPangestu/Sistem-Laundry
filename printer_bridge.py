"""Local Windows ESC/POS bridge for Sani Laundry.

Binds only to 127.0.0.1. Requests that list or print require the random token
shown in this process console. This service intentionally does not expose the
printer over the LAN.
"""
from __future__ import annotations

import base64
import json
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 17891
BASE_DIR = Path(__file__).resolve().parent
TOKEN_FILE = BASE_DIR / ".printer_bridge_token"
MAX_BODY_BYTES = 2 * 1024 * 1024

try:
    import win32print  # type: ignore
except ImportError:
    win32print = None


def get_token() -> str:
    try:
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    except OSError:
        pass
    token = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(token, encoding="utf-8")
    try:
        TOKEN_FILE.chmod(0o600)
    except OSError:
        pass
    return token


TOKEN = get_token()


def list_printers() -> tuple[list[dict[str, object]], str | None]:
    """Return installed Windows printers across pywin32 return formats.

    EnumPrinters(..., level=2) commonly returns dictionaries (PRINTER_INFO_2),
    not tuples. Older pywin32 examples and some environments use tuple records;
    support both so the printer list does not fail with KeyError: 2.
    """
    if win32print is None:
        raise RuntimeError("Modul pywin32 belum terpasang. Jalankan: venv\\Scripts\\python.exe -m pip install pywin32")

    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    records = win32print.EnumPrinters(flags, None, 2)
    found_names: set[str] = set()
    for record in records or []:
        name = None
        if isinstance(record, dict):
            name = (
                record.get("pPrinterName")
                or record.get("PrinterName")
                or record.get("printer_name")
                or record.get("name")
            )
        elif isinstance(record, (tuple, list)):
            # PRINTER_INFO_1 tuple layouts place the printer name at index 2.
            if len(record) > 2:
                name = record[2]
            elif record:
                name = record[0]
        if name:
            found_names.add(str(name).strip())

    try:
        default_name = win32print.GetDefaultPrinter()
    except Exception:
        default_name = None

    names = sorted(name for name in found_names if name)
    printers = [{"name": name, "is_default": name == default_name} for name in names]
    return printers, default_name


def send_raw(printer_name: str, payload: bytes) -> None:
    if win32print is None:
        raise RuntimeError("Modul pywin32 belum terpasang. Jalankan: python -m pip install pywin32")
    printers, _ = list_printers()
    known_names = {str(item["name"]) for item in printers}
    if printer_name not in known_names:
        raise ValueError("Printer tidak ditemukan di Windows. Periksa nama printer atau instal drivernya.")

    handle = win32print.OpenPrinter(printer_name)
    document_started = False
    page_started = False
    try:
        win32print.StartDocPrinter(handle, 1, ("Sani Laundry ESC/POS", None, "RAW"))
        document_started = True
        win32print.StartPagePrinter(handle)
        page_started = True
        win32print.WritePrinter(handle, payload)
        win32print.EndPagePrinter(handle)
        page_started = False
        win32print.EndDocPrinter(handle)
        document_started = False
    finally:
        if page_started:
            try:
                win32print.EndPagePrinter(handle)
            except Exception:
                pass
        if document_started:
            try:
                win32print.EndDocPrinter(handle)
            except Exception:
                pass
        win32print.ClosePrinter(handle)


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "SaniLaundryPrinterBridge/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep useful request logs in the console without exposing request bodies.
        print("[printer-bridge] " + (fmt % args))

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Printer-Token")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()
        self.wfile.write(body)

    def _host_is_local(self) -> bool:
        host = (self.headers.get("Host") or "").split(":", 1)[0].strip("[]").lower()
        return host in {"127.0.0.1", "localhost"}

    def _authorized(self) -> bool:
        supplied = self.headers.get("X-Printer-Token", "")
        return bool(supplied) and secrets.compare_digest(supplied, TOKEN)

    def do_OPTIONS(self) -> None:  # noqa: N802
        if not self._host_is_local():
            self._send_json(403, {"ok": False, "error": "Akses hanya diizinkan melalui komputer lokal."})
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Printer-Token")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if not self._host_is_local():
            self._send_json(403, {"ok": False, "error": "Akses hanya diizinkan melalui komputer lokal."})
            return
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json(200, {
                "ok": True,
                "service": "Sani Laundry Printer Bridge",
                "version": 1,
                "platform": "windows",
                "printer_module_available": win32print is not None,
            })
            return
        if path == "/printers":
            if not self._authorized():
                self._send_json(401, {"ok": False, "error": "Token printer tidak valid. Salin token dari jendela Printer Bridge."})
                return
            try:
                printers, default_name = list_printers()
                self._send_json(200, {"ok": True, "printers": printers, "default_printer": default_name})
            except Exception as exc:
                print("[printer-bridge] /printers failed: %s: %s" % (type(exc).__name__, exc))
                self._send_json(500, {"ok": False, "error": str(exc)})
            return
        self._send_json(404, {"ok": False, "error": "Endpoint tidak ditemukan."})

    def do_POST(self) -> None:  # noqa: N802
        if not self._host_is_local():
            self._send_json(403, {"ok": False, "error": "Akses hanya diizinkan melalui komputer lokal."})
            return
        if urlparse(self.path).path != "/print":
            self._send_json(404, {"ok": False, "error": "Endpoint tidak ditemukan."})
            return
        if not self._authorized():
            self._send_json(401, {"ok": False, "error": "Token printer tidak valid. Salin token dari jendela Printer Bridge."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(413, {"ok": False, "error": "Ukuran data cetak kosong atau terlalu besar."})
            return
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            printer_name = str(body.get("printer_name", "")).strip()
            encoded = str(body.get("data_base64", ""))
            payload = base64.b64decode(encoded, validate=True)
            if not printer_name or not payload:
                raise ValueError("Nama printer dan data cetak wajib diisi.")
            if len(payload) > MAX_BODY_BYTES:
                raise ValueError("Data cetak melebihi batas 512 KB.")
            send_raw(printer_name, payload)
            self._send_json(200, {"ok": True, "message": "Data cetak sudah dikirim ke antrean Windows.", "printer": printer_name, "bytes": len(payload)})
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": str(exc)})


def main() -> int:
    if sys.platform != "win32":
        print("Printer Bridge ini khusus Windows karena memakai antrean printer Windows.")
        return 2
    if win32print is None:
        print("Modul pywin32 belum terpasang.")
        print("Jalankan: venv\\Scripts\\python.exe -m pip install pywin32")
        return 2
    print("=" * 64)
    print("SANI LAUNDRY - LOCAL PRINTER BRIDGE")
    print("Alamat : http://127.0.0.1:%s" % PORT)
    print("Token  : %s" % TOKEN)
    print("Salin token di atas ke Control Center > Printer Lokal.")
    print("Jangan bagikan token ini. Tutup jendela ini untuk menghentikan layanan.")
    print("=" * 64)
    try:
        server = ThreadingHTTPServer((HOST, PORT), BridgeHandler)
    except OSError as exc:
        print("Tidak dapat menjalankan Printer Bridge: %s" % exc)
        print("Pastikan port %s belum dipakai." % PORT)
        return 1
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\nMenghentikan Printer Bridge...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

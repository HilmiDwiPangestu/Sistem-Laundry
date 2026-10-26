from io import BytesIO
from pathlib import Path

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


YELLOW = colors.HexColor("#F6C90E")
INK = colors.HexColor("#1F2328")
MUTED = colors.HexColor("#667085")
LINE = colors.HexColor("#D9DEE7")
SOFT = colors.HexColor("#F7F8FA")


def rupiah(value):
    try:
        return "Rp{:,.0f}".format(float(value or 0)).replace(",", ".")
    except (TypeError, ValueError):
        return "Rp0"


def kg(value):
    if value is None:
        return "-"
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    return f"{text.replace('.', ',')} kg"


def _styles():
    base = getSampleStyleSheet()
    return {
        "business": ParagraphStyle(
            "Business",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=INK,
            spaceAfter=2,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=MUTED,
        ),
        "title": ParagraphStyle(
            "Title",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "summary_label": ParagraphStyle(
            "SummaryLabel",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=MUTED,
        ),
        "summary_value": ParagraphStyle(
            "SummaryValue",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=INK,
        ),
        "cell": ParagraphStyle(
            "Cell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=9.5,
            textColor=INK,
        ),
        "cell_right": ParagraphStyle(
            "CellRight",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=9.5,
            textColor=INK,
            alignment=TA_RIGHT,
        ),
        "cell_header": ParagraphStyle(
            "CellHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.4,
            leading=9.5,
            textColor=colors.white,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


def _header(laundry_settings, styles):
    left = []
    logo_path = Path(settings.BASE_DIR) / "static" / "img" / "sani-laundry-logo.png"
    if logo_path.exists():
        try:
            left.append(Image(str(logo_path), width=25 * mm, height=25 * mm, kind="proportional"))
        except Exception:
            pass

    business_lines = [Paragraph(laundry_settings.nama_usaha or "Sani Laundry", styles["business"])]
    if laundry_settings.alamat:
        business_lines.append(Paragraph(laundry_settings.alamat, styles["small"]))
    if laundry_settings.telepon:
        business_lines.append(Paragraph(f"Telp/WhatsApp: {laundry_settings.telepon}", styles["small"]))

    header = Table(
        [[left, business_lines]],
        colWidths=[32 * mm, 143 * mm],
        hAlign="LEFT",
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return header


def _summary_cards(summary, styles):
    cards = []
    for label, value in summary:
        cards.append(
            [
                Paragraph(label, styles["summary_label"]),
                Spacer(1, 1.5 * mm),
                Paragraph(str(value), styles["summary_value"]),
            ]
        )
    table = Table([cards], colWidths=[43.5 * mm] * len(cards), hAlign="CENTER")
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    table.setStyle(TableStyle(style))
    return table


def _transaction_table(rows, styles, show_date=True):
    if show_date:
        headers = ["No. Nota", "Tanggal", "Pelanggan", "Layanan", "Berat", "Tarif/kg", "Total", "Status"]
        widths = [26, 17, 29, 31, 16, 20, 22, 21]
    else:
        headers = ["No. Nota", "Pelanggan", "Layanan", "Berat", "Tarif/kg", "Total", "Status"]
        widths = [28, 34, 36, 18, 21, 24, 21]

    data = [[Paragraph(h, styles["cell_header"]) for h in headers]]
    for row in rows:
        common = [
            Paragraph(row["nomor"], styles["cell"]),
            Paragraph(row["pelanggan"], styles["cell"]),
            Paragraph(row["layanan"], styles["cell"]),
            Paragraph(kg(row["berat"]), styles["cell_right"]),
            Paragraph(rupiah(row["harga_per_kg"]), styles["cell_right"]),
            Paragraph(rupiah(row["total"]), styles["cell_right"]),
            Paragraph(row["status"], styles["cell"]),
        ]
        if show_date:
            common.insert(1, Paragraph(row["tanggal"], styles["cell"]))
        data.append(common)

    if len(data) == 1:
        empty_span = len(headers) - 1
        data.append([Paragraph("Tidak ada transaksi pada periode ini.", styles["cell"])] + [""] * empty_span)

    table = Table(data, colWidths=[w * mm for w in widths], repeatRows=1, hAlign="CENTER")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for idx in range(1, len(data)):
        if idx % 2 == 0:
            commands.append(("BACKGROUND", (0, idx), (-1, idx), SOFT))
    if len(data) == 2 and not rows:
        commands.append(("SPAN", (0, 1), (-1, 1)))
        commands.append(("ALIGN", (0, 1), (-1, 1), "CENTER"))
    table.setStyle(TableStyle(commands))
    return table


def build_report_pdf(*, title, subtitle, laundry_settings, summary, rows, show_date=True):
    """Build an A4 PDF and return raw bytes."""
    buffer = BytesIO()
    styles = _styles()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=14 * mm,
        title=title,
        author=laundry_settings.nama_usaha or "Sani Laundry",
    )

    story = [
        _header(laundry_settings, styles),
        Spacer(1, 5 * mm),
        Table([[""]], colWidths=[182 * mm], rowHeights=[1.6 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), YELLOW)])),
        Spacer(1, 5 * mm),
        Paragraph(title, styles["title"]),
        Paragraph(subtitle, styles["subtitle"]),
        Spacer(1, 6 * mm),
        KeepTogether(_summary_cards(summary, styles)),
        Spacer(1, 6 * mm),
        _transaction_table(rows, styles, show_date=show_date),
        Spacer(1, 6 * mm),
        Paragraph("Dokumen ini dihasilkan otomatis oleh Sistem Sani Laundry.", styles["footer"]),
    ]
    doc.build(story)
    value = buffer.getvalue()
    buffer.close()
    return value

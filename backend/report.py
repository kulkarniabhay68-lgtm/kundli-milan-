from __future__ import annotations

import io
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ==================================================
# 1. FONT SETTINGS (डिबगिंगसह)
# ==================================================

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT = os.path.join(
    ROOT, "fonts", "NotoSansDevanagari-Regular.ttf"
)
BOLD = os.path.join(
    ROOT, "fonts", "NotoSansDevanagari-Bold.ttf"
)

# डिबगिंगसाठी फॉन्टची स्थिती तपासत आहे
print("--- FONT DEBUG INFO ---")
print("ROOT:", ROOT)
print("Regular font path:", FONT)
print("Regular font exists:", os.path.exists(FONT))
print("Bold font path:", BOLD)
print("Bold font exists:", os.path.exists(BOLD))

if os.path.exists(FONT) and "Deva" not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(TTFont("Deva", FONT))

if os.path.exists(BOLD) and "DevaBold" not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(TTFont("DevaBold", BOLD))

BASE_FONT = "Deva" if os.path.exists(FONT) else "Helvetica"
BOLD_FONT = "DevaBold" if os.path.exists(BOLD) else "Helvetica-Bold"

print("Base font selected:", BASE_FONT)
print("Bold font selected:", BOLD_FONT)
print("-----------------------")


# ==================================================
# 2. HELPER FUNCTIONS
# ==================================================

SIGN_NAMES = {
    1: "मेष", 2: "वृषभ", 3: "मिथुन", 4: "कर्क",
    5: "सिंह", 6: "कन्या", 7: "तुला", 8: "वृश्चिक",
    9: "धनु", 10: "मकर", 11: "कुंभ", 12: "मीन",
}

NAKSHATRA_NAMES = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशीर्ष",
    "आर्द्रा", "पुनर्वसू", "पुष्य", "आश्लेषा", "मघा",
    "पूर्वा फाल्गुनी", "उत्तरा फाल्गुनी", "हस्त", "चित्रा",
    "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूळ",
    "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा",
    "शततारका", "पूर्वाभाद्रपदा", "उत्तराभाद्रपदा", "रेवती",
]


def fmt_date(value):
    if not value:
        return "-"
    try:
        year, month, day = str(value).split("-")
        return f"{day}/{month}/{year}"
    except (ValueError, AttributeError):
        return str(value)


def safe_text(value):
    if value is None or value == "":
        return "-"
    return str(value)


def sign_name(sign_no):
    try:
        return SIGN_NAMES.get(int(sign_no), "-")
    except (TypeError, ValueError):
        return "-"


def nakshatra_name(nakshatra_no):
    try:
        number = int(nakshatra_no)
        if 1 <= number <= 27:
            return NAKSHATRA_NAMES[number - 1]
    except (TypeError, ValueError):
        pass
    return "-"


def make_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontName=BOLD_FONT,
        fontSize=18,
        leading=25,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#744210"),
        spaceAfter=8 * mm,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        fontName=BOLD_FONT,
        fontSize=12,
        leading=17,
        spaceBefore=5 * mm,
        spaceAfter=3 * mm,
        textColor=colors.HexColor("#744210"),
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        fontName=BASE_FONT,
        fontSize=9,
        leading=14,
    ))

    return styles


def make_table(data, widths, header=True):
    table = Table(
        data,
        colWidths=widths,
        repeatRows=1 if header else 0,
        hAlign="LEFT",
    )

    commands = [
        ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbbd9b")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]

    if header:
        commands.extend([
            ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6e8bd")),
        ])

    table.setStyle(TableStyle(commands))
    return table


# ==================================================
# 3. PDF GENERATOR
# ==================================================

def build_pdf(result: dict) -> bytes:
    """
    सध्याच्या engine.py च्या response स्वरूपातून PDF तयार करते.
    अपेक्षित fields: kootas, total_score, max_score,
    birth_details आणि warnings.
    """

    if not isinstance(result, dict):
        raise ValueError("रिपोर्टसाठी निकाल dictionary स्वरूपात हवा.")

    birth_details = result.get("birth_details", {})
    boy = birth_details.get("groom", {})
    girl = birth_details.get("bride", {})
    kootas = result.get("kootas", [])

    if not kootas:
        raise ValueError(
            "निकालात kootas उपलब्ध नाहीत. आधी गुणमेलनाची गणना करा."
        )

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="कुंडली मिलन अहवाल",
        author="Kundli Milan",
    )

    styles = make_styles()
    story = []

    # ------------------------------
    # TITLE
    # ------------------------------

    story.append(Paragraph("कुंडली मिलन अहवाल", styles["ReportTitle"]))

    story.append(Paragraph(
        "जन्ममाहिती आणि अष्टकूट गुणमेलन",
        styles["ReportBody"],
    ))
    story.append(Spacer(1, 4 * mm))

    

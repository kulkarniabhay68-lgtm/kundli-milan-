from future import annotations

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

==================================================

1. FONT SETTINGS

==================================================

BASE_DIR = os.path.dirname(os.path.abspath(file))

FONT = os.path.join(
BASE_DIR, "NotoSansDevanagari-Regular (1).ttf"
)
BOLD = os.path.join(
BASE_DIR, "NotoSansDevanagari-Bold (1).ttf"
)

print("Regular font:", FONT, os.path.exists(FONT))
print("Bold font:", BOLD, os.path.exists(BOLD))

if not os.path.exists(FONT):
raise FileNotFoundError(f"Regular Marathi font not found: {FONT}")

if not os.path.exists(BOLD):
raise FileNotFoundError(f"Bold Marathi font not found: {BOLD}")

if "Deva" not in pdfmetrics.getRegisteredFontNames():
pdfmetrics.registerFont(TTFont("Deva", FONT))

if "DevaBold" not in pdfmetrics.getRegisteredFontNames():
pdfmetrics.registerFont(TTFont("DevaBold", BOLD))

BASE_FONT = "Deva"
BOLD_FONT = "DevaBold"

==================================================

2. HELPER FUNCTIONS

==================================================

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
    fontSize=20,
    leading=27,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#744210"),
    spaceAfter=8 * mm,
))

styles.add(ParagraphStyle(
    name="SectionHeading",
    fontName=BOLD_FONT,
    fontSize=14,
    leading=20,
    spaceBefore=5 * mm,
    spaceAfter=3 * mm,
    textColor=colors.HexColor("#744210"),
))

styles.add(ParagraphStyle(
    name="ReportBody",
    fontName=BASE_FONT,
    fontSize=11,
    leading=17,
))

styles.add(ParagraphStyle(
    name="TableText",
    fontName=BASE_FONT,
    fontSize=10,
    leading=15,
))

styles.add(ParagraphStyle(
    name="TableHeader",
    fontName=BOLD_FONT,
    fontSize=10,
    leading=15,
))

return styles

def make_table(data, widths, styles, header=True):
formatted_data = []

for row_index, row in enumerate(data):
    style_name = (
        "TableHeader"
        if header and row_index == 0
        else "TableText"
    )

    formatted_data.append([
        Paragraph(safe_text(cell), styles[style_name])
        for cell in row
    ])

table = Table(
    formatted_data,
    colWidths=widths,
    repeatRows=1 if header else 0,
    hAlign="LEFT",
)

commands = [
    ("GRID", (0, 0), (-1, -1), 0.4,
     colors.HexColor("#cbbd9b")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]

if header:
    commands.append(
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#f6e8bd"))
    )

table.setStyle(TableStyle(commands))
return table

==================================================

3. PDF GENERATOR

==================================================

def build_pdf(result: dict) -> bytes:
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

story.append(
    Paragraph("कुंडली मिलन अहवाल", styles["ReportTitle"])
)
story.append(
    Paragraph(
        "जन्ममाहिती आणि अष्टकूट गुणमेलन",
        styles["ReportBody"],
    )
)
story.append(Spacer(1, 4 * mm))

# जन्ममाहिती
story.append(
    Paragraph("१. जन्ममाहिती", styles["SectionHeading"])
)

birth_rows = [
    ["तपशील", "वर", "वधू"],
    [
        "जन्मतारीख",
        fmt_date(boy.get("birth_date")),
        fmt_date(girl.get("birth_date")),
    ],
    [
        "जन्मवेळ",
        safe_text(boy.get("birth_time")),
        safe_text(girl.get("birth_time")),
    ],
    [
        "जन्मस्थळ",
        safe_text(boy.get("birth_place")),
        safe_text(girl.get("birth_place")),
    ],
    [
        "टाइमझोन",
        safe_text(boy.get("timezone")),
        safe_text(girl.get("timezone")),
    ],
    [
        "अक्षांश",
        safe_text(boy.get("latitude")),
        safe_text(girl.get("latitude")),
    ],
    [
        "रेखांश",
        safe_text(boy.get("longitude")),
        safe_text(girl.get("longitude")),
    ],
    [
        "चंद्रराशी",
        sign_name(boy.get("sign_no")),
        sign_name(girl.get("sign_no")),
    ],
    [
        "नक्षत्र",
        nakshatra_name(boy.get("nakshatra_no")),
        nakshatra_name(girl.get("nakshatra_no")),
    ],
]

story.append(make_table(
    birth_rows,
    [42 * mm, 65 * mm, 65 * mm],
    styles,
))

# अष्टकूट गुणमेलन
story.append(
    Paragraph("२. अष्टकूट गुणमेलन", styles["SectionHeading"])
)

score_rows = [
    ["कूट", "वराची माहिती", "वधूची माहिती", "मिळालेले गुण", "कमाल गुण"]
]

for item in kootas:
    groom_value = (
        item.get("groom_varna")
        or item.get("groom_group")
        or item.get("groom_tara")
        or item.get("groom_yoni")
        or item.get("groom_lord")
        or item.get("groom_gana")
        or item.get("groom_nadi")
        or item.get("groom_sign_no")
        or "-"
    )

    bride_value = (
        item.get("bride_varna")
        or item.get("bride_group")
        or item.get("bride_tara")
        or item.get("bride_yoni")
        or item.get("bride_lord")
        or item.get("bride_gana")
        or item.get("bride_nadi")
        or item.get("bride_sign_no")
        or "-"
    )

    score_rows.append([
        safe_text(item.get("koota")),
        safe_text(groom_value),
        safe_text(bride_value),
        f"{float(item.get('score', 0)):g}",
        f"{float(item.get('max_score', 0)):g}",
    ])

total_score = float(result.get("total_score", 0))
max_score = float(result.get("max_score", 36))

score_rows.append([
    "एकूण", "-", "-", f"{total_score:g}", f"{max_score:g}"
])

story.append(make_table(
    score_rows,
    [34 * mm, 39 * mm, 39 * mm, 30 * mm, 25 * mm],
    styles,
))

story.append(Spacer(1, 4 * mm))

story.append(
    Paragraph(
        f"एकूण गुण: {total_score:g} / {max_score:g}",
        styles["SectionHeading"],
    )
)

if result.get("is_suitable_by_score_only"):
    score_message = (
        "सध्याच्या गुणनियमांनुसार १८ किंवा अधिक गुण मिळाले आहेत."
    )
else:
    score_message = (
        "सध्याच्या गुणनियमांनुसार १८ पेक्षा कमी गुण मिळाले आहेत."
    )

story.append(Paragraph(score_message, styles["ReportBody"]))

# निरीक्षणे
story.append(
    Paragraph("३. गुणमेलनातील निरीक्षणे", styles["SectionHeading"])
)

nadi_item = next(
    (item for item in kootas if item.get("koota") == "नाडी"),
    None,
)
bhakoot_item = next(
    (item for item in kootas if item.get("koota") == "भकूट"),
    None,
)

observations = []

if nadi_item:
    if nadi_item.get("nadi_dosha_indicated"):
        observations.append(
            "दोघांची नाडी समान असल्याचे गणनेत दिसते. "
            "पारंपरिक नियम व परिहार स्वतंत्रपणे तपासणे आवश्यक आहे."
        )
    else:
        observations.append(
            "या गणनेनुसार दोघांची नाडी समान नाही."
        )

if bhakoot_item:
    if bhakoot_item.get("unfavorable_pair"):
        observations.append(
            "भकूटातील प्रतिकूल जोडी दर्शवली आहे. "
            "परिहाराचे नियम स्वतंत्रपणे तपासणे आवश्यक आहे."
        )
    else:
        observations.append(
            "वापरलेल्या मूलभूत नियमांनुसार भकूट दोष दर्शवलेला नाही."
        )

if not observations:
    observations.append(
        "दोषविषयक निरीक्षणांसाठी पुरेशी माहिती उपलब्ध नाही."
    )

for note in observations:
    story.append(
        Paragraph("• " + note, styles["ReportBody"])
    )

# सूचना
story.append(
    Paragraph("४. महत्त्वाच्या सूचना", styles["SectionHeading"])
)

warnings = result.get("warnings", [])

if not warnings:
    warnings = [
        "गुणतक्ते आणि नक्षत्र-वर्गीकरण प्रमाणित स्रोताशी पडताळा.",
        "गुणांवरूनच विवाहाचा अंतिम निर्णय घेऊ नये.",
    ]

for warning in warnings:
    story.append(
        Paragraph(
            "• " + safe_text(warning),
            styles["ReportBody"],
        )
    )

story.append(Spacer(1, 5 * mm))

story.append(
    Paragraph(
        "हा अहवाल सॉफ्टवेअरने दिलेल्या गणनेवर आधारित आहे. "
        "लग्नकुंडली, मंगळदोष आणि इतर ग्रहस्थितींचे स्वतंत्र "
        "विश्लेषण या अहवालात समाविष्ट नाही.",
        styles["ReportBody"],
    )
)

doc.build(story)
return buffer.getvalue()

def generate_report(result: dict) -> bytes:
return build_pdf(result)

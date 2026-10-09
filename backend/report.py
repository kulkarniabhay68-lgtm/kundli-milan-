from __future__ import annotations

import io
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

ROOT = os.path.dirname(os.path.dirname(__file__))

FONT = os.path.join(
    ROOT, "fonts", "NotoSansDevanagari-Regular.ttf"
)
BOLD = os.path.join(
    ROOT, "fonts", "NotoSansDevanagari-Bold.ttf"
)

if os.path.exists(FONT):
    pdfmetrics.registerFont(TTFont("Deva", FONT))

if os.path.exists(BOLD):
    pdfmetrics.registerFont(TTFont("DevaBold", BOLD))

BASE_FONT = "Deva" if os.path.exists(FONT) else "Helvetica"
BOLD_FONT = "DevaBold" if os.path.exists(BOLD) else "Helvetica-Bold"

PABBR = {
    "सूर्य": "रवि",
    "चंद्र": "चं",
    "मंगळ": "मं",
    "बुध": "बु",
    "गुरु": "गु",
    "शुक्र": "शु",
    "शनि": "श",
    "राहू": "रा",
    "केतू": "के",
}


def fmt_date(value):
    year, month, day = value.split("-")
    return f"{day}/{month}/{year}"


def chart_grid(chart):
    houses = [[] for _ in range(12)]
    asc = chart["lagna"]["sign_no"]

    for name, body in chart["bodies"].items():
        house = ((body["sign_no"] - asc) % 12) + 1
        houses[house - 1].append(PABBR.get(name, name))

    positions = {
        0: (1, 0),
        1: (0, 0),
        2: (0, 1),
        3: (0, 2),
        4: (0, 3),
        5: (1, 3),
        6: (2, 3),
        7: (3, 3),
        8: (3, 2),
        9: (3, 1),
        10: (3, 0),
        11: (2, 0),
    }

    data = [[""] * 4 for _ in range(4)]

    for house, (row, col) in positions.items():
        sign = ((asc + house - 1) % 12) + 1
        data[row][col] = f"{sign}\n" + " ".join(houses[house])

    for row in range(4):
        for col in range(4):
            if (row, col) in {
                (1, 1), (1, 2), (2, 1), (2, 2)
            }:
                data[row][col] = ""

    table = Table(
        data,
        colWidths=[23 * mm] * 4,
        rowHeights=[18 * mm] * 4,
    )
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#9b7a39")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#9b7a39")),
    ]))
    return table


def build_pdf(result: dict) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="DevaTitle",
        fontName=BOLD_FONT,
        fontSize=18,
        leading=23,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="DevaH",
        fontName=BOLD_FONT,
        fontSize=12,
        leading=16,
        spaceBefore=6,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="Deva",
        fontName=BASE_FONT,
        fontSize=8.5,
        leading=13,
    ))

    story = []
    boy = result["boy"]
    girl = result["girl"]

    story += [
        Paragraph("कुंडली मिलन अहवाल", styles["DevaTitle"]),
        Spacer(1, 5 * mm),
    ]

    info = [
        ["वर", boy["name"], "वधू", girl["name"]],
        [
            "जन्म",
            fmt_date(boy["date"]) + " " + boy["time"],
            "जन्म",
            fmt_date(girl["date"]) + " " + girl["time"],
        ],
        [
            "जन्मस्थळ",
            boy.get("place_display", boy.get("place", "")),
            "जन्मस्थळ",
            girl.get("place_display", girl.get("place", "")),
        ],
        [
            "अक्षांश / रेखांश",
            f'{boy["latitude"]:.4f}, {boy["longitude"]:.4f}',
            "अक्षांश / रेखांश",
            f'{girl["latitude"]:.4f}, {girl["longitude"]:.4f}',
        ],
        ["चंद्रराशी", boy["moon_rashi"], "चंद्रराशी", girl["moon_rashi"]],
        [
            "नक्षत्र / चरण",
            f'{boy["nakshatra"]} ({boy["pada"]})',
            "नक्षत्र / चरण",
            f'{girl["nakshatra"]} ({girl["pada"]})',
        ],
        [
            "लग्नराशी",
            boy["lagna"]["rashi"],
            "लग्नराशी",
            girl["lagna"]["rashi"],
        ],
        [
            "नाडी / गण / योनि",
            f'{boy["nadi"]} / {boy["gana"]} / {boy["yoni"]}',
            "नाडी / गण / योनि",
            f'{girl["nadi"]} / {girl["gana"]} / {girl["yoni"]}',
        ],
    ]

    table = Table(
        info,
        colWidths=[28 * mm, 62 * mm, 28 * mm, 62 * mm],
    )
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
        ("FONTNAME", (0, 0), (0, -1), BOLD_FONT),
        ("FONTNAME", (2, 0), (2, -1), BOLD_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbbd9b")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffaf0")),
    ]))

    story += [
        table,
        Spacer(1, 5 * mm),
        Paragraph("लग्न कुंडल्या", styles["DevaH"]),
    ]

    charts = Table(
        [[
            [Paragraph("वर", styles["DevaH"]), chart_grid(boy)],
            [Paragraph("वधू", styles["DevaH"]), chart_grid(girl)],
        ]],
        colWidths=[91 * mm, 91 * mm],
    )
    charts.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    story += [charts, PageBreak()]
    story.append(Paragraph("गुणमेलन — अष्टकूट", styles["DevaH"]))

    match = result["match"]
    rows = [["कूट", "कमाल", "मिळाले"]]

    for item in match["kootas"]:
        score = item["score"]
        if isinstance(score, float):
            score = f"{score:g}"
        rows.append([item["name"], str(item["max"]), str(score)])

    rows.append([
        "अष्टकूट एकूण",
        "36",
        f'{match["ashtakoot_total"]:g}',
    ])
    rows.append([
        "सत्कूट (तात्पुरती reference गणना)",
        "3",
        str(match["satkoot_bonus_provisional"]),
    ])
    rows.append([
        "संदर्भ एकूण",
        "—",
        f'{match["reference_total_provisional"]:g}',
    ])

    koot_table = Table(
        rows,
        colWidths=[100 * mm, 30 * mm, 35 * mm],
    )
    koot_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("FONTNAME", (0, -3), (-1, -1), BOLD_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bfa56b")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6e8bd")),
    ]))

    story += [koot_table, Spacer(1, 5 * mm)]

    notes = []
    if match["bhakoot_dosha"]:
        notes.append("राशी-कूट दोष नोंदला आहे.")
    if match["nadi_dosha"]:
        notes.append("नाडी दोष नोंदला आहे.")
    if match["nadi_pada_vedha"]:
        notes.append("नाडी पादवेध नोंदला आहे.")
    if not notes:
        notes.append("अष्टकूटातील नाडी व राशी-कूटामध्ये दोष नोंदलेला नाही.")

    story.append(Paragraph(
        "गुणमेलन निरीक्षण: " + " ".join(notes),
        styles["Deva"],
    ))

    story.append(Paragraph("मंगळ दोष", styles["DevaH"]))
    mangal = result["mangal"]

    mangal_rows = [
        ["", "वर", "वधू"],
        [
            "लग्नापासून",
            str(mangal["boy"]["houses"]["lagna"]),
            str(mangal["girl"]["houses"]["lagna"]),
        ],
        [
            "चंद्रापासून",
            str(mangal["boy"]["houses"]["moon"]),
            str(mangal["girl"]["houses"]["moon"]),
        ],
        [
            "शुक्रापासून",
            str(mangal["boy"]["houses"]["venus"]),
            str(mangal["girl"]["houses"]["venus"]),
        ],
        [
            "मंगळदोष",
            "होय" if mangal["boy"]["manglik"] else "नाही",
            "होय" if mangal["girl"]["manglik"] else "नाही",
        ],
    ]

    mangal_table = Table(
        mangal_rows,
        colWidths=[60 * mm, 45 * mm, 45 * mm],
    )
    mangal_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bfa56b")),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    story += [
        mangal_table,
        Spacer(1, 5 * mm),
        Paragraph("ग्रहमेलन — गणितावर आधारित निरीक्षण", styles["DevaH"]),
    ]

    for note in result.get("graha_milan_notes", []):
        story.append(Paragraph("• " + note, styles["Deva"]))

    story += [
        Spacer(1, 3 * mm),
        Paragraph(
            "टीप: ग्रहमेलनातील निरीक्षणे गणनेवर आधारित आहेत. "
            "सत्कूटाचे 3 गुण येथे provisional reference म्हणून स्वतंत्र दाखवले आहेत.",
            styles["Deva"],
        ),
    ]

    doc.build(story)
    return buffer.getvalue()


def generate_report(result: dict) -> bytes:
    """FastAPI endpoint साठी PDF bytes परत करते."""
    return build_pdf(result)

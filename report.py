from __future__ import annotations

import io, os, math
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

ROOT=os.path.dirname(os.path.dirname(__file__))
FONT=os.path.join(ROOT,"fonts","NotoSansDevanagari-Regular.ttf")
BOLD=os.path.join(ROOT,"fonts","NotoSansDevanagari-Bold.ttf")
if os.path.exists(FONT): pdfmetrics.registerFont(TTFont("Deva",FONT))
if os.path.exists(BOLD): pdfmetrics.registerFont(TTFont("DevaBold",BOLD))
BASE_FONT="Deva" if os.path.exists(FONT) else "Helvetica"
BOLD_FONT="DevaBold" if os.path.exists(BOLD) else "Helvetica-Bold"

SIGNS=["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]
PABBR={"सूर्य":"रवि","चंद्र":"चं","मंगळ":"मं","बुध":"बु","गुरु":"गु","शुक्र":"शु","शनि":"श","राहू":"रा","केतू":"के"}

def fmt_date(v):
    y,m,d=v.split("-"); return f"{d}/{m}/{y}"

def chart_grid(chart):
    # North Indian-style 12-house diamond grid. Each cell contains sign number and planets.
    houses=[[] for _ in range(12)]
    asc=chart["lagna"]["sign_no"]
    for name,b in chart["bodies"].items():
        h=((b["sign_no"]-asc)%12)+1
        houses[h-1].append(PABBR.get(name,name))
    # 4x4 matrix positions for diamond-style houses.
    pos={
        0:(1,0),1:(0,0),2:(0,1),3:(0,2),4:(0,3),5:(1,3),
        6:(2,3),7:(3,3),8:(3,2),9:(3,1),10:(3,0),11:(2,0)
    }
    data=[[""]*4 for _ in range(4)]
    for h,(r,c) in pos.items():
        sign=((asc+h-1)%12)+1
        txt=f"{sign}\n"+" ".join(houses[h])
        data[r][c]=txt
    # Put center blank-ish; diamond boundaries are represented by a light square grid.
    for r in range(4):
        for c in range(4):
            if (r,c) in {(1,1),(1,2),(2,1),(2,2)}: data[r][c]=""
    t=Table(data,colWidths=[23*mm]*4,rowHeights=[18*mm]*4)
    t.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),BASE_FONT),
        ("FONTSIZE",(0,0),(-1,-1),7),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("GRID",(0,0),(-1,-1),0.6,colors.HexColor("#9b7a39")),
        ("BOX",(0,0),(-1,-1),1,colors.HexColor("#9b7a39")),
        ("SPAN",(1,1),(2,2)),
    ]))
    return t

def build_pdf(result:dict)->bytes:
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=12*mm,leftMargin=12*mm,topMargin=12*mm,bottomMargin=12*mm)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="DevaTitle",fontName=BOLD_FONT,fontSize=18,leading=23,alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="DevaH",fontName=BOLD_FONT,fontSize=12,leading=16,spaceBefore=6,spaceAfter=5))
    styles.add(ParagraphStyle(name="Deva",fontName=BASE_FONT,fontSize=8.5,leading=13))
    story=[]
    boy,girl=result["boy"],result["girl"]
    story += [Paragraph("कुंडली मिलन अहवाल",styles["DevaTitle"]),Spacer(1,5*mm)]
    info=[
        ["वर",boy["name"],"वधू",girl["name"]],
        ["जन्म",fmt_date(boy["date"])+"  "+boy["time"],"जन्म",fmt_date(girl["date"])+"  "+girl["time"]],
        ["जन्मस्थळ",boy.get("place_display",boy["place"]), "जन्मस्थळ",girl.get("place_display",girl["place"])],
        ["अक्षांश / रेखांश",f'{boy["latitude"]:.4f}, {boy["longitude"]:.4f}',"अक्षांश / रेखांश",f'{girl["latitude"]:.4f}, {girl["longitude"]:.4f}'],
        ["चंद्रराशी",boy["moon_rashi"],"चंद्रराशी",girl["moon_rashi"]],
        ["नक्षत्र / चरण",f'{boy["nakshatra"]} ({boy["pada"]})',"नक्षत्र / चरण",f'{girl["nakshatra"]} ({girl["pada"]})'],
        ["लग्नराशी",boy["lagna"]["rashi"],"लग्नराशी",girl["lagna"]["rashi"]],
        ["नाडी / गण / योनि",f'{boy["nadi"]} / {boy["gana"]} / {boy["yoni"]}',"नाडी / गण / योनि",f'{girl["nadi"]} / {girl["gana"]} / {girl["yoni"]}'],
    ]
    t=Table(info,colWidths=[28*mm,62*mm,28*mm,62*mm])
    t.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),BASE_FONT),("FONTNAME",(0,0),(0,-1),BOLD_FONT),("FONTNAME",(2,0),(2,-1),BOLD_FONT),
                           ("FONTSIZE",(0,0),(-1,-1),7.5),("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#cbbd9b")),("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#fffaf0"))]))
    story += [t,Spacer(1,5*mm),Paragraph("लग्न कुंडल्या",styles["DevaH"])]
    charts=Table([[ [Paragraph("वर",styles["DevaH"]), chart_grid(boy)], [Paragraph("वधू",styles["DevaH"]), chart_grid(girl)] ]], colWidths=[91*mm,91*mm])
    charts.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
    story += [charts,PageBreak()]

    story += [Paragraph("गुणमेलन — अष्टकूट",styles["DevaH"])]
    rows=[["कूट","कमाल","मिळाले"]]
    for x in result["match"]["kootas"]:
        rows.append([x["name"],str(x["max"]),str(x["score"]).rstrip("0").rstrip(".") if isinstance(x["score"],float) else str(x["score"])])
    rows.append(["अष्टकूट एकूण","36",str(result["match"]["ashtakoot_total"]).rstrip("0").rstrip(".")])
    rows.append(["सत्कूट (तात्पुरती reference गणना)","3",str(result["match"]["satkoot_bonus_provisional"])])
    rows.append(["संदर्भ एकूण","—",str(result["match"]["reference_total_provisional"]).rstrip("0").rstrip(".")])
    kt=Table(rows,colWidths=[100*mm,30*mm,35*mm])
    kt.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),BASE_FONT),("FONTNAME",(0,0),(-1,0),BOLD_FONT),("FONTNAME",(0,-3),(-1,-1),BOLD_FONT),
                            ("FONTSIZE",(0,0),(-1,-1),8.5),("ALIGN",(1,1),(-1,-1),"CENTER"),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#bfa56b")),
                            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#f6e8bd"))]))
    story += [kt,Spacer(1,5*mm)]
    notes=[]
    if result["match"]["bhakoot_dosha"]: notes.append("राशी-कूट दोष नोंदला आहे.")
    if result["match"]["nadi_dosha"]: notes.append("नाडी दोष नोंदला आहे.")
    if result["match"]["nadi_pada_vedha"]: notes.append("नाडी पादवेध नोंदला आहे.")
    if not notes: notes.append("अष्टकूटातील नाडी व राशी-कूटामध्ये दोष नोंदलेला नाही.")
    story += [Paragraph("गुणमेलन निरीक्षण: "+" ".join(notes),styles["Deva"])]

    story += [Paragraph("मंगळ दोष",styles["DevaH"])]
    mg=result["mangal"]
    mrows=[["", "वर","वधू"],
           ["लग्नापासून",str(mg["boy"]["houses"]["lagna"]),str(mg["girl"]["houses"]["lagna"])],
           ["चंद्रापासून",str(mg["boy"]["houses"]["moon"]),str(mg["girl"]["houses"]["moon"])],
           ["शुक्रापासून",str(mg["boy"]["houses"]["venus"]),str(mg["girl"]["houses"]["venus"])],
           ["मंगळदोष", "होय" if mg["boy"]["manglik"] else "नाही", "होय" if mg["girl"]["manglik"] else "नाही"]]
    mt=Table(mrows,colWidths=[60*mm,45*mm,45*mm])
    mt.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),BASE_FONT),("FONTNAME",(0,0),(-1,0),BOLD_FONT),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#bfa56b")),("ALIGN",(1,1),(-1,-1),"CENTER")]))
    story += [mt,Spacer(1,5*mm)]

    story += [Paragraph("ग्रहमेलन — गणितावर आधारित निरीक्षण",styles["DevaH"])]
    for n in result.get("graha_milan_notes",[]):
        story.append(Paragraph("• "+n,styles["Deva"]))
    story += [Spacer(1,3*mm),Paragraph(
        "टीप: या आवृत्तीत ग्रहमेलनातील वाक्ये केवळ गणनेतून सिद्ध होणाऱ्या घटकांवर तयार केली आहेत. "
        "दाते पंचांगच्या अतिरिक्त 'नाडीपादवेध व नवांशमैत्री' सत्कूटासाठी sample PDF मध्ये नियमांचे पूर्ण scoring table प्रकाशित नाही; "
        "म्हणून त्या 3 गुणांची गणना येथे provisional reference म्हणून स्वतंत्र दाखवली आहे.",
        styles["Deva"])]
    doc.build(story)
    return buf.getvalue()

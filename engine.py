from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any
import math

import swisseph as swe

SIGNS = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]
SIGN_LORDS = ["मंगळ","शुक्र","बुध","चंद्र","रवि","बुध","शुक्र","मंगळ","गुरु","शनि","शनि","गुरु"]

NAKSHATRAS = [
    "अश्विनी","भरणी","कृत्तिका","रोहिणी","मृगशीर्ष","आर्द्रा","पुनर्वसू","पुष्य",
    "आश्लेषा","मघा","पूर्वा फाल्गुनी","उत्तरा फाल्गुनी","हस्त","चित्रा","स्वाती",
    "विशाखा","अनुराधा","ज्येष्ठा","मूळ","पूर्वाषाढा","उत्तराषाढा","श्रवण",
    "धनिष्ठा","शतभिषा","पूर्वाभाद्रपदा","उत्तराभाद्रपदा","रेवती"
]
NAK_LORDS = ["केतू","शुक्र","रवि","चंद्र","मंगळ","राहू","गुरु","शनि","बुध"] * 3

NADI = ["आद्य","मध्य","अंत्य","अंत्य","मध्य","आद्य","आद्य","मध्य","अंत्य",
        "अंत्य","मध्य","आद्य","आद्य","मध्य","अंत्य","अंत्य","मध्य","आद्य",
        "आद्य","मध्य","अंत्य","अंत्य","मध्य","आद्य","आद्य","मध्य","अंत्य"]

GANA = {
    1:"देव",2:"मनुष्य",3:"राक्षस",4:"मनुष्य",5:"देव",6:"मनुष्य",7:"देव",8:"देव",9:"राक्षस",
    10:"राक्षस",11:"मनुष्य",12:"मनुष्य",13:"देव",14:"राक्षस",15:"देव",16:"राक्षस",17:"देव",
    18:"राक्षस",19:"राक्षस",20:"मनुष्य",21:"मनुष्य",22:"देव",23:"राक्षस",24:"राक्षस",25:"मनुष्य",
    26:"मनुष्य",27:"देव"
}

# 27 Nakshatra -> Yoni. This mapping follows the traditional 14-yoni table.
YONI = {
    1:"अश्व",2:"गज",3:"मेष",4:"सर्प",5:"सर्प",6:"श्वान",7:"मांजर",8:"मेष",
    9:"मांजर",10:"मूषक",11:"मूषक",12:"गाय",13:"महिषी",14:"व्याघ्र",15:"महिषी",
    16:"व्याघ्र",17:"हरिण",18:"हरिण",19:"श्वान",20:"वानर",21:"नकुल",22:"वानर",
    23:"सिंह",24:"अश्व",25:"सिंह",26:"गाय",27:"गज"
}
# Published 14x14 classical-style matrix; row=bride, col=groom.
YONI_ORDER = ["अश्व","गज","मेष","सर्प","श्वान","मांजर","मूषक","गाय","महिषी","व्याघ्र","हरिण","वानर","नकुल","सिंह"]
YONI_MATRIX = [
    [4,2,2,3,2,2,2,1,0,1,3,3,2,1],
    [2,4,3,3,2,2,2,2,3,1,2,3,2,0],
    [2,3,4,2,1,2,1,3,3,1,2,0,3,1],
    [3,3,2,4,2,1,1,1,1,2,2,2,0,2],
    [2,2,1,2,4,2,1,2,2,1,0,2,1,1],
    [2,2,2,1,2,4,0,2,2,1,3,3,2,1],
    [2,2,1,1,1,0,4,2,2,2,2,2,1,2],
    [1,2,3,1,2,2,2,4,3,0,3,2,2,1],
    [0,3,3,1,2,2,2,3,4,1,2,2,2,1],
    [1,1,1,2,1,1,2,1,1,4,1,1,2,1],
    [3,2,2,2,0,3,2,3,2,1,4,2,2,1],
    [3,3,0,2,2,3,2,2,2,1,2,4,3,2],
    [2,2,3,0,1,2,1,2,2,2,2,3,4,2],
    [1,0,1,2,1,1,2,1,1,1,1,2,2,4],
]

NATURAL_FRIENDSHIP = {
    "रवि":{"रवि":"same","चंद्र":"friend","मंगळ":"friend","बुध":"neutral","गुरु":"friend","शुक्र":"enemy","शनि":"enemy"},
    "चंद्र":{"रवि":"friend","चंद्र":"same","मंगळ":"neutral","बुध":"friend","गुरु":"neutral","शुक्र":"neutral","शनि":"neutral"},
    "मंगळ":{"रवि":"friend","चंद्र":"friend","मंगळ":"same","बुध":"enemy","गुरु":"friend","शुक्र":"neutral","शनि":"neutral"},
    "बुध":{"रवि":"friend","चंद्र":"enemy","मंगळ":"neutral","बुध":"same","गुरु":"enemy","शुक्र":"friend","शनि":"neutral"},
    "गुरु":{"रवि":"friend","चंद्र":"friend","मंगळ":"friend","बुध":"enemy","गुरु":"same","शुक्र":"enemy","शनि":"neutral"},
    "शुक्र":{"रवि":"enemy","चंद्र":"neutral","मंगळ":"neutral","बुध":"friend","गुरु":"enemy","शुक्र":"same","शनि":"friend"},
    "शनि":{"रवि":"enemy","चंद्र":"neutral","मंगळ":"enemy","बुध":"friend","गुरु":"neutral","शुक्र":"friend","शनि":"same"},
}

PLANETS = [
    ("सूर्य", swe.SUN), ("चंद्र", swe.MOON), ("मंगळ", swe.MARS), ("बुध", swe.MERCURY),
    ("गुरु", swe.JUPITER), ("शुक्र", swe.VENUS), ("शनि", swe.SATURN), ("राहू", swe.TRUE_NODE)
]

def norm360(x: float) -> float:
    return x % 360.0

def dms(deg: float) -> str:
    d = int(deg)
    mf = (deg - d) * 60
    m = int(mf)
    s = round((mf - m) * 60)
    if s == 60:
        s, m = 0, m + 1
    if m == 60:
        m, d = 0, d + 1
    return f"{d:02d}° {m:02d}' {s:02d}\""

def sign_index(lon: float) -> int:
    return int(norm360(lon) // 30) + 1

def varna(sign_no: int) -> int:
    if sign_no in (4, 8, 12): return 4
    if sign_no in (1, 5, 9): return 3
    if sign_no in (2, 6, 10): return 2
    return 1

def vashya_group(sign_no: int, degree_in_sign: float) -> str:
    if sign_no in (3, 6, 7, 11): return "मानव"
    if sign_no == 9 and degree_in_sign < 15: return "मानव"
    if sign_no in (1, 2) or (sign_no == 9 and degree_in_sign >= 15) or (sign_no == 10 and degree_in_sign < 15):
        return "चतुष्पद"
    if sign_no in (4, 12) or (sign_no == 10 and degree_in_sign >= 15):
        return "जलचर"
    if sign_no == 5: return "वनचर"
    if sign_no == 8: return "कीट"
    raise ValueError("Invalid sign")

def vashya_score(groom_group: str, bride_group: str) -> float:
    if groom_group == bride_group:
        return 2.0
    partial = {
        ("मानव","चतुष्पद"), ("चतुष्पद","मानव"),
        ("मानव","जलचर"), ("जलचर","मानव"),
        ("चतुष्पद","वनचर"), ("वनचर","चतुष्पद"),
        ("जलचर","कीट"), ("कीट","जलचर")
    }
    return 1.0 if (groom_group, bride_group) in partial else 0.0

def tara_score(groom_nak: int, bride_nak: int) -> float:
    def good(a: int, b: int) -> bool:
        count = (b - a) % 27 + 1
        remainder = count % 9
        return remainder in (0, 2, 4, 6, 8)
    a = good(groom_nak, bride_nak)
    b = good(bride_nak, groom_nak)
    return 3.0 if a and b else 1.5 if a or b else 0.0

def yoni_score(groom_nak: int, bride_nak: int) -> int:
    yg, yb = YONI[groom_nak], YONI[bride_nak]
    return YONI_MATRIX[YONI_ORDER.index(yb)][YONI_ORDER.index(yg)]

def graha_maitri_score(groom_lord: str, bride_lord: str) -> float:
    a = NATURAL_FRIENDSHIP[groom_lord][bride_lord]
    b = NATURAL_FRIENDSHIP[bride_lord][groom_lord]
    if a == "same": return 5.0
    pair = {a, b}
    if pair == {"friend"}: return 5.0
    if pair == {"friend", "neutral"}: return 4.0
    if pair == {"neutral"}: return 3.0
    if pair == {"friend", "enemy"}: return 1.0
    if pair == {"neutral", "enemy"}: return 0.5
    return 0.0

def gana_score(groom: str, bride: str) -> float:
    if groom == bride: return 6.0
    if (groom, bride) == ("देव", "मनुष्य"): return 6.0
    if (groom, bride) == ("मनुष्य", "देव"): return 5.0
    if (groom, bride) == ("देव", "राक्षस"): return 1.0
    return 0.0

def bhakoot_score(groom_sign: int, bride_sign: int) -> int:
    d1 = (bride_sign - groom_sign) % 12 + 1
    d2 = (groom_sign - bride_sign) % 12 + 1
    return 0 if (d1, d2) in {(2,12),(12,2),(5,9),(9,5),(6,8),(8,6)} else 7

def nadi_score(groom_nak: int, bride_nak: int) -> int:
    return 0 if NADI[groom_nak-1] == NADI[bride_nak-1] else 8

def nadi_pada_vedha(groom_nak: int, groom_pada: int, bride_nak: int, bride_pada: int) -> bool:
    if groom_nak != bride_nak:
        return False
    return {groom_pada, bride_pada} in ({1,4},{2,3})

def navamsa_sign_from_longitude(lon: float) -> int:
    sign = sign_index(lon)
    pada = int((lon % 30) // (30/9))
    # Standard D9 navamsa sequence by sign:
    # movable -> same sign, fixed -> 9th from sign, dual -> 5th from sign.
    starts = {1:1,2:10,3:7,4:4,5:1,6:10,7:7,8:4,9:1,10:10,11:7,12:4}
    return ((starts[sign] - 1 + pada) % 12) + 1

def house_from_cusps(lon: float, cusps) -> int:
    x = norm360(lon)
    c = [norm360(x) for x in cusps[:12]]
    for i in range(12):
        start, end = c[i], c[(i+1)%12]
        if i == 11:
            end += 360
        xx = x if x >= start else x + 360
        if start <= xx < end:
            return i+1
    return 12

def calculate_chart(person: dict) -> dict:
    dt = datetime.fromisoformat(person["date"] + "T" + person["time"])
    tz = ZoneInfo(person.get("timezone", "Asia/Kolkata"))
    local = dt.replace(tzinfo=tz)
    utc = local.astimezone(ZoneInfo("UTC"))
    hour = utc.hour + utc.minute/60 + utc.second/3600
    jd = swe.julday(utc.year, utc.month, utc.day, hour, swe.GREG_CAL)

    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    bodies = {}
    for name, pid in PLANETS:
        xx, _ = swe.calc_ut(jd, pid, flags)
        lon = norm360(xx[0])
        sign = sign_index(lon)
        bodies[name] = {
            "longitude": lon,
            "degree": dms(lon % 30),
            "rashi": SIGNS[sign-1],
            "sign_no": sign,
            "retrograde": bool(xx[3] < 0)
        }

    ketu_lon = norm360(bodies["राहू"]["longitude"] + 180)
    ketu_sign = sign_index(ketu_lon)
    bodies["केतू"] = {
        "longitude": ketu_lon, "degree": dms(ketu_lon % 30),
        "rashi": SIGNS[ketu_sign-1], "sign_no": ketu_sign, "retrograde": True
    }

    # D1 whole-sign houses: this is kept deterministic for the primary Rashi chart.
    _, ascmc = swe.houses_ex(jd, float(person["latitude"]), float(person["longitude"]), b"W", swe.FLG_SIDEREAL)
    asc = norm360(ascmc[0])
    asc_sign = sign_index(asc)

    # Bhava Chalit working layer: Placidus cusps are kept separately so we never
    # silently mix Bhava Chalit positions into the D1 whole-sign chart.
    chal_cusps, _ = swe.houses_ex(jd, float(person["latitude"]), float(person["longitude"]), b"P", swe.FLG_SIDEREAL)

    for body in bodies.values():
        body["house"] = ((body["sign_no"] - asc_sign) % 12) + 1
        body["bhava_chalit_house"] = house_from_cusps(body["longitude"], chal_cusps)

    moon_lon = bodies["चंद्र"]["longitude"]
    nak = int(moon_lon / (360/27)) + 1
    within = moon_lon % (360/27)
    pada = int(within / ((360/27)/4)) + 1
    moon_nav_sign = navamsa_sign_from_longitude(moon_lon)

    return {
        "name": person["name"], "date": person["date"], "time": person["time"],
        "place": person["place"], "place_display": person.get("place_display", person["place"]),
        "latitude": float(person["latitude"]), "longitude": float(person["longitude"]),
        "timezone": person.get("timezone", "Asia/Kolkata"), "utc": utc.isoformat(),
        "julian_day": jd,
        "lagna": {
            "longitude": asc, "degree": dms(asc % 30), "rashi": SIGNS[asc_sign-1], "sign_no": asc_sign
        },
        "bodies": bodies,
        "moon_rashi": bodies["चंद्र"]["rashi"], "moon_sign_no": bodies["चंद्र"]["sign_no"],
        "nakshatra": NAKSHATRAS[nak-1], "nakshatra_no": nak, "pada": pada,
        "nadi": NADI[nak-1], "gana": GANA[nak], "yoni": YONI[nak],
        "varna": varna(bodies["चंद्र"]["sign_no"]),
        "vashya": vashya_group(bodies["चंद्र"]["sign_no"], moon_lon % 30),
        "moon_navamsa_sign": SIGNS[moon_nav_sign-1],
        "moon_navamsa_lord": SIGN_LORDS[moon_nav_sign-1],
        "lagna_lord": SIGN_LORDS[asc_sign-1],
        "sun_rashi": bodies["सूर्य"]["rashi"]
    }

def match_charts(groom: dict, bride: dict) -> dict:
    items = [
        ("वर्ण",1.0,1.0 if groom["varna"] >= bride["varna"] else 0.0),
        ("वश्य",2.0,vashya_score(groom["vashya"], bride["vashya"])),
        ("तारा",3.0,tara_score(groom["nakshatra_no"], bride["nakshatra_no"])),
        ("योनि",4.0,float(yoni_score(groom["nakshatra_no"], bride["nakshatra_no"]))),
        ("ग्रह मैत्री",5.0,graha_maitri_score(SIGN_LORDS[groom["moon_sign_no"]-1], SIGN_LORDS[bride["moon_sign_no"]-1])),
        ("गण",6.0,gana_score(groom["gana"], bride["gana"])),
        ("राशी",7.0,float(bhakoot_score(groom["moon_sign_no"], bride["moon_sign_no"]))),
        ("नाडी",8.0,float(nadi_score(groom["nakshatra_no"], bride["nakshatra_no"]))),
    ]
    base = sum(s for _,_,s in items)

    # Date Panchang's sample PDF explicitly documents an extra "Satkoot"
    # reference based on Nadi Pada-Vedha and Navamsha Maitri. The exact table
    # is not published in the sample, so this bonus is marked provisional.
    pada_vedha = nadi_pada_vedha(groom["nakshatra_no"],groom["pada"],bride["nakshatra_no"],bride["pada"])
    g1 = NATURAL_FRIENDSHIP[groom["moon_navamsa_lord"]][bride["moon_navamsa_lord"]]
    g2 = NATURAL_FRIENDSHIP[bride["moon_navamsa_lord"]][groom["moon_navamsa_lord"]]
    nav_ok = not (g1 == "enemy" and g2 == "enemy")
    satkoot_bonus = 3 if (not pada_vedha and nav_ok) else 0

    return {
        "kootas":[{"name":n,"max":m,"score":s} for n,m,s in items],
        "ashtakoot_total":base,
        "satkoot_bonus_provisional":satkoot_bonus,
        "reference_total_provisional":base+satkoot_bonus,
        "nadi_dosha":nadi_score(groom["nakshatra_no"],bride["nakshatra_no"]) == 0,
        "nadi_pada_vedha":pada_vedha,
        "bhakoot_dosha":bhakoot_score(groom["moon_sign_no"],bride["moon_sign_no"]) == 0
    }

def mangal(person: dict) -> dict:
    mars = person["bodies"]["मंगळ"]
    affected = {1,2,4,7,8,12}
    houses = {
        "lagna": mars["house"],
        "moon": ((mars["sign_no"] - person["bodies"]["चंद्र"]["sign_no"]) % 12) + 1,
        "venus": ((mars["sign_no"] - person["bodies"]["शुक्र"]["sign_no"]) % 12) + 1
    }
    return {
        "from_lagna": houses["lagna"] in affected,
        "from_moon": houses["moon"] in affected,
        "from_venus": houses["venus"] in affected,
        "houses": houses,
        # Date-Panchang-style primary Manglik flag is kept Lagna-based in v1;
        # Moon/Venus checks are retained as supplementary diagnostics.
        "manglik": houses["lagna"] in affected
    }

def planet_aspects(house: int, planet: str) -> list[int]:
    targets = {((house+6-1)%12)+1}
    if planet == "मंगळ":
        targets |= {((house+3-1)%12)+1, ((house+7-1)%12)+1}
    elif planet == "गुरु":
        targets |= {((house+4-1)%12)+1, ((house+8-1)%12)+1}
    elif planet == "शनि":
        targets |= {((house+2-1)%12)+1, ((house+9-1)%12)+1}
    return sorted(targets)

def graha_milan_notes(boy: dict, girl: dict, match: dict) -> list[str]:
    notes=[]
    for label, p in (("वर",boy),("वधू",girl)):
        mg = mangal(p)
        if mg["manglik"]:
            notes.append(f"{label}च्या कुंडलीत मंगळदोषासाठी १/२/४/७/८/१२ या स्थानांची तपासणी केल्यावर मंगळदोष दिसतो.")
        else:
            notes.append(f"{label}च्या कुंडलीत लग्न/चंद्र/शुक्रापासून मंगळदोषाच्या स्थानात मंगळ आढळला नाही.")
    # Jupiter's 7th aspect on the partner's 7th house is a concrete dynamic fact.
    for label, p in (("वर",boy),("वधू",girl)):
        jh=p["bodies"]["गुरु"]["house"]
        if 7 in planet_aspects(jh,"गुरु"):
            notes.append(f"{label}च्या कुंडलीत गुरुची सप्तम स्थानावर दृष्टी आहे.")
    if match["bhakoot_dosha"]:
        notes.append("राशी-कूटामध्ये पारंपरिक २/१२, ५/९ किंवा ६/८ संबंधामुळे दोष नोंदला आहे.")
    else:
        notes.append("राशी-कूटामध्ये वरील प्रमुख दोषसंबंध आढळला नाही.")
    return notes

def calculate_match(payload: dict) -> dict:
    boy = calculate_chart(payload["boy"])
    girl = calculate_chart(payload["girl"])
    match = match_charts(boy, girl)
    return {
        "settings":{
            "zodiac":"Sidereal / Nirayana",
            "ayanamsha":"Lahiri / Chitrapaksha",
            "d1_house_system":"Whole Sign",
            "bhava_chalit_working":"Placidus cusp layer (provisional; Date Panchang exact method still to be validated)",
            "timezone":"Birth-place timezone; India defaults to Asia/Kolkata",
            "engine":"Swiss Ephemeris"
        },
        "boy":boy, "girl":girl, "match":match,
        "mangal":{"boy":mangal(boy),"girl":mangal(girl)},
        "graha_milan_notes":graha_milan_notes(boy,girl,match)
    }

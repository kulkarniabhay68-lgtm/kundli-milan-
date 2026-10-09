from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import swisseph as swe


SIGNS = [
    "मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"
]

SIGN_LORDS = [
    "मंगळ", "शुक्र", "बुध", "चंद्र", "रवि", "बुध",
    "शुक्र", "मंगळ", "गुरु", "शनि", "शनि", "गुरु"
]

NAKSHATRAS = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशीर्ष",
    "आर्द्रा", "पुनर्वसू", "पुष्य", "आश्लेषा", "मघा",
    "पूर्वा फाल्गुनी", "उत्तरा फाल्गुनी", "हस्त", "चित्रा",
    "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूळ",
    "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा",
    "शतभिषा", "पूर्वाभाद्रपदा", "उत्तराभाद्रपदा", "रेवती"
]

NADI = [
    "आद्य", "मध्य", "अंत्य", "अंत्य", "मध्य", "आद्य",
    "आद्य", "मध्य", "अंत्य", "अंत्य", "मध्य", "आद्य",
    "आद्य", "मध्य", "अंत्य", "अंत्य", "मध्य", "आद्य",
    "आद्य", "मध्य", "अंत्य", "अंत्य", "मध्य", "आद्य",
    "आद्य", "मध्य", "अंत्य"
]

GANA = {
    1: "देव", 2: "मनुष्य", 3: "राक्षस", 4: "मनुष्य", 5: "देव",
    6: "मनुष्य", 7: "देव", 8: "देव", 9: "राक्षस", 10: "राक्षस",
    11: "मनुष्य", 12: "मनुष्य", 13: "देव", 14: "राक्षस",
    15: "देव", 16: "राक्षस", 17: "देव", 18: "राक्षस",
    19: "राक्षस", 20: "मनुष्य", 21: "मनुष्य", 22: "देव",
    23: "राक्षस", 24: "राक्षस", 25: "मनुष्य", 26: "मनुष्य",
    27: "देव"
}

YONI = {
    1: "अश्व", 2: "गज", 3: "मेष", 4: "सर्प", 5: "सर्प",
    6: "श्वान", 7: "मांजर", 8: "मेष", 9: "मांजर",
    10: "मूषक", 11: "मूषक", 12: "गाय", 13: "महिषी",
    14: "व्याघ्र", 15: "महिषी", 16: "व्याघ्र", 17: "हरिण",
    18: "हरिण", 19: "श्वान", 20: "वानर", 21: "नकुल",
    22: "वानर", 23: "सिंह", 24: "अश्व", 25: "सिंह",
    26: "गाय", 27: "गज"
}

PLANETS = [
    ("सूर्य", swe.SUN), ("चंद्र", swe.MOON),
    ("मंगळ", swe.MARS), ("बुध", swe.MERCURY),
    ("गुरु", swe.JUPITER), ("शुक्र", swe.VENUS),
    ("शनि", swe.SATURN), ("राहू", swe.TRUE_NODE)
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

    return f'{d:02d}° {m:02d}\' {s:02d}"'


def sign_index(lon: float) -> int:
    return int(norm360(lon) // 30) + 1


def navamsa_sign_from_longitude(lon: float) -> int:
    sign = sign_index(lon)
    pada = int((lon % 30) // (30 / 9))
    starts = {
        1: 1, 2: 10, 3: 7, 4: 4, 5: 1, 6: 10,
        7: 7, 8: 4, 9: 1, 10: 10, 11: 7, 12: 4
    }
    return ((starts[sign] - 1 + pada) % 12) + 1


def house_from_cusps(lon: float, cusps) -> int:
    x = norm360(lon)
    c = [norm360(v) for v in cusps[:12]]

    for i in range(12):
        start = c[i]
        end = c[(i + 1) % 12]
        if end <= start:
            end += 360

        xx = x if x >= start else x + 360
        if start <= xx < end:
            return i + 1

    return 12


def planet_aspects(house: int, planet: str) -> list[int]:
    """वैदिक ज्योतिषातील ग्रहांच्या दृष्टीची घरांनुसार गणना."""
    if not isinstance(house, int) or not 1 <= house <= 12:
        raise ValueError("house must be between 1 and 12")

    offsets = [6]

    if planet == "मंगळ":
        offsets.extend([3, 7])
    elif planet == "गुरु":
        offsets.extend([4, 8])
    elif planet == "शनि":
        offsets.extend([2, 9])

    return sorted({
        ((house - 1 + offset) % 12) + 1
        for offset in offsets
    })


def calculate_chart(person: dict) -> dict:
    dt = datetime.fromisoformat(
        person["date"] + "T" + person["time"]
    )
    tz = ZoneInfo(person.get("timezone", "Asia/Kolkata"))
    local = dt.replace(tzinfo=tz)
    utc = local.astimezone(ZoneInfo("UTC"))

    latitude = float(person["latitude"])
    longitude = float(person["longitude"])

    if not -90 <= latitude <= 90:
        raise ValueError("latitude -90 ते 90 दरम्यान असणे आवश्यक आहे")
    if not -180 <= longitude <= 180:
        raise ValueError("longitude -180 ते 180 दरम्यान असणे आवश्यक आहे")

    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    jd = swe.julday(
        utc.year, utc.month, utc.day, hour, swe.GREG_CAL
    )

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
            "rashi": SIGNS[sign - 1],
            "sign_no": sign,
            "retrograde": bool(xx[3] < 0)
        }

    ketu_lon = norm360(bodies["राहू"]["longitude"] + 180)
    ketu_sign = sign_index(ketu_lon)

    bodies["केतू"] = {
        "longitude": ketu_lon,
        "degree": dms(ketu_lon % 30),
        "rashi": SIGNS[ketu_sign - 1],
        "sign_no": ketu_sign,
        "retrograde": True
    }

    # D1 कुंडली: Whole Sign पद्धत
    house_result = swe.houses_ex(
        jd, latitude, longitude, b"W", swe.FLG_SIDEREAL
    )
    ascmc = house_result[1]
    asc = norm360(ascmc[0])
    asc_sign = sign_index(asc)

    # भावचलित: Placidus cusps
    chal_result = swe.houses_ex(
        jd, latitude, longitude, b"P", swe.FLG_SIDEREAL
    )
    chal_cusps = chal_result[0]

    for body in bodies.values():
        body["house"] = (
            (body["sign_no"] - asc_sign) % 12
        ) + 1
        body["bhava_chalit_house"] = house_from_cusps(
            body["longitude"], chal_cusps
        )

    moon_lon = bodies["चंद्र"]["longitude"]
    nak = int(moon_lon / (360 / 27)) + 1
    pada = int(
        (moon_lon % (360 / 27)) / ((360 / 27) / 4)
    ) + 1
    nav_sign = navamsa_sign_from_longitude(moon_lon)

    return {
        "name": person["name"],
        "date": person["date"],
        "time": person["time"],
        "place": person["place"],
        "place_display": person.get(
            "place_display", person["place"]
        ),
        "latitude": latitude,
        "longitude": longitude,
        "timezone": person.get("timezone", "Asia/Kolkata"),
        "utc": utc.isoformat(),
        "julian_day": jd,
        "lagna": {
            "longitude": asc,
            "degree": dms(asc % 30),
            "rashi": SIGNS[asc_sign - 1],
            "sign_no": asc_sign
        },
        "bodies": bodies,
        "moon_rashi": bodies["चंद्र"]["rashi"],
        "moon_sign_no": bodies["चंद्र"]["sign_no"],
        "nakshatra": NAKSHATRAS[nak - 1],
        "nakshatra_no": nak,
        "pada": pada,
        "nadi": NADI[nak - 1],
        "gana": GANA[nak],
        "yoni": YONI[nak],
        "varna": (
            4 if bodies["चंद्र"]["sign_no"] in (4, 8, 12)
            else 3 if bodies["चंद्र"]["sign_no"] in (1, 5, 9)
            else 2 if bodies["चंद्र"]["sign_no"] in (2, 6, 10)
            else 1
        ),
        "moon_navamsa_sign": SIGNS[nav_sign - 1],
        "moon_navamsa_lord": SIGN_LORDS[nav_sign - 1],
        "lagna_lord": SIGN_LORDS[asc_sign - 1],
        "sun_rashi": bodies["सूर्य"]["rashi"]
    }


def calculate_ashtakoot(boy: dict, girl: dict) -> dict:
    """अष्टकूट गुणमेलन (३६ गुणांची गणना)"""
    
    # १. वर्ण कूट (१ गुण)
    varna_points = 1 if boy["varna"] >= girl["varna"] else 0.5
    
    # २. वश्य कूट (२ गुण)
    vashya_matrix = {
        ("मेष", "सिंह"): 2, ("मेष", "वृश्चिक"): 1,
        ("वृषभ", "कर्क"): 2, ("वृषभ", "तुला"): 2,
        ("मिथुन", "कन्या"): 2,
        ("कर्क", "वृश्चिक"): 2, ("कर्क", "धनु"): 1,
        ("सिंह", "तुला"): 1,
        ("कन्या", "मीन"): 2, ("कन्या", "मिथुन"): 2,
        ("तुला", "मकर"): 2, ("तुला", "वृषभ"): 2,
        ("वृश्चिक", "कर्क"): 2,
        ("धनु", "मीन"): 2,
        ("मकर", "मेष"): 1, ("मकर", "कुंभ"): 2,
        ("कुंभ", "मेष"): 1,
        ("मीन", "मकर"): 2
    }
    vashya_score = vashya_matrix.get((boy["moon_rashi"], girl["moon_rashi"]), 0)

    # ३. तारा कूट (३ गुण)
    diff = abs(boy["nakshatra_no"] - girl["nakshatra_no"]) % 9
    tara_score = 3 if diff in [0, 2, 4, 6, 8] else (1.5 if diff in [1, 3, 5, 7] else 0)

    # ४. योनी कूट (४ गुण)
    yoni_score = 4 if boy["yoni"] == girl["yoni"] else 2

    # ५. ग्रह मैत्री (५ गुण)
    lord_boy = SIGN_LORDS[boy["moon_sign_no"] - 1]
    lord_girl = SIGN_LORDS[girl["moon_sign_no"] - 1]
    graha_score = 5 if lord_boy == lord_girl else 3

    # ६. गण कूट (६ गुण)
    g_boy, g_girl = boy["gana"], girl["gana"]
    if g_boy == g_girl:
        gana_score = 6
    elif {g_boy, g_girl} == {"देव", "मनुष्य"}:
        gana_score = 5
    elif {g_boy, g_girl} == {"मनुष्य", "राक्षस"}:
        gana_score = 1
    else:
        gana_score = 0

    # ७. भकूट कूट (७ गुण)
    b_dist = (girl["moon_sign_no"] - boy["moon_sign_no"]) % 12 + 1
    if b_dist in [1, 7, 3, 11, 4, 10]:
        bhakoot_score = 7
    else:
        bhakoot_score = 0

    # ८. नाडी कूट (८ गुण)
    nadi_score = 0 if boy["nadi"] == girl["nadi"] else 8

    total_score = varna_points + vashya_score + tara_score + yoni_score + graha_score + gana_score + bhakoot_score + nadi_score

    return {
        "total_score": round(total_score, 1),
        "details": {
            "varna": {"score": varna_points, "max": 1},
            "vashya": {"score": vashya_score, "max": 2},
            "tara": {"score": tara_score, "max": 3},
            "yoni": {"score": yoni_score, "max": 4},
            "graha_maitri": {"score": graha_score, "max": 5},
            "gana": {"score": gana_score, "max": 6},
            "bhakoot": {"score": bhakoot_score, "max": 7},
            "nadi": {"score": nadi_score, "max": 8}
        }
    }


def calculate_match(payload: dict) -> dict:
    boy = calculate_chart(payload["boy"])
    girl = calculate_chart(payload["girl"])
    
    ashtakoot = calculate_ashtakoot(boy, girl)

    boy_manglik = boy["bodies"]["मंगळ"]["house"] in {1, 2, 4, 7, 8, 12}
    girl_manglik = girl["bodies"]["मंगळ"]["house"] in {1, 2, 4, 7, 8, 12}

    return {
        "settings": {
            "zodiac": "Sidereal / Nirayana",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "d1_house_system": "Whole Sign",
            "bhava_chalit_working": "Placidus cusp layer",
            "timezone": "Birth-place timezone; India defaults to Asia/Kolkata",
            "engine": "Swiss Ephemeris"
        },
        "boy": boy,
        "girl": girl,
        "match": {
            "status": "calculated",
            "ashtakoot": ashtakoot,
            "note": "अष्टकूट गुणमेलन आणि ग्रहस्थिती यशस्वीरित्या पूर्ण झाली आहे."
        },
        "mangal": {
            "boy": {"manglik": boy_manglik, "house": boy["bodies"]["मंगळ"]["house"]},
            "girl": {"manglik": girl_manglik, "house": girl["bodies"]["मंगळ"]["house"]},
            "dosha_matched": boy_manglik == girl_manglik
        },
        "graha_milan_notes": [
            "कुंडली जुळवणी, गुणमेलन आणि मांगलिक दोष तपासणीची गणना यशस्वीरीत्या पूर्ण झाली आहे."
        ]
    }

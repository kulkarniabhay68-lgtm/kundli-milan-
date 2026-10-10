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
        res = swe.calc_ut(jd, pid, flags)
        xx = res[0]
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

    # भावचलित: Placidus cusps वेगळे ठेवले आहेत
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


def calculate_basic_kootas(boy: dict, girl: dict) -> dict:
    """वर्ण, गण, भकूट (५/९ दोषासह) आणि नाडी कूट गणना."""
    
    # १. वर्ण कूट (१ गुण)
    boy_varna = boy.get("varna", 1)
    girl_varna = girl.get("varna", 1)
    varna_score = 1.0 if boy_varna >= girl_varna else 0.0

    # २. गण कूट (६ गुण)
    boy_gana = boy.get("gana")
    girl_gana = girl.get("gana")
    
    if boy_gana == girl_gana:
        gana_score = 6.0
    elif {boy_gana, girl_gana} == {"देव", "मनुष्य"}:
        gana_score = 5.0
    elif {boy_gana, girl_gana} == {"मनुष्य", "राक्षस"}:
        gana_score = 0.0
    else:
        gana_score = 0.0

    # ३. भकूट कूट (७ गुण) - ५/९, २/१२ आणि ६/८ दोष तपासणी
    boy_sign = boy.get("moon_sign_no", 1)
    girl_sign = girl.get("moon_sign_no", 1)
    diff = ((girl_sign - boy_sign) % 12) + 1
    
    if diff in [2, 6, 8, 12, 5, 9]:
        bhakoot_score = 0.0
    else:
        bhakoot_score = 7.0

    # ४. नाडी कूट (८ गुण)
    boy_nadi = boy.get("nadi")
    girl_nadi = girl.get("nadi")
    
    if boy_nadi != girl_nadi:
        nadi_score = 8.0
    else:
        nadi_score = 0.0

    total = varna_score + gana_score + bhakoot_score + nadi_score

    return {
        "varna": {"score": varna_score, "max": 1},
        "gana": {"score": gana_score, "max": 6},
        "bhakoot": {"score": bhakoot_score, "max": 7},
        "nadi": {"score": nadi_score, "max": 8},
        "total_score": total
    }


def calculate_match(payload: dict) -> dict:
    boy = calculate_chart(payload["boy"])
    girl = calculate_chart(payload["girl"])
    
    kootas = calculate_basic_kootas(boy, girl)

    return {
        "settings": {
            "zodiac": "Sidereal / Nirayana",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "engine": "Swiss Ephemeris"
        },
        "boy": boy,
        "girl": girl,
        "ashtakoota": kootas,
        "match": {
            "status": "calculated",
            "note": "कुंडली तयार झाली आहे."
        }
    }

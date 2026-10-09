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
    def calculate_match(payload: dict) -> dict:
    boy = calculate_chart(payload["boy"])
    girl = calculate_chart(payload["girl"])

    return {
        "settings": {
            "zodiac": "Sidereal / Nirayana",
            "ayanamsha": "Lahiri / Chitrapaksha",
            "engine": "Swiss Ephemeris"
        },
        "boy": boy,
        "girl": girl,
        "match": {
            "status": "calculated",
            "note": "कुंडली तयार झाली आहे. अष्टकूट गुणमेलनाची पूर्ण गणना अद्याप जोडलेली नाही."
        }
    }

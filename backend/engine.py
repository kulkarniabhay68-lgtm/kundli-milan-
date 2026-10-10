"""
ASHTAKOOTA KUNDALI MATCHING
आठ कूटांचे पारंपरिक गुणमेलन

टीप:
गुणतक्ते आणि नक्षत्र-वर्गीकरण वापरण्यापूर्वी प्रमाणित
ज्योतिषीय स्रोताशी पडताळा. हे विवाहाच्या यशाची हमी देत नाही.
"""

from enum import Enum


# ==================================================
# 1. INPUT VALIDATION
# ==================================================

VALID_SIGNS = set(range(1, 13))
VALID_NAKSHATRAS = set(range(1, 28))


def validate_number(value, valid_values, field_name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} पूर्णांक असणे आवश्यक आहे.")
    if value not in valid_values:
        raise ValueError(f"{field_name} ची किंमत अवैध आहे: {value}")


# ==================================================
# 2. VARNA KOOTA — MAX 1
# ==================================================

class Varna(str, Enum):
    VIPRA = "विप्र"
    KSHATRIYA = "क्षत्रिय"
    VAISHYA = "वैश्य"
    SHUDRA = "शूद्र"


VARNA_ORDER = {
    Varna.VIPRA: 4,
    Varna.KSHATRIYA: 3,
    Varna.VAISHYA: 2,
    Varna.SHUDRA: 1,
}


def calculate_varna_koota(groom_varna, bride_varna):
    if not isinstance(groom_varna, Varna):
        raise ValueError("groom_varna हा Varna Enum मधील असावा.")
    if not isinstance(bride_varna, Varna):
        raise ValueError("bride_varna हा Varna Enum मधील असावा.")

    score = 1 if VARNA_ORDER[groom_varna] >= VARNA_ORDER[bride_varna] else 0

    return {
        "koota": "वर्ण",
        "groom_varna": groom_varna.value,
        "bride_varna": bride_varna.value,
        "score": score,
        "max_score": 1,
    }


# ==================================================
# 3. VASHYA KOOTA — MAX 2
# ==================================================

DEFAULT_VASHYA = {
    1: "चतुष्पाद",
    2: "चतुष्पाद",
    3: "मानव",
    4: "जलचर",
    5: "वनचर",
    6: "मानव",
    7: "मानव",
    8: "कीटक",
    9: "मानव",
    10: "चतुष्पाद",
    11: "मानव",
    12: "जलचर",
}

VASHYA_SCORE_TABLE = {
    "चतुष्पाद": {
        "चतुष्पाद": 2, "मानव": 0.5, "जलचर": 1,
        "वनचर": 2, "कीटक": 2,
    },
    "मानव": {
        "चतुष्पाद": 0.5, "मानव": 2, "जलचर": 0,
        "वनचर": 0, "कीटक": 0,
    },
    "जलचर": {
        "चतुष्पाद": 1, "मानव": 0.5, "जलचर": 2,
        "वनचर": 1, "कीटक": 1,
    },
    "वनचर": {
        "चतुष्पाद": 0, "मानव": 0, "जलचर": 2,
        "वनचर": 2, "कीटक": 0,
    },
    "कीटक": {
        "चतुष्पाद": 2, "मानव": 0, "जलचर": 1,
        "वनचर": 0, "कीटक": 2,
    },
}


def calculate_vashya_koota(
    groom_sign_no,
    bride_sign_no,
    groom_group=None,
    bride_group=None,
):
    validate_number(groom_sign_no, VALID_SIGNS, "वराची राशी")
    validate_number(bride_sign_no, VALID_SIGNS, "वधूची राशी")

    if groom_group is None:
        groom_group = DEFAULT_VASHYA[groom_sign_no]

    if bride_group is None:
        bride_group = DEFAULT_VASHYA[bride_sign_no]

    if groom_group not in VASHYA_SCORE_TABLE:
        raise ValueError("वराचा वश्य गट अवैध आहे.")

    if bride_group not in VASHYA_SCORE_TABLE:
        raise ValueError("वधूचा वश्य गट अवैध आहे.")

    score = VASHYA_SCORE_TABLE[bride_group][groom_group]

    return {
        "koota": "वश्य",
        "groom_group": groom_group,
        "bride_group": bride_group,
        "score": score,
        "max_score": 2,
    }


# ==================================================
# 4. TARA KOOTA — MAX 3
# ==================================================

AUSPICIOUS_TARAS = {1, 2, 4, 6, 8, 9}


def calculate_tara_number(from_nakshatra, to_nakshatra):
    validate_number(from_nakshatra, VALID_NAKSHATRAS, "पहिले नक्षत्र")
    validate_number(to_nakshatra, VALID_NAKSHATRAS, "दुसरे नक्षत्र")

    count = ((to_nakshatra - from_nakshatra) % 27) + 1
    remainder = count % 9

    return remainder if remainder else 9


def calculate_tara_koota(groom_nakshatra_no, bride_nakshatra_no):
    validate_number(groom_nakshatra_no, VALID_NAKSHATRAS, "वराचे नक्षत्र")
    validate_number(bride_nakshatra_no, VALID_NAKSHATRAS, "वधूचे नक्षत्र")

    groom_tara = calculate_tara_number(
        bride_nakshatra_no, groom_nakshatra_no
    )
    bride_tara = calculate_tara_number(
        groom_nakshatra_no, bride_nakshatra_no
    )

    groom_good = groom_tara in AUSPICIOUS_TARAS
    bride_good = bride_tara in AUSPICIOUS_TARAS

    if groom_good and bride_good:
        score = 3
    elif groom_good or bride_good:
        score = 1.5
    else:
        score = 0

    return {
        "koota": "तारा",
        "groom_tara": groom_tara,
        "bride_tara": bride_tara,
        "score": score,
        "max_score": 3,
    }


# ==================================================
# 5. YONI KOOTA — MAX 4
# ==================================================

YONI_BY_NAKSHATRA = {
    1: "अश्व", 2: "गज", 3: "मेष", 4: "सर्प",
    5: "सर्प", 6: "श्वान", 7: "मार्जार", 8: "मेष",
    9: "मार्जार", 10: "मूषक", 11: "मूषक", 12: "गाय",
    13: "महिषी", 14: "व्याघ्र", 15: "महिषी", 16: "व्याघ्र",
    17: "हरिण", 18: "हरिण", 19: "श्वान", 20: "वानर",
    21: "मुंगूस", 22: "वानर", 23: "सिंह", 24: "अश्व",
    25: "सिंह", 26: "गाय", 27: "गज",
}

YONI_SCORE_TABLE = {
    "अश्व": {"अश्व":4,"गज":2,"मेष":2,"सर्प":3,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":0,"व्याघ्र":2,"हरिण":3,"वानर":3,"मुंगूस":2,"सिंह":2},
    "गज": {"अश्व":2,"गज":4,"मेष":3,"सर्प":3,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":3,"व्याघ्र":2,"हरिण":2,"वानर":3,"मुंगूस":2,"सिंह":0},
    "मेष": {"अश्व":2,"गज":3,"मेष":4,"सर्प":2,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":3,"महिषी":3,"व्याघ्र":2,"हरिण":2,"वानर":0,"मुंगूस":2,"सिंह":2},
    "सर्प": {"अश्व":3,"गज":3,"मेष":2,"सर्प":4,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":2,"व्याघ्र":2,"हरिण":2,"वानर":2,"मुंगूस":0,"सिंह":3},
    "श्वान": {"अश्व":2,"गज":2,"मेष":2,"सर्प":2,"श्वान":4,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":2,"व्याघ्र":2,"हरिण":0,"वानर":2,"मुंगूस":2,"सिंह":2},
    "मार्जार": {"अश्व":2,"गज":2,"मेष":2,"सर्प":3,"श्वान":2,"मार्जार":4,"मूषक":0,"गाय":2,"महिषी":2,"व्याघ्र":2,"हरिण":2,"वानर":2,"मुंगूस":2,"सिंह":2},
    "मूषक": {"अश्व":2,"गज":2,"मेष":2,"सर्प":3,"श्वान":2,"मार्जार":0,"मूषक":4,"गाय":2,"महिषी":2,"व्याघ्र":2,"हरिण":2,"वानर":2,"मुंगूस":2,"सिंह":2},
    "गाय": {"अश्व":2,"गज":2,"मेष":3,"सर्प":2,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":4,"महिषी":2,"व्याघ्र":0,"हरिण":2,"वानर":2,"मुंगूस":2,"सिंह":2},
    "महिषी": {"अश्व":0,"गज":3,"मेष":3,"सर्प":2,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":4,"व्याघ्र":2,"हरिण":2,"वानर":2,"मुंगूस":2,"सिंह":2},
    "व्याघ्र": {"अश्व":2,"गज":2,"मेष":2,"सर्प":2,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":0,"महिषी":2,"व्याघ्र":4,"हरिण":2,"वानर":2,"मुंगूस":2,"सिंह":2},
    "हरिण": {"अश्व":3,"गज":2,"मेष":2,"सर्प":2,"श्वान":0,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":2,"व्याघ्र":2,"हरिण":4,"वानर":3,"मुंगूस":2,"सिंह":2},
    "वानर": {"अश्व":3,"गज":3,"मेष":0,"सर्प":2,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":2,"व्याघ्र":2,"हरिण":3,"वानर":4,"मुंगूस":2,"सिंह":2},
    "मुंगूस": {"अश्व":2,"गज":2,"मेष":2,"सर्प":0,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":2,"व्याघ्र":2,"हरिण":2,"वानर":2,"मुंगूस":4,"सिंह":2},
    "सिंह": {"अश्व":2,"गज":0,"मेष":2,"सर्प":3,"श्वान":2,"मार्जार":2,"मूषक":2,"गाय":2,"महिषी":2,"व्याघ्र":2,"हरिण":2,"वानर":2,"मुंगूस":2,"सिंह":4},
}


def calculate_yoni_koota(groom_nakshatra_no, bride_nakshatra_no):
    validate_number(groom_nakshatra_no, VALID_NAKSHATRAS, "वराचे नक्षत्र")
    validate_number(bride_nakshatra_no, VALID_NAKSHATRAS, "वधूचे नक्षत्र")

    groom_yoni = YONI_BY_NAKSHATRA[groom_nakshatra_no]
    bride_yoni = YONI_BY_NAKSHATRA[bride_nakshatra_no]
    score = YONI_SCORE_TABLE[bride_yoni][groom_yoni]

    return {
        "koota": "योनी",
        "groom_yoni": groom_yoni,
        "bride_yoni": bride_yoni,
        "score": score,
        "max_score": 4,
    }


# ==================================================
# 6. GRAHA MAITRI KOOTA — MAX 5
# ==================================================

SIGN_LORDS = {
    1: "मंगळ", 2: "शुक्र", 3: "बुध", 4: "चंद्र",
    5: "रवि", 6: "बुध", 7: "शुक्र", 8: "मंगळ",
    9: "गुरु", 10: "शनि", 11: "शनि", 12: "गुरु",
}

GRAHA_MAITRI_SCORE_TABLE = {
    1: [5,3,1.5,4,5,1.5,3,5,5,1.5,1.5,5],
    2: [3,5,5,1.5,0,5,5,3,1.5,5,5,1.5],
    3: [1.5,5,5,3,4,5,5,1,4,5,4,1.5],
    4: [4,1.5,1,5,5,1,1.5,4,4,1,1.5,4],
    5: [5,0,4,5,5,4,0,5,5,4,4,5],
    6: [1.5,5,5,1,4,5,5,3,4,5,4,1.5],
    7: [3,5,5,1.5,0,5,5,3,1.5,5,5,1.5],
    8: [5,3,1.5,4,5,1.5,3,5,5,1.5,1.5,5],
    9: [5,1.5,1.5,4,5,1.5,1.5,4,5,1.5,1.5,4],
    10: [1.5,5,4,1.5,0,4,5,1.5,0,4,4,1.5],
    11: [1.5,5,4,1.5,0,4,5,1.5,0,4,4,1.5],
    12: [5,1.5,1.5,4,5,1.5,1.5,4,4,1.5,1.5,5],
}


def calculate_graha_maitri_koota(groom_sign_no, bride_sign_no):
    validate_number(groom_sign_no, VALID_SIGNS, "वराची राशी")
    validate_number(bride_sign_no, VALID_SIGNS, "वधूची राशी")

    score = GRAHA_MAITRI_SCORE_TABLE[bride_sign_no][groom_sign_no - 1]

    return {
        "koota": "ग्रहमैत्री",
        "groom_lord": SIGN_LORDS[groom_sign_no],
        "bride_lord": SIGN_LORDS[bride_sign_no],
        "score": score,
        "max_score": 5,
    }


# ==================================================
# 7. GANA KOOTA — MAX 6
# ==================================================

GANA_BY_NAKSHATRA = {
    1:"देव", 2:"मनुष्य", 3:"राक्षस", 4:"मनुष्य", 5:"देव",
    6:"मनुष्य", 7:"देव", 8:"देव", 9:"राक्षस", 10:"राक्षस",
    11:"मनुष्य", 12:"मनुष्य", 13:"मनुष्य", 14:"राक्षस",
    15:"देव", 16:"राक्षस", 17:"देव", 18:"राक्षस",
    19:"राक्षस", 20:"मनुष्य", 21:"मनुष्य", 22:"देव",
    23:"राक्षस", 24:"राक्षस", 25:"मनुष्य", 26:"मनुष्य",
    27:"देव",
}

GANA_SCORE_TABLE = {
    "देव": {"देव": 6, "मनुष्य": 5, "राक्षस": 1},
    "मनुष्य": {"देव": 5, "मनुष्य": 6, "राक्षस": 0},
    "राक्षस": {"देव": 1, "मनुष्य": 0, "राक्षस": 6},
}


def calculate_gana_koota(groom_nakshatra_no, bride_nakshatra_no):
    validate_number(groom_nakshatra_no, VALID_NAKSHATRAS, "वराचे नक्षत्र")
    validate_number(bride_nakshatra_no, VALID_NAKSHATRAS, "वधूचे नक्षत्र")

    groom_gana = GANA_BY_NAKSHATRA[groom_nakshatra_no]
    bride_gana = GANA_BY_NAKSHATRA[bride_nakshatra_no]
    score = GANA_SCORE_TABLE[bride_gana][groom_gana]

    return {
        "koota": "गण",
        "groom_gana": groom_gana,
        "bride_gana": bride_gana,
        "score": score,
        "max_score": 6,
    }


# ==================================================
# 8. BHAKOOT KOOTA — MAX 7
# ==================================================

BHAKOOT_UNFAVORABLE_PAIRS = {
    (2, 12),
    (5, 9),
    (6, 8),
}


def calculate_bhakoot_koota(groom_sign_no, bride_sign_no):
    validate_number(groom_sign_no, VALID_SIGNS, "वराची राशी")
    validate_number(bride_sign_no, VALID_SIGNS, "वधूची राशी")

    forward = ((bride_sign_no - groom_sign_no) % 12) + 1
    backward = ((groom_sign_no - bride_sign_no) % 12) + 1
    pair = tuple(sorted((forward, backward)))

    unfavorable = pair in BHAKOOT_UNFAVORABLE_PAIRS
    score = 0 if unfavorable else 7

    return {
        "koota": "भकूट",
        "groom_sign_no": groom_sign_no,
        "bride_sign_no": bride_sign_no,
        "distance_pair": pair,
        "unfavorable_pair": unfavorable,
        "score": score,
        "max_score": 7,
        "parihara_status": "तपासणी आवश्यक" if unfavorable else "मूलभूत नियमात दोष दिसत नाही",
    }


# ==================================================
# 9. NADI KOOTA — MAX 8
# ==================================================

NADI_BY_NAKSHATRA = {
    1:"आदि", 2:"मध्य", 3:"अंत्य", 4:"अंत्य", 5:"मध्य",
    6:"आदि", 7:"आदि", 8:"मध्य", 9:"अंत्य", 10:"अंत्य",
    11:"मध्य", 12:"आदि", 13:"आदि", 14:"मध्य", 15:"अंत्य",
    16:"अंत्य", 17:"मध्य", 18:"आदि", 19:"आदि", 20:"मध्य",
    21:"अंत्य", 22:"मध्य", 23:"मध्य", 24:"आदि",
    25:"आदि", 26:"मध्य", 27:"अंत्य",
}


def calculate_nadi_koota(groom_nakshatra_no, bride_nakshatra_no):
    validate_number(groom_nakshatra_no, VALID_NAKSHATRAS, "वराचे नक्षत्र")
    validate_number(bride_nakshatra_no, VALID_NAKSHATRAS, "वधूचे नक्षत्र")

    groom_nadi = NADI_BY_NAKSHATRA[groom_nakshatra_no]
    bride_nadi = NADI_BY_NAKSHATRA[bride_nakshatra_no]
    same_nadi = groom_nadi == bride_nadi

    return {
        "koota": "नाडी",
        "groom_nadi": groom_nadi,
        "bride_nadi": bride_nadi,
        "score": 0 if same_nadi else 8,
        "max_score": 8,
        "nadi_dosha_indicated": same_nadi,
        "parihara_status": "तपासणी आवश्यक" if same_nadi else "मूलभूत नियमात समान नाडी नाही",
    }


# ==================================================
# 10. COMPLETE ASHTAKOOTA MATCHING
# ==================================================

def calculate_ashtakoota_milan(
    groom_sign_no,
    bride_sign_no,
    groom_nakshatra_no,
    bride_nakshatra_no,
    groom_varna,
    bride_varna,
    groom_vashya_group=None,
    bride_vashya_group=None,
):
    kootas = [
        calculate_varna_koota(groom_varna, bride_varna),
        calculate_vashya_koota(
            groom_sign_no, bride_sign_no,
            groom_vashya_group, bride_vashya_group
        ),
        calculate_tara_koota(groom_nakshatra_no, bride_nakshatra_no),
        calculate_yoni_koota(groom_nakshatra_no, bride_nakshatra_no),
        calculate_graha_maitri_koota(groom_sign_no, bride_sign_no),
        calculate_gana_koota(groom_nakshatra_no, bride_nakshatra_no),
        calculate_bhakoot_koota(groom_sign_no, bride_sign_no),
        calculate_nadi_koota(groom_nakshatra_no, bride_nakshatra_no),
    ]

    total_score = round(sum(item["score"] for item in kootas), 2)
    max_score = sum(item["max_score"] for item in kootas)

    if max_score != 36:
        raise RuntimeError("कमाल गुण ३६ असणे आवश्यक आहे.")

    if not 0 <= total_score <= 36:
        raise RuntimeError("एकूण गुण ० ते ३६ दरम्यान असणे आवश्यक आहे.")

    return {
        "kootas": kootas,
        "total_score": total_score,
        "max_score": 36,
        "is_suitable_by_score_only": total_score >= 18,
        "warnings": [
            "गुणतक्ते व नक्षत्र-वर्गीकरण प्रमाणित स्रोताशी पडताळा.",
            "भकूट आणि नाडी परिहाराचे सविस्तर नियम लागू केलेले नाहीत.",
            "गुणांवरूनच विवाहाचा अंतिम निर्णय घेऊ नये.",
        ],
    }


# ==================================================
# 11. TABLE STRUCTURE CHECK
# ==================================================

def validate_ashtakoota_tables():
    assert len(YONI_BY_NAKSHATRA) == 27
    assert len(GANA_BY_NAKSHATRA) == 27
    assert len(NADI_BY_NAKSHATRA) == 27
    assert len(GRAHA_MAITRI_SCORE_TABLE) == 12

    for sign_no in range(1, 13):
        assert len(GRAHA_MAITRI_SCORE_TABLE[sign_no]) == 12

    for yoni in YONI_SCORE_TABLE:
        assert len(YONI_SCORE_TABLE[yoni]) == 14

    assert sum([1, 2, 3, 4, 5, 6, 7, 8]) == 36

    return "तक्त्यांची मूलभूत रचना तपासली."


# ==================================================
# 12. APP IMPORT COMPATIBILITY WRAPPER
# ==================================================

def calculate_match(groom_data, bride_data):
    """
    backend/app.py मधील import त्रुटी दूर करण्यासाठी 
    आणि मुख्य अष्टकूट गुणमेलन कॉल करण्यासाठी मुख्य फंक्शन.
    """
    groom_v = groom_data.get("varna", Varna.KSHATRIYA)
    if isinstance(groom_v, str):
        try:
            groom_v = Varna(groom_v)
        except ValueError:
            groom_v = Varna.KSHATRIYA

    bride_v = bride_data.get("varna", Varna.VAISHYA)
    if isinstance(bride_v, str):
        try:
            bride_v = Varna(bride_v)
        except ValueError:
            bride_v = Varna.VAISHYA

    return calculate_ashtakoota_milan(
        groom_sign_no=groom_data.get("sign_no"),
        bride_sign_no=bride_data.get("sign_no"),
        groom_nakshatra_no=groom_data.get("nakshatra_no"),
        bride_nakshatra_no=bride_data.get("nakshatra_no"),
        groom_varna=groom_v,
        bride_varna=bride_v,
        groom_vashya_group=groom_data.get("vashya_group"),
        bride_vashya_group=bride_data.get("vashya_group"),
    )


# ==================================================
# 13. EXAMPLE — RUN THIS FILE DIRECTLY
# ==================================================

if __name__ == "__main__":
    print(validate_ashtakoota_tables())

    result = calculate_ashtakoota_milan(
        groom_sign_no=1,
        bride_sign_no=7,
        groom_nakshatra_no=1,
        bride_nakshatra_no=15,
        groom_varna=Varna.KSHATRIYA,
        bride_varna=Varna.VAISHYA,
    )

    print("\nअष्टकूट गुणमेलन")
    print("--------------------")

    for item in result["kootas"]:
        print(
            f'{item["koota"]}: '
            f'{item["score"]}/{item["max_score"]}'
        )

    print("--------------------")
    print(f'एकूण गुण: {result["total_score"]}/36')
    print(f'१८ किंवा अधिक गुण: {result["is_suitable_by_score_only"]}')

    print("\nसूचना:")
    for warning in result["warnings"]:
        print("-", warning)

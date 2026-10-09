# कुंडली मिलन — Calculation Engine v1

हा प्रकल्प सध्याच्या `कुंडली मेलन` UI ला calculation backend जोडतो.

## काय तयार केले आहे

- जन्मस्थळ autocomplete backend (`/api/geocode`)
- निवडलेल्या गाव/शहराचे latitude + longitude save
- Swiss Ephemeris + Lahiri/Chitrapaksha sidereal calculation
- D1 Whole Sign Lagna/Rashi chart
- Moon Rashi, Nakshatra, Pada, Nadi, Gana, Yoni, Varna, Vashya
- सूर्य, चंद्र, मंगळ, बुध, गुरु, शुक्र, शनि, राहू, केतू positions
- 8-koota Ashtakoot score
- Mangal check from Lagna/Moon/Venus
- Bhava Chalit working layer (सध्या Placidus cusp layer; Date Panchang exact method अजून validate करायचा आहे)
- A4 PDF report (ग्रहस्थिती तपशीलचा स्वतंत्र भाग नाही)
- Review मधील `ऑर्डर सबमिट` वरून थेट PDF उघडतो; extra report webpage नाही.

## Date Panchang reference

दिलेल्या sample PDF मध्ये:
- वर/वधूचे coordinates दाखवले आहेत
- नक्षत्र + चरण, नाडी, योनि, गण, चंद्रराशी, लग्नराशी, रविराशीचे नवांश स्वामी इ. दाखवले आहेत
- अष्टकूटानंतर `सत्कूट` नावाने अतिरिक्त गुणांचा reference आहे
- ग्रहमेलनात मंगळदोष, भावचिलत स्थिती, ग्रहदृष्टी, लग्नेश/सप्तमेश इ. वापरले आहेत

त्या अतिरिक्त `सत्कूट`चे पूर्ण scoring table sample मध्ये प्रकाशित नाही. त्यामुळे code मध्ये तो **provisional reference** म्हणून स्वतंत्र ठेवला आहे; त्याला final "दाते पंचांग exact" असे घोषित केलेले नाही.

## Run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

नंतर browser मध्ये:
`http://localhost:8000`

## Production

Commercial deployment करण्यापूर्वी Swiss Ephemeris / pysweph licensing तपासा. `pysweph` च्या सध्याच्या PyPI package मध्ये AGPL licensing नमूद आहे; closed-source commercial deployment साठी योग्य commercial license आवश्यक असू शकतो.

## पुढील validation

दाते पंचांगच्या किमान 20–50 reference cases वर:
- Lagna
- Moon Rashi
- Nakshatra + Pada
- ग्रह degrees
- Ashtakoot
- Satkoot
- Bhava Chalit
- Mangal
- final conclusion

तुलना करून configuration lock करणे आवश्यक आहे.

"""Append new interface keys to all three dictionaries together (keeps key parity).

New Tamil and Hindi strings are drafts, like all the others (blueprint I18N-13).
Usage: python scripts/add_i18n_keys.py
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "i18n"

NEW = {
    "state.not_built": (
        "Not built yet",
        "இன்னும் உருவாக்கப்படவில்லை",
        "अभी बनाया नहीं गया",
    ),
    "app.skeleton_notice": (
        "Preview skeleton: layout only, no data yet.",
        "முன்னோட்ட அமைப்பு: வடிவமைப்பு மட்டுமே, இன்னும் தரவு இல்லை.",
        "प्रीव्यू ढाँचा: केवल लेआउट, अभी कोई डेटा नहीं।",
    ),
    "page.data.gaps_title": (
        "Standing data gaps",
        "நிலையான தரவு இடைவெளிகள்",
        "स्थायी डेटा अंतराल",
    ),
    "page.data.original_english": ("Original English", "ஆங்கில மூலம்", "अंग्रेज़ी मूल"),
    "page.data.translation_status": (
        "Translation status",
        "மொழிபெயர்ப்பு நிலை",
        "अनुवाद की स्थिति",
    ),
    "page.data.assumptions_title": (
        "Assumptions in effect",
        "நடைமுறையில் உள்ள அனுமானங்கள்",
        "लागू मान्यताएँ",
    ),
    "page.data.datasets_title": ("Datasets", "தரவுத்தொகுப்புகள்", "डेटासेट"),
    "status.draft": (
        "Draft (not yet reviewed)",
        "வரைவு (இன்னும் மதிப்பாய்வு செய்யப்படவில்லை)",
        "मसौदा (अभी समीक्षा नहीं हुई)",
    ),
    "status.reviewed": ("Reviewed", "மதிப்பாய்வு செய்யப்பட்டது", "समीक्षित"),
    "table.dataset": ("Dataset", "தரவுத்தொகுப்பு", "डेटासेट"),
    "table.licence": ("Licence note", "உரிமக் குறிப்பு", "लाइसेंस नोट"),
    "table.type": ("Type", "வகை", "प्रकार"),
    "table.parameter": ("Parameter", "அளவுரு", "पैरामीटर"),
    "table.value": ("Value", "மதிப்பு", "मान"),
    "page.route.title": ("Route explorer", "வழித்தட ஆய்வு", "मार्ग अन्वेषक"),
    # PHASE 2: map card
    "map.flood_layer": ("Flood layer", "வெள்ள அடுக்கு", "बाढ़ परत"),
    "map.roads_layer": (
        "Roads (current OpenStreetMap)",
        "சாலைகள் (தற்போதைய OpenStreetMap)",
        "सड़कें (वर्तमान OpenStreetMap)",
    ),
    "map.zone": ("Study zone", "ஆய்வுப் பகுதி", "अध्ययन क्षेत्र"),
    "map.loading": ("Loading map data...", "வரைபடத் தரவு ஏற்றப்படுகிறது...", "मानचित्र डेटा लोड हो रहा है..."),
    "map.error": (
        "Map data could not be loaded. Run python scripts/build_phase2.py.",
        "வரைபடத் தரவை ஏற்ற முடியவில்லை. python scripts/build_phase2.py ஐ இயக்கவும்.",
        "मानचित्र डेटा लोड नहीं हो सका। python scripts/build_phase2.py चलाएँ।",
    ),
    "map.tiles_note": (
        "Basemap labels stay in the map provider's language.",
        "அடிப்படை வரைபடத்தின் பெயர்கள் வரைபட வழங்குநரின் மொழியிலேயே இருக்கும்.",
        "बेसमैप के लेबल मानचित्र प्रदाता की भाषा में ही रहते हैं।",
    ),
    "map.attribution": (
        "Flood layers: OpenCity (Oorvani Foundation), Greater Chennai Corporation, NRSC. Roads: OpenStreetMap contributors.",
        "வெள்ள அடுக்குகள்: OpenCity (Oorvani Foundation), பெருநகர சென்னை மாநகராட்சி, NRSC. சாலைகள்: OpenStreetMap பங்களிப்பாளர்கள்.",
        "बाढ़ परतें: OpenCity (Oorvani Foundation), ग्रेटर चेन्नई कॉर्पोरेशन, NRSC. सड़कें: OpenStreetMap योगदानकर्ता।",
    ),
    "map.area_stats": (
        "{area} km2 flooded of {zone} km2 ({pct})",
        "{zone} ச.கி.மீ-இல் {area} ச.கி.மீ வெள்ளத்தில் ({pct})",
        "{zone} वर्ग किमी में से {area} वर्ग किमी बाढ़ग्रस्त ({pct})",
    ),
    "map.roads_note": (
        "Roads are today's roads, not 2015 roads.",
        "சாலைகள் இன்றைய சாலைகள்; 2015 சாலைகள் அல்ல.",
        "सड़कें आज की सड़कें हैं, 2015 की नहीं।",
    ),
}

for i, lang in enumerate(("en", "ta", "hi")):
    path = D / f"{lang}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    added = 0
    for key, values in NEW.items():
        if key not in data:
            data[key] = values[i]
            added += 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(lang, "added", added, "total", len(data) - 1)

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
    # PHASE 7: KPI cards and charts
    "kpi.not_routed": (
        "The observed layer is a map composite and is not routed on. Choose mild, moderate or severe.",
        "கவனிக்கப்பட்ட அடுக்கு வரைபடக் கூட்டுத் தொகுப்பு மட்டுமே; அதில் வழித்தடம் கணக்கிடப்படவில்லை. இலேசான, மிதமான அல்லது கடுமையானதைத் தேர்ந்தெடுக்கவும்.",
        "प्रेक्षित परत केवल एक मानचित्र संयोजन है और उस पर मार्ग की गणना नहीं की गई है। हल्का, मध्यम या गंभीर चुनें।",
    ),
    "kpi.note_time": (
        "mean of {n} origins, max {max} min",
        "{n} தொடக்கப் புள்ளிகளின் சராசரி, அதிகபட்சம் {max} நிமிடம்",
        "{n} आरंभ बिंदुओं का औसत, अधिकतम {max} मिनट",
    ),
    "kpi.note_time_none": (
        "no origin has both a drivable conventional route and a flood-aware route",
        "எந்தத் தொடக்கப் புள்ளிக்கும் ஓட்டக்கூடிய வழக்கமான வழியும் வெள்ளம் அறிந்த வழியும் இல்லை",
        "किसी आरंभ बिंदु के पास चलने योग्य पारंपरिक मार्ग और बाढ़-जागरूक मार्ग दोनों नहीं हैं",
    ),
    "kpi.note_feasibility": (
        "of conventional routes cross a blocked road",
        "வழக்கமான வழித்தடங்கள் தடுக்கப்பட்ட சாலையைக் கடக்கின்றன",
        "पारंपरिक मार्ग अवरुद्ध सड़क से गुजरते हैं",
    ),
    "kpi.note_reach": (
        "{n} of {total} origins reach a facility",
        "{total} தொடக்கப் புள்ளிகளில் {n} ஒரு வசதியை அடைகின்றன",
        "{total} में से {n} आरंभ बिंदु किसी सुविधा तक पहुँचते हैं",
    ),
    "kpi.note_coverage": (
        "within {min} min; conventional {conv}",
        "{min} நிமிடத்திற்குள்; வழக்கமான {conv}",
        "{min} मिनट के भीतर; पारंपरिक {conv}",
    ),
    "kpi.note_robust": (
        "{pct} changed their facility in at least one run ({runs} runs)",
        "{runs} ஓட்டங்களில் குறைந்தது ஒன்றில் {pct} தங்கள் வசதியை மாற்றின",
        "{runs} रन में से कम से कम एक में {pct} ने अपनी सुविधा बदली",
    ),
    "chart.conventional": ("Conventional", "வழக்கமான", "पारंपरिक"),
    "chart.flood_aware": ("Flood-aware", "வெள்ளம் அறிந்த", "बाढ़-जागरूक"),
    "chart.share_origins": ("Share of sample origins", "மாதிரித் தொடக்கப் புள்ளிகளின் பங்கு", "नमूना आरंभ बिंदुओं का हिस्सा"),
    "chart.segments": ("{n} road segments", "{n} சாலைப் பகுதிகள்", "{n} सड़क खंड"),
    "chart.no_origins": ("No origin has a flood-aware route.", "எந்தத் தொடக்கப் புள்ளிக்கும் வெள்ளம் அறிந்த வழி இல்லை.", "किसी आरंभ बिंदु के लिए बाढ़-जागरूक मार्ग नहीं है।"),
    "chart.origin_col": ("Origin", "தொடக்கப் புள்ளி", "आरंभ बिंदु"),
    "chart.extra_col": ("Extra minutes", "கூடுதல் நிமிடங்கள்", "अतिरिक्त मिनट"),
    "chart.status_col": ("Status", "நிலை", "स्थिति"),
    "chart.cut_off": ("Cut off", "துண்டிக்கப்பட்டது", "कटा हुआ"),
    "chart.detour": ("Detour needed", "மாற்றுப்பாதை தேவை", "चक्कर आवश्यक"),
    "chart.same_route": ("Same route", "அதே வழி", "वही मार्ग"),
    "state.planned_not_built": ("Planned, not built", "திட்டமிடப்பட்டது, இன்னும் கட்டப்படவில்லை", "योजनाबद्ध, अभी बनाया नहीं गया"),
    "state.metrics_missing": (
        "Metrics file not found. Run python scripts/build_metrics.py.",
        "அளவீட்டுக் கோப்பு கிடைக்கவில்லை. python scripts/build_metrics.py ஐ இயக்கவும்.",
        "मेट्रिक्स फ़ाइल नहीं मिली। python scripts/build_metrics.py चलाएँ।",
    ),
    "note.indicative_metrics": (
        "Indicative simulation results on a proxy facility list and simulated origins; not predictions.",
        "மாதிரி வசதிப் பட்டியல் மற்றும் உருவகப்படுத்தப்பட்ட தொடக்கப் புள்ளிகளின் அடிப்படையிலான சுட்டிக்காட்டும் உருவகப்படுத்துதல் முடிவுகள்; கணிப்புகள் அல்ல.",
        "प्रॉक्सी सुविधा सूची और सिम्युलेटेड आरंभ बिंदुओं पर संकेतात्मक सिमुलेशन परिणाम; पूर्वानुमान नहीं।",
    ),
    # PHASE 9: route explorer and explanation text
    "expl.reachable_same": (
        "The nearest reachable facility offering {service} is {facility}, {time} minutes away, the same as the conventional route.",
        "{service} வழங்கும் அருகிலுள்ள அடையக்கூடிய வசதி {facility}; {time} நிமிடத் தொலைவு, வழக்கமான வழித்தடத்திற்கு இணையானது.",
        "{service} देने वाली निकटतम पहुँच योग्य सुविधा {facility} है, {time} मिनट दूर, पारंपरिक मार्ग के बराबर।",
    ),
    "expl.unreachable_facilities": (
        "{k} facility(ies) cannot be reached: {names}.",
        "{k} வசதி(கள்) அடைய முடியாதவை: {names}.",
        "{k} सुविधा(एँ) पहुँच योग्य नहीं हैं: {names}।",
    ),
    "expl.status": (
        "Facility status: {status}. Flood layer: {kind}, source {source}.",
        "வசதியின் நிலை: {status}. வெள்ள அடுக்கு: {kind}, மூலம் {source}.",
        "सुविधा की स्थिति: {status}। बाढ़ परत: {kind}, स्रोत {source}।",
    ),
    "reason.NO_PATH_AFTER_FLOODING": (
        "no road path remains after flooding",
        "வெள்ளத்திற்குப் பிறகு சாலை வழி எதுவும் இல்லை",
        "बाढ़ के बाद कोई सड़क मार्ग नहीं बचा",
    ),
    "reason.ORIGIN_CUT_OFF": ("the start point is cut off", "தொடக்கப் புள்ளி துண்டிக்கப்பட்டது", "आरंभ बिंदु कट गया है"),
    "route.pick_origin": (
        "Choose a start (all simulated)",
        "தொடக்கப் புள்ளியைத் தேர்ந்தெடுக்கவும் (அனைத்தும் உருவகப்படுத்தப்பட்டவை)",
        "आरंभ बिंदु चुनें (सभी सिम्युलेटेड)",
    ),
    "route.group_starts": ("Ambulance starts (simulated)", "ஆம்புலன்ஸ் தொடக்கங்கள் (உருவகப்படுத்தப்பட்டவை)", "एम्बुलेंस आरंभ (सिम्युलेटेड)"),
    "route.group_origins": ("Sample origins (simulated)", "மாதிரித் தொடக்கப் புள்ளிகள் (உருவகப்படுத்தப்பட்டவை)", "नमूना आरंभ बिंदु (सिम्युलेटेड)"),
    "route.chosen": ("Chosen facility", "தேர்ந்தெடுக்கப்பட்ட வசதி", "चुनी गई सुविधा"),
    "route.time_fa": ("Flood-aware time", "வெள்ளம் அறிந்த நேரம்", "बाढ़-जागरूक समय"),
    "route.time_conv": ("Conventional time", "வழக்கமான நேரம்", "पारंपरिक समय"),
    "route.difference": ("Difference", "வேறுபாடு", "अंतर"),
    "route.drivable": ("Conventional route drivable", "வழக்கமான வழித்தடம் ஓட்டத்தக்கது", "पारंपरिक मार्ग चलने योग्य"),
    "route.yes": ("Yes", "ஆம்", "हाँ"),
    "route.no": ("No", "இல்லை", "नहीं"),
    "route.none": ("None", "எதுவும் இல்லை", "कोई नहीं"),
    "route.explanation": ("Why this route", "இந்த வழித்தடம் ஏன்", "यह मार्ग क्यों"),
    "route.unreachable_title": ("Unreachable facilities", "அடைய முடியாத வசதிகள்", "अप्राप्य सुविधाएँ"),
    "route.legend_blocked": ("Blocked on conventional route", "வழக்கமான வழித்தடத்தில் தடுக்கப்பட்டது", "पारंपरिक मार्ग पर अवरुद्ध"),
    "route.legend_facility": ("Facility", "வசதி", "सुविधा"),
    "route.legend_start": ("Start (simulated)", "தொடக்கம் (உருவகப்படுத்தப்பட்டது)", "आरंभ (सिम्युलेटेड)"),
    "route.verification": ("Verification", "சரிபார்ப்பு", "सत्यापन"),
    "route.minutes_value": ("{n} min", "{n} நிமிடம்", "{n} मिनट"),
    "state.routes_missing": (
        "Route file not found. Run python scripts/build_routes.py.",
        "வழித்தடக் கோப்பு கிடைக்கவில்லை. python scripts/build_routes.py ஐ இயக்கவும்.",
        "मार्ग फ़ाइल नहीं मिली। python scripts/build_routes.py चलाएँ।",
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

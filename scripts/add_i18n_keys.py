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
    # PHASE 8, metrics table and export pages
    "iso.unit": ("Zone", "மண்டலம்", "क्षेत्र"),
    "iso.basis": ("Population basis", "மக்கள்தொகை அடிப்படை", "जनसंख्या आधार"),
    "iso.basis_placeholder": ("Placeholder", "தற்காலிக மதிப்பு", "प्लेसहोल्डर"),
    "iso.isolated_share": ("Isolated share of road nodes", "தனிமைப்படுத்தப்பட்ட சாலை முனைகளின் பங்கு", "अलग-थलग सड़क नोड का हिस्सा"),
    "iso.delayed_share": ("Delayed share", "தாமதமான பங்கு", "विलंबित हिस्सा"),
    "iso.people_col": ("Share of sample points (not people)", "மாதிரிப் புள்ளிகளின் பங்கு (மக்கள் அல்ல)", "नमूना बिंदुओं का हिस्सा (लोग नहीं)"),
    "iso.score": ("Priority score", "முன்னுரிமை மதிப்பெண்", "प्राथमिकता स्कोर"),
    "iso.top_by_scenario": ("Top five zones by scenario", "சூழ்நிலை வாரியாக முதல் ஐந்து மண்டலங்கள்", "परिदृश्य के अनुसार शीर्ष पाँच क्षेत्र"),
    "iso.rank_change": ("Change versus the previous scenario", "முந்தைய சூழ்நிலையுடன் ஒப்பிடும் மாற்றம்", "पिछले परिदृश्य की तुलना में बदलाव"),
    "iso.new_in_top": ("new", "புதிது", "नया"),
    "iso.units_note": (
        "Zones are 1 km grid cells because ward boundaries and populations were not loaded. Every zone has the same placeholder weight, so the ranking follows the share of road nodes cut off, not people.",
        "வார்டு எல்லைகளும் மக்கள்தொகையும் ஏற்றப்படாததால் மண்டலங்கள் 1 கி.மீ கட்டக் கூறுகள். ஒவ்வொரு மண்டலத்திற்கும் ஒரே தற்காலிக எடை; எனவே தரவரிசை மக்களை அல்ல, துண்டிக்கப்பட்ட சாலை முனைகளின் பங்கைப் பின்பற்றுகிறது.",
        "वार्ड सीमाएँ और जनसंख्या लोड नहीं की गईं, इसलिए क्षेत्र 1 किमी ग्रिड सेल हैं। हर क्षेत्र का प्लेसहोल्डर भार समान है, इसलिए रैंकिंग लोगों की नहीं, कटे हुए सड़क नोड के हिस्से की है।",
    ),
    "iso.legend_rank": ("Number = rank among the top {k}", "எண் = முதல் {k} இடையிலான தரவரிசை", "संख्या = शीर्ष {k} में रैंक"),
    "iso.excluded_baseline": (
        "{n} road nodes are excluded because they cannot reach any facility even without flooding.",
        "வெள்ளம் இல்லாவிட்டாலும் எந்த வசதியையும் அடைய முடியாததால் {n} சாலை முனைகள் விலக்கப்பட்டன.",
        "{n} सड़क नोड बाहर रखे गए क्योंकि वे बाढ़ के बिना भी किसी सुविधा तक नहीं पहुँच सकते।",
    ),
    "iso.limits_title": ("Limits of this view", "இந்தக் காட்சியின் வரம்புகள்", "इस दृश्य की सीमाएँ"),
    "iso.limit1": ("Node share is a proxy for streets and area, not for people; a single dead-end node counts as one node.", "முனைப் பங்கு தெருக்கள் மற்றும் பரப்பளவின் தோராயம் மட்டுமே, மக்கள் அல்ல; ஒரு முட்டுச்சந்து முனையும் ஒரு முனையாகக் கணக்கிடப்படும்.", "नोड का हिस्सा सड़कों और क्षेत्र का अनुमान है, लोगों का नहीं; एक बंद सिरे वाला नोड भी एक नोड गिना जाता है।"),
    "iso.limit2": ("Population is not loaded, so every zone has the same placeholder weight.", "மக்கள்தொகை ஏற்றப்படவில்லை; எனவே ஒவ்வொரு மண்டலத்திற்கும் ஒரே தற்காலிக எடை.", "जनसंख्या लोड नहीं है, इसलिए हर क्षेत्र का भार समान प्लेसहोल्डर है।"),
    "iso.limit3": ("Scenarios are simulated subsets of flood reports; the ranking is not a forecast.", "சூழ்நிலைகள் வெள்ளப் பதிவுகளின் உருவகப்படுத்தப்பட்ட உட்தொகுப்புகள்; தரவரிசை முன்னறிவிப்பு அல்ல.", "परिदृश्य बाढ़ रिपोर्टों के सिम्युलेटेड उपसमूह हैं; रैंकिंग पूर्वानुमान नहीं है।"),
    "iso.limit4": ("Nodes already disconnected without flooding are excluded, so very poorly connected areas may be under-reported.", "வெள்ளம் இல்லாமலேயே துண்டிக்கப்பட்ட முனைகள் விலக்கப்படுகின்றன; எனவே மிகக் குறைவாக இணைக்கப்பட்ட பகுதிகள் குறைத்துக் காட்டப்படலாம்.", "बाढ़ के बिना भी कटे हुए नोड बाहर रखे गए हैं, इसलिए बहुत कम जुड़े क्षेत्रों की स्थिति कम दिख सकती है।"),
    "iso.limit5": ("Rankings change between scenarios, and the comparison above shows the change.", "சூழ்நிலைகளுக்கிடையே தரவரிசை மாறும்; மேலே உள்ள ஒப்பீடு அந்த மாற்றத்தைக் காட்டுகிறது.", "परिदृश्यों के बीच रैंकिंग बदलती है, और ऊपर की तुलना यह बदलाव दिखाती है।"),
    "metrics.title": ("Metrics by scenario", "சூழ்நிலை வாரியாக அளவீடுகள்", "परिदृश्य के अनुसार मेट्रिक्स"),
    "metrics.col_metric": ("Metric", "அளவீடு", "मेट्रिक"),
    "metrics.m1_mean": ("Travel-time increase, mean (min)", "பயண நேர அதிகரிப்பு, சராசரி (நிமிடம்)", "यात्रा समय में वृद्धि, औसत (मिनट)"),
    "metrics.m1_median": ("Travel-time increase, median (min)", "பயண நேர அதிகரிப்பு, இடைநிலை (நிமிடம்)", "यात्रा समय में वृद्धि, माध्यिका (मिनट)"),
    "metrics.m1_max": ("Travel-time increase, maximum (min)", "பயண நேர அதிகரிப்பு, அதிகபட்சம் (நிமிடம்)", "यात्रा समय में वृद्धि, अधिकतम (मिनट)"),
    "metrics.m1_n": ("Origins included in the increase", "அதிகரிப்பில் சேர்க்கப்பட்ட தொடக்கப் புள்ளிகள்", "वृद्धि में शामिल आरंभ बिंदु"),
    "metrics.m2_false": ("Conventional routes crossing a blocked road", "தடுக்கப்பட்ட சாலையைக் கடக்கும் வழக்கமான வழித்தடங்கள்", "अवरुद्ध सड़क से गुजरने वाले पारंपरिक मार्ग"),
    "metrics.m2_fa": ("Origins with a flood-aware route", "வெள்ளம் அறிந்த வழித்தடம் உள்ள தொடக்கப் புள்ளிகள்", "बाढ़-जागरूक मार्ग वाले आरंभ बिंदु"),
    "metrics.m3_any": ("Origins reaching at least one facility", "குறைந்தது ஒரு வசதியை அடையும் தொடக்கப் புள்ளிகள்", "कम से कम एक सुविधा तक पहुँचने वाले आरंभ बिंदु"),
    "metrics.m3_fac": ("Origins reaching {facility}", "{facility} ஐ அடையும் தொடக்கப் புள்ளிகள்", "{facility} तक पहुँचने वाले आरंभ बिंदु"),
    "metrics.m4_conv": ("Coverage within {min} min, conventional", "{min} நிமிடத்திற்குள் உள்ளடக்கம், வழக்கமான", "{min} मिनट के भीतर कवरेज, पारंपरिक"),
    "metrics.m4_fa": ("Coverage within {min} min, flood-aware", "{min} நிமிடத்திற்குள் உள்ளடக்கம், வெள்ளம் அறிந்த", "{min} मिनट के भीतर कवरेज, बाढ़-जागरूक"),
    "metrics.m4_diff": ("Coverage difference (percentage points)", "உள்ளடக்க வேறுபாடு (சதவீதப் புள்ளிகள்)", "कवरेज अंतर (प्रतिशत अंक)"),
    "metrics.m5_overall": ("Routing robustness (same facility across runs)", "வழித்தட உறுதித்தன்மை (ஓட்டங்களில் அதே வசதி)", "मार्ग मजबूती (रन में वही सुविधा)"),
    "metrics.m5_changed": ("Origins whose facility changed in at least one run", "குறைந்தது ஒரு ஓட்டத்தில் வசதி மாறிய தொடக்கப் புள்ளிகள்", "कम से कम एक रन में सुविधा बदलने वाले आरंभ बिंदु"),
    "metrics.note": (
        "Sample of {n} simulated origins, {runs} robustness runs. Coverage is a share of sample points, not of people. Indicative simulation, not a prediction.",
        "{n} உருவகப்படுத்தப்பட்ட தொடக்கப் புள்ளிகளின் மாதிரி, {runs} உறுதித்தன்மை ஓட்டங்கள். உள்ளடக்கம் மாதிரிப் புள்ளிகளின் பங்கு, மக்களின் பங்கு அல்ல. சுட்டிக்காட்டும் உருவகப்படுத்துதல், முன்னறிவிப்பு அல்ல.",
        "{n} सिम्युलेटेड आरंभ बिंदुओं का नमूना, {runs} मजबूती रन। कवरेज नमूना बिंदुओं का हिस्सा है, लोगों का नहीं। संकेतात्मक सिमुलेशन, पूर्वानुमान नहीं।",
    ),
    "export.intro": (
        "Files use English column names and include the interface language. They describe simulation results, not predictions.",
        "கோப்புகள் ஆங்கிலப் பத்தித் தலைப்புகளைப் பயன்படுத்துகின்றன; இடைமுக மொழியையும் சேர்க்கின்றன. அவை உருவகப்படுத்துதல் முடிவுகளை விவரிக்கின்றன, முன்னறிவிப்புகளை அல்ல.",
        "फ़ाइलें अंग्रेज़ी कॉलम नामों का उपयोग करती हैं और इंटरफ़ेस भाषा शामिल करती हैं। वे सिमुलेशन परिणाम बताती हैं, पूर्वानुमान नहीं।",
    ),
    "export.metrics_csv": ("Metrics table (CSV)", "அளவீட்டு அட்டவணை (CSV)", "मेट्रिक्स तालिका (CSV)"),
    "export.facilities_csv": ("Facilities with verification status (CSV)", "சரிபார்ப்பு நிலையுடன் வசதிகள் (CSV)", "सत्यापन स्थिति के साथ सुविधाएँ (CSV)"),
    "export.isolation_csv": ("Isolation ranking, all scenarios (CSV)", "தனிமைப்படுத்தல் தரவரிசை, அனைத்து சூழ்நிலைகள் (CSV)", "अलगाव रैंकिंग, सभी परिदृश्य (CSV)"),
    "export.audit_json": ("Audit log for the current scenario and the chosen start (JSON)", "தற்போதைய சூழ்நிலைக்கும் தேர்ந்த தொடக்கத்திற்குமான தணிக்கைப் பதிவு (JSON)", "वर्तमान परिदृश्य और चुने आरंभ का ऑडिट लॉग (JSON)"),
    "export.not_available": ("Not available for the observed composite: choose a simulated scenario.", "கவனிக்கப்பட்ட கூட்டுத் தொகுப்புக்குக் கிடைக்காது: உருவகப்படுத்தப்பட்ட சூழ்நிலையைத் தேர்ந்தெடுக்கவும்.", "प्रेक्षित संयोजन के लिए उपलब्ध नहीं: सिम्युलेटेड परिदृश्य चुनें।"),
    "export.failed": ("The file could not be created. Run the build scripts listed in the README.", "கோப்பை உருவாக்க முடியவில்லை. README இல் உள்ள உருவாக்கச் சிறுநிரல்களை இயக்கவும்.", "फ़ाइल नहीं बन सकी। README में दी गई बिल्ड स्क्रिप्ट चलाएँ।"),
    # PHASE 8b: ward populations
    "iso.units_note_wards": (
        "Units are Chennai's 155 wards (2008 boundaries) clipped to the study zone. Populations are Census 2011, assumed evenly spread inside each ward and scaled to the part of the ward inside the zone. Estimates are indicative.",
        "அலகுகள் சென்னையின் 155 வார்டுகள் (2008 எல்லைகள்), ஆய்வுப் பகுதிக்குள் வெட்டப்பட்டவை. மக்கள்தொகை 2011 கணக்கெடுப்பு; ஒவ்வொரு வார்டிலும் சீராகப் பரவியுள்ளதாகக் கருதி, வார்டின் ஆய்வுப் பகுதிக்குள் உள்ள பகுதிக்கு ஏற்ப அளவிடப்பட்டது. மதிப்பீடுகள் சுட்டிக்காட்டுபவை மட்டுமே.",
        "इकाइयाँ चेन्नई के 155 वार्ड (2008 सीमाएँ) हैं, जो अध्ययन क्षेत्र तक काटे गए हैं। जनसंख्या 2011 की जनगणना की है, हर वार्ड में समान रूप से फैली मानी गई और वार्ड के क्षेत्र के भीतर वाले हिस्से के अनुसार घटाई गई। अनुमान केवल संकेतात्मक हैं।",
    ),
    "iso.limit2_wards": (
        "Population is Census 2011 (old), assumed evenly spread inside each ward; it is not where people are during a flood.",
        "மக்கள்தொகை 2011 கணக்கெடுப்பு (பழையது); ஒவ்வொரு வார்டிலும் சீராகப் பரவியுள்ளதாகக் கருதப்படுகிறது; வெள்ளத்தின்போது மக்கள் இருக்கும் இடம் இதுவல்ல.",
        "जनसंख्या 2011 की जनगणना की है (पुरानी), हर वार्ड में समान रूप से फैली मानी गई है; बाढ़ के समय लोग जहाँ होते हैं, यह वह नहीं है।",
    ),
    "iso.basis_census": ("Census 2011, scaled to the study zone", "2011 கணக்கெடுப்பு, ஆய்வுப் பகுதிக்கு ஏற்ப அளவிடப்பட்டது", "2011 की जनगणना, अध्ययन क्षेत्र के अनुसार घटाई गई"),
    "metrics.note_weighted": (
        "Sample of {n} simulated origins, {runs} robustness runs. Coverage weights each origin by the Census 2011 population of its ward (scaled to the study zone), so it is an indicative share of people in the sample wards, not of the whole city. Not a prediction.",
        "{n} உருவகப்படுத்தப்பட்ட தொடக்கப் புள்ளிகளின் மாதிரி, {runs} உறுதித்தன்மை ஓட்டங்கள். உள்ளடக்கம் ஒவ்வொரு தொடக்கப் புள்ளியையும் அதன் வார்டின் 2011 மக்கள்தொகையால் (ஆய்வுப் பகுதிக்கு ஏற்ப அளவிடப்பட்டது) எடையிடுகிறது; எனவே இது மாதிரி வார்டுகளில் உள்ள மக்களின் சுட்டிக்காட்டும் பங்கு, முழு நகரத்தினுடையது அல்ல. முன்னறிவிப்பு அல்ல.",
        "{n} सिम्युलेटेड आरंभ बिंदुओं का नमूना, {runs} मजबूती रन। कवरेज हर आरंभ बिंदु को उसके वार्ड की 2011 जनगणना जनसंख्या (अध्ययन क्षेत्र के अनुसार घटाई गई) से भारित करता है, इसलिए यह नमूना वार्डों के लोगों का संकेतात्मक हिस्सा है, पूरे शहर का नहीं। पूर्वानुमान नहीं।",
    ),
    "state.audit_missing": (
        "Audit file not found. Run python scripts/build_audit.py.",
        "தணிக்கைக் கோப்பு கிடைக்கவில்லை. python scripts/build_audit.py ஐ இயக்கவும்.",
        "ऑडिट फ़ाइल नहीं मिली। python scripts/build_audit.py चलाएँ।",
    ),
    "route.audit_hint": (
        "The log lists the selection, every assumption in effect, datasets, flood layer, facilities, result, metrics and limits. It is a JSON file in English.",
        "இந்தப் பதிவு தேர்வு, நடைமுறையிலுள்ள அனைத்து அனுமானங்கள், தரவுத்தொகுப்புகள், வெள்ள அடுக்கு, வசதிகள், முடிவு, அளவீடுகள் மற்றும் வரம்புகளைப் பட்டியலிடுகிறது. இது ஆங்கிலத்தில் உள்ள JSON கோப்பு.",
        "यह लॉग चयन, लागू सभी धारणाएँ, डेटासेट, बाढ़ परत, सुविधाएँ, परिणाम, मेट्रिक्स और सीमाएँ सूचीबद्ध करता है। यह अंग्रेज़ी में JSON फ़ाइल है।",
    ),
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

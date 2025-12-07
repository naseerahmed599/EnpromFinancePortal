"""
Cost Center Parser Utility
Intelligently parses cost center codes and enriches them with project and category information
"""

PROJECTS = {
    "290000": {"name": "Zukünftige Projekte", "description": "Zukünftige Projekte"},
    "250348": {"name": "Hamburg", "description": "Isolatorenketten_Seiltausch_Hamburg"},
    "250107": {"name": "", "description": "Flb_Abs.1 Borken-Gießen Nord"},
    "250042": {
        "name": "Neuenhagen Marzahn",
        "description": "Isolatorenwechsel (Los 3+4) und LWL-Wechsel (Los 1+2)",
    },
    "250041": {
        "name": "Kleine Enercon Projekte",
        "description": "Kleine Enercon Projekte - Interne Controlling Nummer je Projekt",
    },
    "244912": {
        "name": "Kettenwechselprojekte 2025_26",
        "description": "Kettenwechselprojekte 2025_26",
    },
    "244725": {"name": "UW Görries", "description": "UW Görries"},
    "244092": {
        "name": "UW Schwerte",
        "description": "110kV – Freileitungsanbindung Schwerte",
    },
    "243846": {"name": "Montage 8DA10", "description": "Montage 8DA10"},
    "242175": {"name": "UW Himmelreich", "description": "UW Himmelreich"},
    "242025": {"name": "UW Siedenbrünzow", "description": "UW_Siedenbrünzow"},
    "241978": {
        "name": "MW_Abz_Vorb_HT0005 Güs-Schu_M.65",
        "description": "Mastwechsel_Abz_Vorb_HT0005 Güs-Schu_M.65",
    },
    "241968": {
        "name": "MW_Abz_Neubb.-Glock._HT0105 Grl-Nbr M.128",
        "description": "Mastwechsel_Abz_Neubb.-Glock._HT0105 Grl-Nbr M.128",
    },
    "241958": {
        "name": "Mastwech._HT0105 Grl-Nbr Mast 12",
        "description": "Mastwechel_HT0105 Grl-Nbr Mast 12",
    },
    "241796": {"name": "UW Semlin", "description": "Umrüstung UW Semlin"},
    "241525": {"name": "UW Melsdorf", "description": "UW_Melsdorf"},
    "241418": {"name": "IEE -Pl. temp. 110_Kabelplanung", "description": ""},
    "241058": {
        "name": "Planungsarbeiten UW Nitzahn",
        "description": "110-kV-Freileitung Kirchmöser - Wustermark Mast 38 neu WA4-8 A1/11/J UW Nitzahn",
    },
    "241048": {
        "name": "Planungsarbeiten UW Heiligengrabe-Halenbeck",
        "description": "110-kV-Freileitung Perleberg - Wittstock Mast 126 neu WA5-4 JD-10-21 UW Heiligengrabe-Halenbeck",
    },
    "241038": {
        "name": "Planungsarbeiten UW Wiesenhagen",
        "description": "110-kV-Freileitung Thyrow - Luckenwalde Mast 31 neu WA5-0 JD-10-21 UW Wiesenhagen",
    },
    "241028": {
        "name": "Planungsarbeiten UW Walsleben-Paalzow",
        "description": "110-kV-Freileitung Neuruppin - Perleberg Mast 45 neu WA4-8 JE-09-21 UW Walsleben-Paalzow",
    },
    "240965": {"name": "UW_Jesow", "description": "240965 UW_Jesow (d. Lindenhof)"},
    "240958": {
        "name": "Berechnung Erdseilspitze LH-13-167A",
        "description": "Berechnung Erdseilspitze LH-13-167A",
    },
    "240908": {
        "name": "Planungsarbeiten Neuenhagen - Rüdersdorf - Fürstenwalde",
        "description": "110-kV-Ltg. Neuenhagen - Rüdersdorf - Fürstenwalde (HT-2121) inkl. Abzweig Heidekrug HAT-2030",
    },
    "240391": {"name": "Einbindung UW Kisdorf", "description": "Einbindung UW Kisdorf"},
    "240381": {
        "name": "Planung 110-kV-Freileitung U400 ARCELOR",
        "description": "Planung 110-kV-Freileitung U400 ARCELOR",
    },
    "240315": {"name": "UW Zernitz", "description": "UW Zernitz"},
    "240305": {"name": "UW Satzkorn", "description": "UW Satzkorn"},
    "235571": {
        "name": "Planungsarbeiten UW Granzow West",
        "description": "110-KV-Freileitung Neuruppin - Perleberg Mast 187 neu WA4-8 JE-09 UW Granzow West",
    },
    "235561": {
        "name": "Planungsarbeiten UW Kränzlin West",
        "description": "110-KV-Freileitung Neuruppin - Perleberg Mast 24 neu W8 JE-09 UW Kränzlin West",
    },
    "235551": {
        "name": "Planungsarbeiten UW Bergsdorf",
        "description": "110-KV-Freileitung Gransee Mast 21 Mast 19 neu WA4-8 JE-09 UW Bergsdorf",
    },
    "234108": {
        "name": "Planungsarbeiten UW Bosau Mast 56N",
        "description": "Planungsarbeiten UW Bosau Mast 56N",
    },
    "234011": {
        "name": "Stade-Landesbergen",
        "description": "Stade-Landesbergen PFA-4 Sottrum-Verden",
    },
    "233802": {
        "name": "Wahle Hattorf Helmstedt",
        "description": "Wahle-Hattorf-Helmstedt",
    },
    "231295": {"name": "UW Brahlstorf", "description": "UW Brahlstorf"},
    "230672": {
        "name": "Planungsarbeiten Kruckel - Dauersberg",
        "description": "Planungsarbeiten Kruckel - Dauersberg",
    },
    "230652": {
        "name": "Harvarie Badingen-Buch",
        "description": "Seilmontage 380-kV-Ltg. Ats-Nhg-Gse-Mow 479",
    },
    "223861": {
        "name": "Twistetal-Borken",
        "description": "380kV FB Twistetal-Borken Abschnitt 1",
    },
    "223815": {
        "name": "UW Klein Süstedt",
        "description": "Errichtung Wind UW Klein Süstedt- WP Klein Süstedt",
    },
    "223588": {"name": "Neom", "description": "Neom"},
    "222841": {"name": "Technische Unterstützung 110-kV-Leitungen", "description": ""},
    "222831": {
        "name": "Technische Unterstützung 110-380-kV-Leitungen",
        "description": "",
    },
    "222765": {"name": "UW Bokel", "description": "UW Bokel"},
    "222190": {
        "name": "Inspektionsflugs Stade-Landesbergen, Abschnitt 1",
        "description": "Inspektionsflugs Stade-Landesbergen, Abschnitt 1",
    },
    "222180": {
        "name": "Inspektionsflug Husum - Klixbüll, Abschnitt 4",
        "description": "Inspektionsflug A 300 WKL Husum - Klixbüll Abschnitt 4",
    },
    "221918": {"name": "Vermessung", "description": ""},
    "221908": {
        "name": "Nachtrassierung HS-Ltg",
        "description": "Nachtrassierung HS-Ltg",
    },
    "221461": {
        "name": "Pulgar Vieselbach",
        "description": "FB 380 kV Pulgar-Vieselbach (Abschnitt Mitte)",
    },
    "221451": {"name": "Röhrsdorf Weida", "description": "Röhrsdorf-Weida-Remptendorf"},
    "220770": {
        "name": "UAV Inspections of OHL",
        "description": "UAV Inspections of OHL",
    },
    "212502": {
        "name": "Helmstedt Wolmirstedt",
        "description": "Erdseilklemmenwechsel RZ West 380-kV-Ltg. He-Wol; Wol-Fö; JsN-Fö",
    },
    "212322": {
        "name": "Ragow-Streumen",
        "description": "Wechsel Tempergussklemmen auf der 380-kV-Ltg. Ragow-Streumen 561/562",
    },
    "211121": {"name": "Mehrum Nord", "description": "Einschleifung UW Mehrum Nord"},
    "210902": {
        "name": "Alfstedt",
        "description": "Einschleifung UW Alfstedt in die 380-kV",
    },
    "210762": {
        "name": "Stade Landesbergen",
        "description": "Seilnebenarbeiten in Stade 380kV Stade-Landesbergen",
    },
    "210351": {
        "name": "Parchim Süd Perleberg",
        "description": "FB 380-kV Parchim Süd-Perleberg",
    },
    "202832": {
        "name": "Wahle Mecklar",
        "description": "380-kV-Leitung Wahle-Mecklar - Seilzugarbeiten Baulos A3",
    },
    "202642": {"name": "Güstrow", "description": "Masterhöhung UW Güstrow"},
    "202632": {
        "name": "Iso- und Armaturentausch 493/494 Los 1 + Los 2",
        "description": "Iso- und Armaturentausch 493/494 Los 1 + Los 2",
    },
    "202621": {
        "name": "Audorf",
        "description": "BEK Provisorium Ersatzneubau UW Audorf",
    },
    "202102": {
        "name": "Erdseilklemmenwechsel an 380-kV-Leitungen",
        "description": "Erdseilklemmenwechsel an 380-kV-Leitungen",
    },
    "201432": {
        "name": "Krajnik Vierraden",
        "description": "Iso-Armaturentausch 507/508  Krajnik Vierraden",
    },
    "200742": {
        "name": "Wol-Tb-Wu",
        "description": "Iso- u. Armaturenwechsel Wol-Tb-Wu",
    },
    "200741": {"name": "Umrüstung Umspannwerk Testweg 4", "description": ""},
    "200542": {
        "name": "Nordring Berlin, östlicher Teilabschnit",
        "description": "Freileitungsbau 380-kV-Nordring Berlin, östlicher Teilabschnit",
    },
    "200532": {
        "name": "Erfurt",
        "description": "Kettenwechsel u. Stegetausch 220-kV Vieselbach -Wolkramshausen 367/368",
    },
    "200000": {"name": "Diverse Projekte", "description": "Diverse Projekte"},
    "191462": {
        "name": "Isowechsel 380-kV-Ltg. Jessen/Nord",
        "description": "Isowechsel 380-kV-Ltg. Jessen/Nord- Lauchstädt 499/500/504",
    },
    "190802": {
        "name": "Iso und Stegetausch 220kV Vis-Wk",
        "description": "Iso und Stegetausch 220kV Vis-Wk 367-368",
    },
}

COST_CENTER_CATEGORIES = {
    "9901": "Entsorgung",
    "9900": "Andere",
    "9700": "Finanzierung",
    "9103": "Stillstand Machinen",
    "9102": "Stillstand Monteure",
    "9101": "Stillstand Bauleitung",
    "9100": "Stillstand",
    "1199": "Demontage Sonstiges",
    "1104": "Demontage Entsorgung",
    "1103": "Fundamentdemontage",
    "1102": "Mastdemontage",
    "1101": "Seildemontage",
    "1100": "Demontage",
    "1000": "Kreuzungssicherung",
    "0900": "Provisorien",
    "0899": "Seilzug Sonstiges",
    "0804": "Rollenleinsystem",
    "0803": "Erdseil, LWL",
    "0802": "Leiterseil",
    "0801": "Abankerung der Masten",
    "0800": "Seilzug",
    "0799": "Mastbau Sonstiges",
    "0709": "Latchway/Highstep",
    "0704": "Stahlsanierung",
    "0703": "Mastverstärkung",
    "0702": "Stocken",
    "0701": "Vormontage",
    "0700": "Mastbau",
    "0699": "Fundamente Sonstige",
    "0603": "Mastfußmontage und -ausrichtung",
    "0602": "Tiefengründung",
    "0601": "Platten- & Stufenfundament",
    "0600": "Fundamente",
    "0502": "Schwerer Wegebau",
    "0501": "Leichter Wegebau",
    "0500": "Wegebau",
    "0499": "Baustelle Sonstiges",
    "0403": "Baustelleneinrichtung",
    "0402": "Bauleiter",
    "0401": "Projektleitung",
    "0400": "Baustelleneinrichtung Allgemein",
    "0300": "Technische Dokumentation",
    "0200": "Konstruktion / Design",
}

SGA_COST_CENTERS = {
    "550602": "SG&A - Bauausführungen / Site Construction - Bauabteilung",
    "550601": "SG&A - Bauausführungen / Site Construction - Monteure",
    "550600": "SG&A - Bauausführungen / Site Construction",
    "550500": "SG&A - Recht / Legal",
    "550400": "SG&A - Vertrieb / Sales",
    "550300": "SG&A - Projekte / Project",
    "550200": "SG&A - Finanzen / Finance",
    "550100": "SG&A - Verwaltung / Administration",
    "550000": "SG&A - Geschäftsführung / Executive board",
    "9999": "Sammelkostenstelle (Ausnahme) / Cost collection (Exception)",
}


def parse_cost_center(cost_center_str):
    """
    Parse a cost center string and return enriched information

    Args:
        cost_center_str: Cost center string (can be 6 or 10 digits)

    Returns:
        dict with keys:
            - original: original string
            - project_id: extracted project ID (if applicable)
            - project_name: project name from lookup
            - cost_center_id: extracted cost center ID (if applicable)
            - cost_center_category: cost center category name
            - type: 'project_with_cc', 'project_only', 'sga', 'unknown'
            - display_name: formatted display name
    """
    if not cost_center_str:
        return {
            "original": "",
            "project_id": None,
            "project_name": None,
            "cost_center_id": None,
            "cost_center_category": None,
            "type": "unknown",
            "display_name": "Unknown",
        }

    cc_str = str(cost_center_str).strip().replace("_", "")

    result = {
        "original": cost_center_str,
        "project_id": None,
        "project_name": None,
        "cost_center_id": None,
        "cost_center_category": None,
        "type": "unknown",
        "display_name": str(cost_center_str),
    }

    if len(cc_str) == 6 and (cc_str.startswith("55") or cc_str == "9999"):
        result["type"] = "sga"
        result["cost_center_id"] = cc_str
        result["cost_center_category"] = SGA_COST_CENTERS.get(cc_str, "SG&A - Unknown")
        result["display_name"] = result["cost_center_category"]
        return result

    if len(cc_str) == 10:
        project_id = cc_str[:6]
        cc_id = cc_str[6:]

        result["type"] = "project_with_cc"
        result["project_id"] = project_id
        result["cost_center_id"] = cc_id

        if project_id in PROJECTS:
            proj_info = PROJECTS[project_id]
            result["project_name"] = proj_info["name"] or proj_info["description"]
        else:
            result["project_name"] = f"Project {project_id}"

        result["cost_center_category"] = COST_CENTER_CATEGORIES.get(
            cc_id, f"CC-{cc_id}"
        )

        result["display_name"] = (
            f"{result['project_name']} → {result['cost_center_category']}"
        )
        return result

    if len(cc_str) == 6:
        result["type"] = "project_only"
        result["project_id"] = cc_str

        if cc_str in PROJECTS:
            proj_info = PROJECTS[cc_str]
            result["project_name"] = proj_info["name"] or proj_info["description"]
            result["display_name"] = result["project_name"]
        else:
            result["project_name"] = f"Project {cc_str}"
            result["display_name"] = result["project_name"]

        return result

    # Unknown format
    result["display_name"] = f"Unknown: {cost_center_str}"
    return result


def enrich_cost_center_data(data_list):
    """
    Enrich a list of records with parsed cost center information

    Args:
        data_list: List of dicts containing 'costCenter' key

    Returns:
        List of dicts with added keys: parsed_cc, project_name, cost_center_category
    """
    enriched = []
    for record in data_list:
        enriched_record = record.copy()
        cc_value = record.get("costCenter", "")
        parsed = parse_cost_center(cc_value)
        enriched_record["parsed_cc"] = parsed
        enriched_record["project_name"] = parsed["project_name"]
        enriched_record["cost_center_category"] = parsed["cost_center_category"]
        enriched_record["cc_display_name"] = parsed["display_name"]
        enriched_record["cc_type"] = parsed["type"]
        enriched.append(enriched_record)
    return enriched

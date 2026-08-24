DIVISION_MASTER = {
    "430001": "City Division",
    "430002": "Yadgir",
    "430003": "Div-I",
    "430004": "Div-II",
    "430005": "Bidar",
    "430006": "Humnabad",
    "430014": "Sedam",
    "430017": "Shorapur"
}


DIVISION_ALIASES = {
    "division-i": "430003",
    "division-ii": "430004",
    "div 1": "430003",
    "div 2": "430004"
}


def resolve_division(division):

    value = str(division).strip()

    # ---------------------------------------------
    # 1. Direct Division Code
    # ---------------------------------------------

    if value in DIVISION_MASTER:

        return {
            "success": True,
            "division_code": value,
            "division_name": DIVISION_MASTER[value],
            "resolution_type": "direct_code"
        }


    # ---------------------------------------------
    # 2. Official Division Name
    # ---------------------------------------------

    for code, name in DIVISION_MASTER.items():

        if value.lower() == name.lower():

            return {
                "success": True,
                "division_code": code,
                "division_name": name,
                "resolution_type": "official_name"
            }


    # ---------------------------------------------
    # 3. Known Division Alias
    # ---------------------------------------------

    normalized_value = value.lower()

    if normalized_value in DIVISION_ALIASES:

        code = DIVISION_ALIASES[normalized_value]

        return {
            "success": True,
            "division_code": code,
            "division_name": DIVISION_MASTER[code],
            "resolution_type": "alias"
        }


    # ---------------------------------------------
    # 4. Unable to Resolve
    # ---------------------------------------------

    return {
        "success": False,
        "error_type": "unresolved_division",
        "message": f"Unable to resolve division: {value}"
    }
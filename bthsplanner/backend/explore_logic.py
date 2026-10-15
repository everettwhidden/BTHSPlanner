from data.courses import COURSE_CATALOG, MAJORS

from .helpers import grade_badges


def filter_explore_catalog(
    query: str,
    order: str,
    grades: list[str],
    majors: list[str],
    filters: list[str],
    period_lengths: list[str],
    semesters: list[str],
) -> list[dict]:
    query = query.lower().strip()
    results = []

    for name, data in COURSE_CATALOG.items():
        if query not in name.lower() and query not in data.get("description", "").lower():
            continue

        badges = grade_badges(
            data.get("is_elective", False),
            data.get("grades", []),
            data.get("available_grades", []),
        )

        # picking both Elective and Non-elective is the same as picking neither
        if len(filters) == 1:
            wants_elective = filters[0] == "Elective"
            if data.get("is_elective", False) != wants_elective:
                continue

        if grades and not any(g in badges for g in grades):
            continue

        if majors:
            in_major = any(
                name in MAJORS.get(m, {}).get("Junior", [])
                or name in MAJORS.get(m, {}).get("Senior", [])
                for m in majors
            )
            if not in_major:
                continue

        if period_lengths:
            periods = data.get("periods", 1)
            label = "1 period" if periods == 1 else f"{periods} periods"
            if label not in period_lengths:
                continue

        if semesters:
            sems = data.get("semesters", 2)
            label = "1 semester" if sems == 1 else f"{sems} semesters"
            if label not in semesters:
                continue

        results.append({
            "name": name,
            "description": data.get("description", ""),
            "periods": data.get("periods", 1),
            "semesters": data.get("semesters", 2),
            "credits": f"{float(data.get('credits', 1.0)):.1f}",
            "is_elective": data.get("is_elective", False),
            "disabled": False,
            "grade_badges": badges,
        })

    if order == "A-Z":
        results.sort(key=lambda c: c["name"].lower())

    return results
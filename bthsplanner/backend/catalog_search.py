from data.courses import COURSE_CATALOG, language_opts

from .constants import AP_LOTES, PHYSICS_MAJOR_SN_COURSES
from .helpers import grade_badges

YEARS = ["Freshman", "Sophomore", "Junior", "Senior"]
MAX_PERIODS = 10
AP_LIMIT = 3


def search_electives(
    query: str,
    grade: str,
    major: str,
    language_base: str,
    lang_is_accelerated: bool,
    chose_economics_jr: bool,
    took_ap_calc_bc_junior: bool,
    courses_by_year: dict[str, set],
    current_periods: int,
    ap_count: int,
) -> list[dict]:
    """Courses the student can add in the search popup for one year.

    Pure function: everything it needs comes in as arguments, so it can be
    tested without starting the app. courses_by_year maps each year to the
    set of courses already in that year's plan. current_periods and ap_count
    are for the year being looked at.
    """
    query = query.lower().strip()
    grade = grade.strip()

    # everything already in the plan, and everything taken before this year
    active_courses = set().union(*courses_by_year.values())
    prior_years = set()
    for yr in YEARS[:3]:
        if yr == grade:
            break
        prior_years |= courses_by_year[yr]

    available_headroom = MAX_PERIODS - current_periods
    ap_limit_reached = ap_count >= AP_LIMIT

    results = []
    for name, data in COURSE_CATALOG.items():
        is_lang_opt = name in language_opts

        # language I's aren't flagged as electives, so let them through separately
        if not (data.get("is_elective", False) or is_lang_opt):
            continue
        if name in active_courses and not data.get("allow_multiple", False):
            continue

        if name == "AP Macroeconomics with Government" and not chose_economics_jr:
            continue
        if name in ("Linear Algebra", "Multivariable Calculus") and not took_ap_calc_bc_junior:
            continue
        if name == "AP Physics C: Mechanics" and "AP Physics C: Electricity & Magnetism" in courses_by_year["Senior"]:
            continue
        if name in PHYSICS_MAJOR_SN_COURSES and major == "Physics":
            continue

        if grade == "Junior":
            if language_base == "Spanish" and name in ("AP Spanish Language & Culture", "Advanced Spanish"):
                if "Spanish III" not in courses_by_year["Sophomore"]:
                    continue
            # AP language courses are only open to accelerated students (Spanish is handled above)
            if language_base in ("Chinese", "German", "Italian", "French") and not lang_is_accelerated:
                if name == f"AP {language_base} Language & Culture":
                    continue

        if name in AP_LOTES and language_base not in name:
            continue

        if is_lang_opt:
            # only junior/senior, and only after finishing level III of their own language
            if grade not in ("Junior", "Senior"):
                continue
            if name.split()[0] == language_base:
                continue
            if f"{language_base} III" not in prior_years:
                continue

        if grade == "Senior" and language_base == "Spanish":
            if name in ("Advanced Spanish", "AP Spanish Language & Culture") and "Spanish III" not in active_courses:
                continue

        if "available_grades" in data:
            if grade not in data["available_grades"]:
                continue
        elif grade in ("Freshman", "Sophomore"):
            continue

        if query not in name.lower() and query not in data.get("description", "").lower():
            continue

        periods = data.get("periods", 1)
        too_large = periods > available_headroom
        results.append({
            "name": name,
            "description": data.get("description", ""),
            "periods": periods,
            "semesters": data.get("semesters", 2),
            "credits": f"{float(data.get('credits', 1.0)):.1f}",
            "is_elective": data.get("is_elective", False),
            "disabled": too_large or ("AP" in name and ap_limit_reached),
            "grade_badges": grade_badges(
                data.get("is_elective", False),
                data.get("grades", []),
                data.get("available_grades", []),
            ),
        })
    return results

#import json
import io
import openpyxl
import math
import re
import reflex as rx
#from sqlmodel import select
#import bcrypt
            #colors
from data.courses import req_courses
from data.courses import elective_color
from data.courses import COURSE_CATALOG, MAJORS
from data.courses import lang_color
from data.courses import science_color
from data.courses import math_color
from data.courses import history_color
from data.courses import english_color
from data.courses import language_opts
import bthsplanner.theme as theme

required_courses_labels = ["Major Course", "Required Course"]

num_of_courses = str(len(COURSE_CATALOG))


config = rx.Config(
    app_name="bthsplanner", 
)

#old login class
class User(rx.Model, table=True):
    __tablename__ = "user"
    
    
    saved_progress: str # Stores JSON string of course/major selections

MAJOR_NAMES = list(MAJORS.keys())

# ====================== STATE LOGIC ======================
class PlannerState(rx.State):
    
    
    active_tab: str = "Plan"
    course_catalog: list[dict] = COURSE_CATALOG
    modal_source: str = "planner"
    is_detail_open: bool = False

    pre_credits: dict[str, bool] = {
        "Algebra I": False,
        "Geometry": False,
        "US History" : False,
        "Biology/Living Environment" : False,
    }

    def toggle_pre_credit(self, credit: str, checked: bool):
        self.pre_credits[credit] = checked

        if credit == "Geometry":
            if checked:
                self.j_math = "AP Calculus BC"
                self.sn_math = "Multivariable Calculus"
            else:
                self.j_math = "Pre-Calculus"
                self.sn_math = "AP Calculus BC"

    pre_language: str = "Spanish I"

    def change_pre_language(self, val: str):
        self.pre_language = val


    def change_tab(self, name: str):
        self.active_tab = name
    # --- Existing Grade Tracking ---
    major: str = "Aerospace Engineering"
    f_hist: str = "Pre-AP World History"
    f_sci: str = "Regents Physics"
    f_math: str = "Geometry"
    f_lang: str = "Spanish I"
    so_eng: str = "English 10"
    so_hist: str = "AP European History"
    j_eng: str = "English 11"
    j_his: str = "Regents United States History"
    j_phys: str = "Regents Physics"
    j_math: str = "Pre-Calculus"
    sn_math: str = "AP Calculus BC"
    sn_math_active: bool = True
    sn_eng: str = "Creative Writing"
    sn_his: str = "Economics"
    sn_ec: str = "Economics"
    sn_gov: str = "Participation in Government"

    # --- SPLIT ELECTIVE TRACKING LISTS ---
    freshman_electives: list[str] = []
    sophomore_electives: list[str] = []
    junior_electives: list[str] = []   # Electives explicitly added to Junior year
    senior_electives: list[str] = []   # Electives explicitly added to Senior year
    

    
        
    
    # --- Helper Data Export/Import Functions ---
    def _export_progress_dict(self) -> dict:
        return {
            "major": self.major,
            "f_hist": self.f_hist, "f_sci": self.f_sci, "f_math": self.f_math, "f_lang": self.f_lang,
            "so_eng": self.so_eng, "so_hist": self.so_hist,
            "j_eng": self.j_eng, "j_his": self.j_his, "j_phys": self.j_phys, "j_math": self.j_math,
            "sn_eng": self.sn_eng, "sn_his": self.sn_his, "sn_ec": self.sn_ec, "sn_gov": self.sn_gov, "sn_math": self.sn_math,
            "freshman_electives": list(self.freshman_electives),
            "sophomore_electives": list(self.sophomore_electives),
            "junior_electives": list(self.junior_electives),
            "senior_electives": list(self.senior_electives),
        }

    def _import_progress_dict(self, data: dict):
        self.major = data.get("major", self.major)
        self.f_hist = data.get("f_hist", self.f_hist)
        self.f_sci = data.get("f_sci", self.f_sci)
        self.f_math = data.get("f_math", self.f_math)
        self.f_lang = data.get("f_lang", self.f_lang)
        self.so_eng = data.get("so_eng", self.so_eng)
        self.so_hist = data.get("so_hist", self.so_hist)
        self.j_eng = data.get("j_eng", self.j_eng)
        self.j_his = data.get("j_his", self.j_his)
        self.j_phys = data.get("j_phys", self.j_phys)
        self.j_math = data.get("j_math", self.j_math)
        self.sn_eng = data.get("sn_eng", self.sn_eng)
        self.sn_his = data.get("sn_his", self.sn_his)
        self.sn_ec = data.get("sn_ec", self.sn_ec)
        self.sn_gov = data.get("sn_gov", self.sn_gov)
        self.sn_math = data.get("sn_math", self.sn_math)
        self.freshman_electives = data.get("freshman_electives", [])
        self.sophomore_electives = data.get("sophomore_electives", [])
        self.junior_electives = data.get("junior_electives", [])
        self.senior_electives = data.get("senior_electives", [])

    search_query: str = ""             # Live search text string
    active_modal_course: dict = {}     # Holds the course info for your detail popup
    is_detail_open: bool = False       # Controls the visibility of the global detail modal

    #adnvaced lang courses electives, exclude spanish bc spanihs has advanced spanish
    ap_lotes = ["AP Chinese Language & Culture", "AP French Language & Culture", "AP German Language & Culture", "AP Italian Language & Culture"]
    # NOW FULLY ACTIVATED FOR AUTOMATED GRADED FILTER ROUTING
    current_modal_grade: str = "Junior"
    
    @rx.var
    def current_page(self) -> str:
        return self.router.page.path
    
    # --- Existing Explicit Mutator Actions ---
    def export_to_excel(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "4-Year Plan"

        years = ["Freshman", "Sophomore", "Junior", "Senior"]
        year_cols = {"Freshman": 2, "Sophomore": 3, "Junior": 4, "Senior": 5}  # B, C, D, E

        # --- Row 1: Major ---
        ws.cell(row=1, column=1, value="Major")
        ws.cell(row=1, column=2, value=self.major)

        # --- Row 3: Year headers ---
        ws.cell(row=3, column=1, value="Year")
        for year, col in year_cols.items():
            ws.cell(row=3, column=col, value=year)

        # --- Rows 4+: courses, one per row, stacked under each year's column ---
        year_courses = {year: sorted(self._courses_for_year(year)) for year in years}
        max_courses = max(len(c) for c in year_courses.values())

        for i in range(max_courses):
            row = 4 + i
            for year, col in year_cols.items():
                courses = year_courses[year]
                if i < len(courses):
                    ws.cell(row=row, column=col, value=courses[i])

        # --- Summary rows: one blank row after the last course row ---
        summary_start = 4 + max_courses + 1
        ws.cell(row=summary_start, column=1, value="Courses")
        ws.cell(row=summary_start + 1, column=1, value="Periods")
        ws.cell(row=summary_start + 2, column=1, value="AP Count")

        course_counts = {
            "Freshman": self.freshman_course_count, "Sophomore": self.sophomore_course_count,
            "Junior": self.junior_course_count, "Senior": self.senior_course_count,
        }
        total_courses = sum(course_counts.values())
        periods = {
            "Freshman": self.freshman_periods, "Sophomore": self.sophomore_periods,
            "Junior": self.junior_periods, "Senior": self.senior_periods,
        }
        total_periods = sum(periods.values())
        ap_counts = {
            "Freshman": self.freshman_ap_count, "Sophomore": self.sophomore_ap_count,
            "Junior": self.junior_ap_count, "Senior": self.senior_ap_count,
        }
        total_ap = sum(ap_counts.values())

        for year, col in year_cols.items():
            ws.cell(row=summary_start, column=col, value=course_counts[year])
            ws.cell(row=summary_start, column=col+1, value=total_courses)
            ws.cell(row=summary_start + 1, column=col, value=periods[year])
            ws.cell(row=summary_start + 1, column=col+1, value=total_periods)
            ws.cell(row=summary_start + 2, column=col, value=ap_counts[year])
            ws.cell(row=summary_start + 2, column=col+1, value=total_ap)

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return rx.download(
            data=buffer.getvalue(),
            filename="brooklyn_tech_plan.xlsx",
        )

    @rx.var
    def freshman_math_courses(self) -> list[str]:
        if self.math_is_accelerated:
            return ["Algebra II"]
        if not self.pre_credits.get("Algebra I", False):
            return ["Algebra I", "Geometry"]
        return ["Geometry"]
    
    def change_major(self, val: str):
        self.major = val
        # Reset all dropdowns and electives to defaults on major change
        self.f_hist = "Pre-AP World History"
        self.f_sci = "Regents Physics"
        self.f_math = "Geometry"
        self.f_lang = "Spanish I"
        self.so_eng = "English 10"
        self.so_hist = "AP European History"
        self.j_eng = "English 11"
        self.j_his = "Regents United States History"
        self.j_phys = "Regents Physics"
        self.j_math = "Pre-Calculus"
        self.sn_eng = "Creative Writing"
        self.sn_his = "Participation in Government" if self.has_econ_gov_conflict else "Economics"
        self.sn_ec = "Economics"
        self.sn_gov = "Participation in Government"
        self.freshman_electives = []
        self.sophomore_electives = []
        self.junior_electives = []
        self.senior_electives = []
        self.j_math = "Pre-Calculus"
        self.sn_math = "AP Calculus BC"
    def change_f_hist(self, val: str):
        snapshot = self._export_progress_dict()
        self.f_hist = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)

    def change_f_sci(self, val: str):
        snapshot = self._export_progress_dict()
        self.f_sci = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_f_math(self, val: str):
        snapshot = self._export_progress_dict()
        self.f_math = val
        self._enforce_ap_limits()
        self._evict_duplicates()
        self.j_math = "AP Calculus BC"
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_f_lang(self, val: str):
        snapshot = self._export_progress_dict()
        self.f_lang = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_so_eng(self, val: str):
        snapshot = self._export_progress_dict()
        self.so_eng = val
        if val == "AP Capstone Seminar":
    
            if self.senior_ap_count < 3:
                self.sn_eng = "AP Capstone Research"
                if not self._enforce_period_limits():
                    self._import_progress_dict(snapshot)
        else:
            self.sn_eng = "Creative Writing"
            if not self._enforce_period_limits():
                self._import_progress_dict(snapshot)

    def change_so_hist(self, val: str):
        snapshot = self._export_progress_dict()
        self.so_hist = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_j_his(self, val: str):
        snapshot = self._export_progress_dict()
        prev = self.j_his
        self.j_his = val
        if prev == "Economics" and val != "Economics":
            self.sn_his = "Economics"
            if "AP Macroeconomics with Government" in self.senior_electives:
                self.senior_electives.remove("AP Macroeconomics with Government")
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)

    def change_j_phys(self, val: str):
        snapshot = self._export_progress_dict()
        self.j_phys = val
        self._enforce_ap_limits()
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_j_math(self, val: str):
        snapshot = self._export_progress_dict()
        self.j_math = val
        if val == "AP Calculus BC":
            self.sn_math = "Multivariable Calculus"
        if val == "Pre-Calculus":
            self.sn_math = "AP Calculus BC"
        self._enforce_ap_limits()
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_sn_math(self, val: str):
        snapshot = self._export_progress_dict()
        self.sn_math = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def toggle_sn_math(self):
        self.sn_math_active = not self.sn_math_active

    

    #for physcs majors physics II and or Physics c e and m
    selected_senior_physics: set[str] = {"AP Physics C: Electricity & Magnetism"}
    
        #selected_senior_physics.remove("AP Physics II")
    def toggle_senior_physics(self, course_name: str):
        #makes sure physics majors keep atleast one
        if course_name in self.selected_senior_physics:
            if len(self.selected_senior_physics) > 1:
                self.selected_senior_physics.remove(course_name)
        else:
            self.selected_senior_physics.add(course_name)
            if self.senior_periods > 8 or self.senior_ap_count > 3:
                self.selected_senior_physics.remove(course_name)
            

    def change_j_eng(self, val: str):
        snapshot = self._export_progress_dict()
        self.j_eng = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_sn_eng(self, val: str):
        snapshot = self._export_progress_dict()
        self.sn_eng = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_sn_his(self, val: str):
        snapshot = self._export_progress_dict()
        self.sn_his = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_sn_ec(self, val: str):
        snapshot = self._export_progress_dict()
        self.sn_ec = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)
    def change_sn_gov(self, val: str):
        snapshot = self._export_progress_dict()
        self.sn_gov = val
        self._evict_duplicates()
        if not self._enforce_period_limits():
            self._import_progress_dict(snapshot)

    # --- Dynamic Period, Course Count Calculators ---
    # --- Dynamic Period Tracker Using Semester Pairing Logic ---
    # --- Dynamic Period Tracker Using Semester Pairing Logic ---
    def _calculate_total_periods(self, year: str) -> int:
        courses = self._courses_for_year(year)
        full_year_periods = 0
        single_semester_1_pd = 0
        single_semester_2_pd = 0
        
        for c in courses:
            data = COURSE_CATALOG.get(c, {})
            pds = data.get("periods", 1)
            
            if data.get("semesters") == 1:
                if pds == 2:
                    # Count how many 2 period semester classes they have
                    single_semester_2_pd += 1
                else:
                    # Count how many 1 period semester classes they have
                    single_semester_1_pd += 1
            else:
                full_year_periods += pds
                
        # 1. Pair up 1-period semester classes: math.ceil(count / 2) -> each pair = 1 period
        # 2. Pair up 2-period semester classes: math.ceil(count / 2) * 2 -> each pair = 2 periods
        total_semester_room = math.ceil(single_semester_1_pd / 2) + (math.ceil(single_semester_2_pd / 2) * 2)
        
        return full_year_periods + total_semester_room

    @rx.var
    def freshman_periods(self) -> int:
        return self._calculate_total_periods("Freshman")

    @rx.var
    def sophomore_periods(self) -> int:
        return self._calculate_total_periods("Sophomore")

    

    @rx.var
    def junior_periods(self) -> int:
        return self._calculate_total_periods("Junior")

    @rx.var
    def senior_periods(self) -> int:
        return self._calculate_total_periods("Senior")

    @rx.var
    def freshman_course_count(self) -> int:
        return len(self._courses_for_year("Freshman"))

    @rx.var
    def sophomore_course_count(self) -> int:
        return len(self._courses_for_year("Sophomore"))

    @rx.var
    def junior_course_count(self) -> int:
        return len(self._courses_for_year("Junior"))

    @rx.var
    def senior_course_count(self) -> int:
        return len(self._courses_for_year("Senior"))

    @rx.var
    def total_course_count(self) -> int:
        return (self.freshman_course_count + 
                self.sophomore_course_count + 
                self.junior_course_count + 
                self.senior_course_count)

    
    
    # --- AP Course Counters ---
    @rx.var
    def freshman_ap_count(self) -> int:
        count = 0
        for c in self._courses_for_year("Freshman"):
            # pre ap world is not ap
            if c[:2] == "AP":
                count += 1
        return count

    @rx.var
    def sophomore_ap_count(self) -> int:
        return sum(1 for c in self._courses_for_year("Sophomore") if "AP" in c)

    @rx.var
    def junior_ap_count(self) -> int:
        return sum(1 for c in self._courses_for_year("Junior") if "AP" in c)

    @rx.var
    def senior_ap_count(self) -> int:
        return sum(1 for c in self._courses_for_year("Senior") if "AP" in c)
    
  
    
    # --- Global Pop-up Event Actions ---
    def set_search_query(self, val: str):
        self.search_query = val

    def close_course_details(self):
        self.is_detail_open = False
    
    def open_course_details(self, name: str):
        data = COURSE_CATALOG.get(name, {})
        self.active_modal_course = {
            "name": name,
            "description": data.get("description", "No description available for this course yet."),
            "periods": str(data.get("periods", 1)),
            "credits": str(data.get("credits", 1.0)),
            "is_elective": data.get("is_elective", False),
            "semesters": str(data.get("semesters", 2)),
            "grade_badges": _grade_badges(
                data.get("is_elective", False),
                data.get("grades", []),
                data.get("available_grades", [])
            ),
        }
        self.is_detail_open = True

    def open_search_for_grade(self, grade_name: str):
        self.current_modal_grade = grade_name
        self.search_query = ""

    def add_course(self, course_name: str, target_year: str):
        if target_year == "Freshman" and course_name not in self.freshman_electives:
            self.freshman_electives.append(course_name)
        elif target_year == "Sophomore" and course_name not in self.sophomore_electives:
            self.sophomore_electives.append(course_name)
        elif target_year == "Junior" and course_name not in self.junior_electives:
            self.junior_electives.append(course_name)
        elif target_year == "Senior" and course_name not in self.senior_electives:
            self.senior_electives.append(course_name)
        self._evict_duplicates()

    def delete_course(self, course_name: str, target_year: str):
        junior_reqs = MAJORS[self.major].get("Junior", [])
        senior_reqs = MAJORS[self.major].get("Senior", [])
        
        if course_name in junior_reqs or course_name in senior_reqs:
            return rx.window_alert(f"Cannot delete {course_name}! This course is a core requirement for {self.major}.")
            
        if target_year == "Freshman" and course_name in self.freshman_electives:
            self.freshman_electives.remove(course_name)
        elif target_year == "Sophomore" and course_name in self.sophomore_electives:
            self.sophomore_electives.remove(course_name)
        elif target_year == "Junior" and course_name in self.junior_electives:
            self.junior_electives.remove(course_name)
        elif target_year == "Senior" and course_name in self.senior_electives:
            self.senior_electives.remove(course_name)

    # --- Computed Vars ---
    @rx.var(cache=True)
    def room(self) -> str: return MAJORS[self.major].get("room", "N/A")

    @rx.var(cache=True)
    def major_note(self) -> str: return MAJORS[self.major].get("note", "")

    @rx.var(cache=True)
    def math_is_accelerated(self) -> bool: return self.pre_credits.get("Geometry", False)

    @rx.var
    def took_ap_calc_bc_junior(self) -> bool:
        return self.math_is_accelerated or self.j_math == "AP Calculus BC" or self.j_math == "AP Calculus AB"

    @rx.var(cache=True)
    def lang_is_accelerated(self) -> bool: return "II" in self.f_lang

    @rx.var(cache=True)
    def language_base(self) -> str: return self.f_lang.split()[0] if self.f_lang else ""

    @rx.var(cache=True)
    def took_seminar(self) -> bool: return self.so_eng == "AP Capstone Seminar"

    @rx.var(cache=True)
    def chose_economics_jr(self) -> bool: 
        took_reg_econ = self.j_his == "Economics"
        return took_reg_econ
    
    @rx.var(cache=True)
    def chose_african_jr(self) -> bool:
        return self.j_his == "AP African American Studies" 
    @rx.var(cache=True)
    def chose_government_jr(self) -> bool:
        return (
            ("AP US Government" in self.junior_major_courses or 
            "AP US Government" in self.junior_electives) or ("AP US Government" in self.senior_major_courses or "AP US Government" in self.senior_electives) or ("AP Comparative Government" in self.senior_major_courses)
        )
    @rx.var(cache = True)
    def has_macro(self) -> bool:
        return ("AP Macroeconomics with Government" in self.junior_major_courses or "AP Macroeconomics with Government" in self.senior_major_courses)

    @rx.var(cache=True)
    def has_econ_gov_conflict(self) -> bool:
        #True if the student already has AP Macroeconomics or AP Macroeconomics / AP Microeconomics (One Semester each)
        conflict_courses = {
            "AP Macroeconomics with Government",
            "AP Macroeconomics / AP Microeconomics (One Semester each)",
        }
        sources = (
            self.junior_major_courses + self.senior_major_courses +
            self.junior_electives + self.senior_electives
        )
        return any(c in conflict_courses for c in sources)
    @rx.var(cache=True)
    def has_gov_conflict(self) -> bool:
        """True if the student's major already includes AP Comparative Government 
        as a required junior-year course (currently: LAS) — this conflicts with 
        also taking Participation in Government junior year, since Comparative 
        Government already satisfies the gov credit."""
        return self.major == "Law & Society" or "AP Comparative Government" in MAJORS[self.major].get("Junior", [])
    @rx.var(cache=True)

    def took_ap_hg_fr(self) -> bool:
        return "AP Human Geography" in self._courses_for_year("Freshman")
    
    @rx.var(cache=True)
    def has_ap_physics_junior(self) -> bool: return any("AP Physics I" in c for c in MAJORS[self.major].get("Junior", []))

    @rx.var(cache=True)
    def need_regents_physics_junior(self) -> bool: 
        if "AP Physics I" in self.junior_electives or "AP Physics I" in self.senior_electives:
            return False
        return (self.f_sci != "Regents Physics") and not self.has_ap_physics_junior

    @rx.var(cache=True)
    def junior_ap_room_for_physics(self) -> bool:
        """Whether there's room for another AP junior year, not counting the
        Regents Physics / AP Physics I swap slot itself."""
        others = [c for c in self._courses_for_year("Junior") if "AP" in c and c != self.j_phys]
        return len(others) < 3
    @rx.var(cache = True)
    def major_has_aphg(self) -> bool:
        return "AP Human Geography" in self.junior_major_courses or "AP Human Geography" in self.senior_major_courses

    @rx.var(cache=True)
    def junior_major_courses(self) -> list[str]:
        courses = MAJORS[self.major].get("Junior", [])
        final_courses = []
        for c in courses:
            if "AP Biology" in c and self.f_sci == "AP Biology":
                final_courses.append("AP Chemistry")
            else:
                final_courses.append(c)
        return final_courses

    @rx.var(cache=True)
    def senior_major_courses(self) -> list[str]:
        courses = MAJORS[self.major].get("Senior", [])
        courses = [c for c in courses if c != "AP Calculus BC or Multi-Variable Calculus"]

        # 🎯 LIU Pharmacy: AP Biology freshman year bumps the senior AP Biology
        # slot to AP Physics I, or AP Physics C: Mechanics if they also took
        # AP Physics I junior year.
        if self.major == "LIU Pharmacy" and self.f_sci == "AP Biology":
            took_ap_physics_jr = "AP Physics I" in self.junior_electives or self.j_phys == "AP Physics I"
            replacement = "AP Physics C: Mechanics" if took_ap_physics_jr else "AP Physics I"
            courses = [replacement if c == "AP Biology" else c for c in courses]

        return courses
    # --- Math Major Overrides and Filtering Backend ---
    @property
    def _math_keywords(self) -> list[str]:
        return ["Calculus", "Algebra II", "Geometry", "Pre-Calculus"]

    @rx.var
    def junior_math_override(self) -> str:
        if self.major == "Applied Mathematics":
            return "Mathematics Major Override"
        for c in self.junior_major_courses:
            if any(kw in c for kw in self._math_keywords):
                return c
            
        return ""

    @rx.var
    def senior_math_override(self) -> str:
        if self.major == "Applied Mathematics" or self.major == "LIU Pharmacy":
            return "Mathematics Major Override"
        for c in self.senior_major_courses:
            if any(kw in c for kw in self._math_keywords):
                return c
        return ""

    @rx.var
    def filtered_junior_major_courses(self) -> list[str]:
        override = self.junior_math_override
        return [c for c in self.junior_major_courses if c != override]

    @rx.var
    def filtered_senior_major_courses(self) -> list[str]:
        override = self.senior_math_override
        return [c for c in self.senior_major_courses if c != override]

    
    def _courses_for_year(self, year: str) -> set:
        if year == "Freshman":
            return set([
                "Design & Drafting for Production (DDP)", "English 9",
                self.f_hist, self.f_sci, self.f_lang, 
            ] + self.freshman_math_courses + self.freshman_electives)

        if year == "Sophomore":
            math = "Pre-Calculus" if self.math_is_accelerated else "Algebra II"
            lang = (self.language_base + " III") if self.lang_is_accelerated else (self.language_base + " II")
            return set([
                "AP Computer Science Principles", "Health Education", self.so_eng, self.so_hist,
                "Regents Chemistry", math, lang,
            ] + self.sophomore_electives)
            
        if year == "Junior":
            math = "AP Calculus BC" if self.math_is_accelerated else self.j_math
            # Start with dropdowns and electives as a clean list
            courses = [self.j_eng, self.j_his.rstrip("*")] + self.junior_electives
            
            # 🎯 If they chose Economics in Junior year, dynamically inject Government into Junior year active tracker
            if (self.j_his == "Economics" or (
                "AP Macroeconomics / AP Microeconomics (One Semester each)" in self.junior_major_courses or 
                "AP Macroeconomics / AP Microeconomics (One Semester each)" in self.junior_electives
            )) and not self.has_econ_gov_conflict and not self.chose_government_jr and not self.has_gov_conflict:
                courses.append(self.sn_gov)
            
            if self.junior_math_override != "":
                courses.extend(self.filtered_junior_major_courses)
                courses.append(math)
            else:
                courses.extend(self.junior_major_courses)
                courses.append(math)
                
            if not self.lang_is_accelerated:
                courses.append(self.language_base + " III")
            if self.need_regents_physics_junior:
                courses.append(self.j_phys)
            return set(courses)
        
        if year == "Senior":

            math = self.sn_math if self.sn_math else "AP Calculus BC"
            courses = [self.sn_eng] + self.senior_electives
            
            if self.major == "Physics":
                if math and self.sn_math_active:
                    courses.append(math)
                courses.extend(list(self.selected_senior_physics))
                courses.append("Modern Physics") 
            else:
                if self.senior_math_override != "":
                    courses.extend(self.filtered_senior_major_courses)
                else:
                    courses.extend(self.senior_major_courses)
                if math and self.sn_math_active:
                    courses.append(math)
            # 🎯 Only track Senior History rules if they DID NOT choose Economics early in Junior year
            if self.has_macro:
                pass
            elif not self.chose_economics_jr:
                if self.chose_government_jr:
                    courses.append("Economics")
                else:
                    courses.append(self.sn_his)
                    if self.sn_his in ("AP US Government", "Participation in Government"):
                        courses.append(self.sn_ec)
                    if self.sn_his == "Economics" and not self.has_gov_conflict:
                        courses.append(self.sn_gov)

            return set(courses)

    def _evict_duplicates(self):
        fr = self._courses_for_year("Freshman")
        so = self._courses_for_year("Sophomore")
        jr = self._courses_for_year("Junior")

        prior_after_fr = fr
        prior_after_so = fr | so
        prior_after_jr = fr | so | jr

        if self.so_eng in prior_after_fr and self.so_eng != "English 10":
            self.so_eng = "English 10"
        if self.so_hist in prior_after_fr:
            self.so_hist = "Regents Global History"
        self.sophomore_electives = [c for c in self.sophomore_electives if c not in prior_after_fr or COURSE_CATALOG.get(c, {}).get("allow_multiple", False)]

        if self.j_eng in prior_after_so:
            self.j_eng = "English 11"
        if self.j_his.rstrip("*") in prior_after_so:
            self.j_his = "Regents United States History"
        if self.j_his == "Economics" and self.has_econ_gov_conflict:
            self.j_his = "Regents United States History"
            self.sn_his = "Economics"
        self.junior_electives = [c for c in self.junior_electives if c not in prior_after_so or COURSE_CATALOG.get(c, {}).get("allow_multiple", False)]

        if self.sn_eng in prior_after_jr:
            self.sn_eng = "Creative Writing"
        if self.sn_his in prior_after_jr:
            self.sn_his = "Participation in Government"
        if self.sn_ec in prior_after_jr:
            self.sn_his = "Participation in Government"
        if self.sn_gov in prior_after_jr:
            self.sn_gov = "Participation in Government"
        self.senior_electives = [c for c in self.senior_electives if c not in prior_after_jr or COURSE_CATALOG.get(c, {}).get("allow_multiple", False)]

    def _enforce_ap_limits(self):
        if self.junior_ap_count > 3:
            if "AP" in self.j_eng: self.j_eng = "English 11"
            if "AP" in self.j_his: self.j_his = "Regents United States History"
            if "AP" in self.j_phys: self.j_phys = "Regents Physics"
            if "AP" in self.j_math: self.j_math = "Pre-Calculus"
            while self.junior_ap_count > 3:
                ap_els = [c for c in self.junior_electives if "AP" in c]
                if not ap_els: break
                self.junior_electives.remove(ap_els[0])
        if self.senior_ap_count > 3:
            if "AP" in self.sn_eng: self.sn_eng = "Creative Writing"
            if "AP" in self.sn_his: self.sn_his = "Economics"
            if "AP" in self.sn_ec: self.sn_ec = "Economics"
            while self.senior_ap_count > 3:
                ap_els = [c for c in self.senior_electives if "AP" in c]
                if not ap_els: break
                self.senior_electives.remove(ap_els[0])

    def _enforce_period_limits(self) -> bool:
        
        year_to_electives = {
            "Freshman": "freshman_electives",
            "Sophomore": "sophomore_electives",
            "Junior": "junior_electives",
            "Senior": "senior_electives",
        }
        ok = True
        for year, attr in year_to_electives.items():
            while self._calculate_total_periods(year) > 8:
                electives = getattr(self, attr)
                if not electives:
                    ok = False
                    break  # over the cap with no electives left to cut — nothing more to auto-fix
                electives.pop(0) 
        return ok

    
    def compute_filtered_catalog(self) -> list[dict]:
        query = self.search_query.lower().strip()
        results = []
        
        active_courses = set()
        for yr in ["Freshman", "Sophomore", "Junior", "Senior"]:
            active_courses.update(self._courses_for_year(yr))

        

        
    
    
        current_grade = str(self.current_modal_grade).strip()

        # Headroom AND AP limit verification routing based on active modal view
        if current_grade == "Freshman":
            current_periods = self.freshman_periods
            ap_limit_reached = self.freshman_ap_count >= 3
        elif current_grade == "Sophomore":
            current_periods = self.sophomore_periods
            ap_limit_reached = self.sophomore_ap_count >= 3
        elif current_grade == "Junior":
            current_periods = self.junior_periods
            ap_limit_reached = self.junior_ap_count >= 3
        else:
            current_periods = self.senior_periods
            ap_limit_reached = self.senior_ap_count >= 3

        available_headroom = 8 - current_periods

        for name, data in COURSE_CATALOG.items():
            if self.active_tab == "Explore":
                if query not in name.lower() and query not in data.get("description", "").lower():
                    continue
            else:
                if not data.get("is_elective", False) or (name in active_courses and not data.get("allow_multiple", False)):
                    continue
                
                if name in ["AP Macroeconomics with Government", "AP Microeconomics with Government"]:
                    if not self.chose_economics_jr:
                        continue

                if name == "Linear Algebra" and not self.took_ap_calc_bc_junior:
                    continue
                if name == "Multivariable Calculus" and not self.took_ap_calc_bc_junior:
                    continue
                if name == "AP Physics C: Mechanics":
                    if "AP Physics C: Electricity & Magnetism" in self._courses_for_year("Senior"):
                        continue

                if name == "AP Physics C: Electricity & Magnetism" and self.major == "Physics":  
                    continue
                
                if current_grade == "Junior" and self.language_base == "Spanish":
                    if name == "AP Spanish Language & Culture" and "Advanced Spanish" not in self._courses_for_year("Sophomore"):
                        continue

                if current_grade == "Junior" and self.language_base == "Chinese" and not self.lang_is_accelerated:
                    if name == "AP Chinese Language & Culture":
                        continue
                if current_grade == "Junior" and self.language_base == "German" and not self.lang_is_accelerated:
                    if name == "AP German Language & Culture":
                        continue

                if current_grade == "Junior" and self.language_base == "Italian" and not self.lang_is_accelerated:
                    if name == "AP Italian Language & Culture":
                        continue
                if current_grade == "Junior" and self.language_base == "French" and not self.lang_is_accelerated:
                    if name == "AP French Language & Culture":
                        continue

                if name in self.ap_lotes and self.language_base not in name:
                    continue

                if name == "Advanced Spanish" and current_grade == "Junior":
                    if "Spanish III" not in self._courses_for_year("Sophomore"):
                        continue

                if name == "Advanced Spanish" and current_grade == "Senior":
                    if "Spanish III" not in self._courses_for_year("Junior"):
                        continue

                

                if "available_grades" in data:
                    allowed = data["available_grades"]
                    if current_grade not in allowed:
                        continue
                    
                else:
                    if current_grade in ["Freshman", "Sophomore"]:
                        continue

            # ◄ RULE: Unless it explicitly says 2 periods, default it to 1 period
            raw_periods = data.get("periods", 1)
            semesters = data.get("semesters", 2)
            
            
            is_too_large = raw_periods > available_headroom
            is_ap_course = "AP" in name
            should_disable = is_too_large or (is_ap_course and ap_limit_reached)

            if query in name.lower() or query in data.get("description", "").lower():
                
                credits_formatted = f"{float(data.get('credits', 1.0)):.1f}"

                results.append({
                    "name": name, 
                    "description": data.get("description", ""),
                    "periods": raw_periods, # ◄ FIX: This now passes '1' or '2' to the badge display
                    "semesters" : semesters,
                    "credits": credits_formatted,
                    "is_elective" : data.get("is_elective", False),
                    "disabled": should_disable if self.active_tab != "Explore" else False,
                    "grade_badges": _grade_badges(
                        data.get("is_elective", False),
                        data.get("grades", []),
                        data.get("available_grades", [])
                    ),
                })
        return results
   #login 

    @rx.var
    def filtered_catalog(self) -> list[dict]:
        return self.compute_filtered_catalog()
    
    @rx.var
    def filtered_catalog_count(self) -> int:
        return len(self.compute_filtered_catalog())
    @rx.var
    def dropdown_colors(self) -> dict[str, str]:
        return {name: data.get("color", "#1e2025") for name, data in COURSE_CATALOG.items()}

def styled_select(options: list[str], value: rx.Var, on_change: any, font: str = "18px", width: str = "160px",) -> rx.Component:
    return rx.select.root(
        rx.select.trigger(
            class_name="reflex-dropdown-select",
            style={
                "background_color": "#101827",
                "padding": "8px 12px !important",
                "border": "1px solid #434651",
                "border_radius": "0.5rem",
                "width": width,
                "font_weight": "600 !important",
                "background_image": "none !important",
                "font_size" : font
            },
        ),
        rx.select.content(
            *[rx.select.item(opt, value=opt) for opt in options]
        ),
        value=value,
        on_change=on_change,
    )

def legend_item(label: str, border_color: str) -> rx.Component:
    """Helper component for rendering a single legend item."""
    return rx.hstack(
        # The colored rounded outline box
        rx.box(
            width="18px",
            height="18px",
            border=f"3.5px solid {border_color}",
            border_radius="5px",
            background_color="transparent",
        ),
        # Label text
        rx.text(
            label,
            color="#FFFFFF", 
            font_size="18px",
            font_weight="600",
        ),
        align_items="center",
        spacing="2",
    )

def legend_bar() -> rx.Component:
    """Main horizontal legend bar component."""
    return rx.hstack(
        # Main label
        rx.text(
            "Legend:",
            font_weight="bold",
            color="white",
            font_size="20px",
            #margin_right="8px",
        ),
        # Color indicator items matching your image
        legend_item("English", english_color),  
        legend_item("History", history_color),   
        legend_item("Science", science_color),    
        legend_item("Math", math_color),  
        legend_item("Language", lang_color),   
        legend_item("Major/Required", req_courses),
        legend_item("Elective", elective_color),  

        align_items="center",
        spacing="5",
        padding="12px 0px",
        background_color="#0F172A",  # Dark background matching image
        border_radius="8px",
    )
def pre_credit_checkbox(label: str) -> rx.Component:
    return rx.hstack(
        rx.checkbox(
            checked=PlannerState.pre_credits[label],
            on_change=PlannerState.toggle_pre_credit(label),
        ),
        rx.text(label, color="#FFFFFF", font_size="18px", font_weight="600"),
        align_items="center",
        spacing="2",
    )
def pre_language_checkbox() -> rx.Component:
    return rx.hstack(
        rx.checkbox(
            checked=PlannerState.pre_credits["Language"],
            on_change=PlannerState.toggle_pre_credit("Language"),
        ),
        styled_select(language_opts, PlannerState.pre_language, PlannerState.change_pre_language),
        align_items="center",
        spacing="2",
    )
def _grade_badges(is_elective: bool, grades: list, available_grades: list) -> list[str]:
    if grades:
        return grades
    elif available_grades:
        return available_grades
    elif is_elective:
        return ["Junior", "Senior"]
    else:
        return []
    
def navigation_layout(content: rx.Component) -> rx.Component:
    return rx.vstack(
        # Auth Modal Condition
        
        
        # Navigation Bar
        rx.box(
            rx.hstack(
                # Logo & Brand
                rx.hstack(
                    rx.image(
                        src="/header_logo.png",
                        width="55px",
                        height="auto",
                        border_radius="4px",
                    
                    ),
                    rx.text(
                        "BTHS Planner", size="7", weight="bold", color="#fafafa", 
                    ),
                    spacing="3",
                    align_items="center",
                ),
                # Navigation Links
                rx.hstack(
                    rx.link(
                        rx.text(
                            "Plan", size = "5",
                            color=rx.cond(
                                PlannerState.active_tab == "Plan",
                                "#fafafa",
                                "rgba(250, 250, 250, 0.6)",
                            
                            ),
                            weight=rx.cond(
                                PlannerState.active_tab == "Plan",
                                "medium",
                                "normal",
                            ),
                            
                        ),
                        href="/",
                        text_decoration="none",
                        padding_x="12px",
                        padding_y="8px",
                        border_bottom=rx.cond(
                            PlannerState.active_tab == "Plan",
                            "2px solid #3b82f6",
                            "2px solid transparent",
                        ),
                    ),
                    rx.link(
                        rx.text(
                            "Explore", size = "5",
                            color=rx.cond(
                                PlannerState.active_tab == "Explore",
                                "#fafafa",
                                "rgba(250, 250, 250, 0.6)",
                            ),
                            weight=rx.cond(
                                PlannerState.active_tab == "Explore",
                                "medium",
                                "normal",
                            ),
                        ),
                        href="/explore",
                        text_decoration="none",
                        padding_x="12px",
                        padding_y="8px",
                        border_bottom=rx.cond(
                            PlannerState.active_tab == "Explore",
                            "2px solid #3b82f6",
                            "2px solid transparent",
                        ),
                    ),
                    rx.link(
                        rx.text(
                            "How It Works", size = "5",
                            color=rx.cond(
                                PlannerState.active_tab == "How It Works",
                                "#fafafa",
                                "rgba(250, 250, 250, 0.6)",
                            ),
                            weight=rx.cond(
                                PlannerState.active_tab == "How It Works",
                                "medium",
                                "normal",
                            ),
                        ),
                        href="/how-it-works",
                        text_decoration="none",
                        padding_x="12px",
                        padding_y="8px",
                        border_bottom=rx.cond(
                            PlannerState.active_tab == "How It Works",
                            "2px solid #3b82f6",
                            "2px solid transparent",
                        ),
                    ),
                    spacing="4",
                    margin_left="24px",
                ),
                rx.spacer(),
                # Action Buttons
                rx.hstack(
                    
                    rx.button(
                        "Export to Excel",
                        on_click=PlannerState.export_to_excel,
                        color_scheme="blue",
                        size="3",
                    ),
                    
                    
                    spacing="3",
                    align_items="center",
                ),
                align_items="center",
                width="100%",
                max_width="1400px",
                margin="0 auto",
            ),
            position="sticky",
            top="0",
            z_index="100",
            background_color="#1f2937", # color of tab bar
            border_bottom="1px solid #31353f",
            padding_x="40px",
            padding_y="16px",
            width="100%",
        ),
        # Page Content Container
        rx.box(
            content,
            padding_x="32px",
            padding_y="40px",
            width="100%",
            max_width="1400px",
            margin="0 auto",
        ),
        width="100%",
        min_height="100vh",
        background_color=theme.illini_blue, #main color on every page 
        spacing="0",
    )

def _expand_taken(taken: set) -> set:
    expanded = set()
    for t in taken:
        expanded.add(t)
        if " / " in t:
            for part in t.split(" / "):
                clean = part.strip()
                expanded.add(clean)
                no_paren = re.sub(r'\s*\(.*?\)\s*$', '', clean).strip()
                if no_paren != clean:
                    expanded.add(no_paren)
    return expanded

def _filter(opts: list, current: str, at_limit: bool, taken: set) -> list:
    expanded = _expand_taken(taken)
    return [
        o for o in opts
        if (o == current or o not in expanded)
        and (o == current or "AP" not in o or not at_limit)
    ]

class DropdownOptions(PlannerState):
    @rx.var
    def f_hist_opts(self) -> list[str]:
        opts = ["Pre-AP World History", "AP Human Geography"]
        return _filter(opts, self.f_hist, self.freshman_ap_count >= 3, set())
    @rx.var
    def f_sci_opts(self) -> list[str]:
        opts = ["Regents Physics", "Regents Biology", "AP Biology"]
        return _filter(opts, self.f_sci, self.freshman_ap_count >= 3, set())
    @rx.var
    def so_eng_opts(self) -> list[str]:
        opts = ["English 10", "AP Capstone Seminar"]
        return _filter(opts, self.so_eng, self.sophomore_ap_count >= 3, self._courses_for_year("Freshman"))
    @rx.var
    def so_hist_opts(self) -> list[str]:
        opts = ["AP European History", "AP World History", "Regents Global History"]
        return _filter(opts, self.so_hist, self.sophomore_ap_count >= 3, self._courses_for_year("Freshman"))
    @rx.var
    def j_eng_opts(self) -> list[str]:
        opts = ["AP English Language & Composition", "English 11"]
        prior = self._courses_for_year("Freshman") | self._courses_for_year("Sophomore")
        return _filter(opts, self.j_eng, self.junior_ap_count >= 3, prior)
    @rx.var
    def j_his_opts(self) -> list[str]:
        opts = ["AP United States History", "Regents United States History", "Economics", "AP African American Studies"]
        if self.has_econ_gov_conflict:
            opts = [o for o in opts if o != "Economics"]
        prior = self._courses_for_year("Freshman") | self._courses_for_year("Sophomore")
        return _filter(opts, self.j_his, self.junior_ap_count >= 3, prior)
    @rx.var
    def j_math_opts(self) -> list[str]:
        opts = ["AP Calculus AB", "AP Calculus BC"] if self.math_is_accelerated else ["Pre-Calculus", "AP Calculus AB", "AP Calculus BC"]
        prior = self._courses_for_year("Freshman") | self._courses_for_year("Sophomore")
        return _filter(opts, self.j_math, self.junior_ap_count >= 3, prior)
    @rx.var
    def j_phys_opts(self) -> list[str]:
        return ["Regents Physics", "AP Physics I"]
    @rx.var
    def sn_calcs(self) -> list[str]:
        return ["AP Calculus BC", "AP Calculus AB"]
    @rx.var
    def sn_math_opts(self) -> list[str]:
        if self.major == "LIU Pharmacy":
            opts = ["Multivariable Calculus", "Linear Algebra", "AP Calculus BC"] if self.j_math == "AP Calculus AB" else ["Multivariable Calculus", "Linear Algebra"]
        elif self.senior_math_override:
            opts = ["Multivariable Calculus", "AP Calculus BC"] if self.j_math == "AP Calculus AB" else ["Multivariable Calculus"]    
        else:
            opts = ["Multivariable Calculus", "Linear Algebra", "AP Calculus BC"] if self.j_math == "AP Calculus AB" else ["Multivariable Calculus", "Linear Algebra"]
        prior = self._courses_for_year("Freshman") | self._courses_for_year("Sophomore") | self._courses_for_year("Junior")
        return _filter(opts, self.sn_math, False, prior)
    @rx.var
    def sn_eng_opts(self) -> list[str]:
        opts = ["AP Capstone Research", "AP English Literature & Composition", "Creative Writing", "Film & Literature", "Graphic Novels", "Journalism", "Science Fiction & Fantasy", "Mystery, Horror & the Supernatural", "Live, Love, & Death", "Drama", "Yearbook"] if self.so_eng == "AP Capstone Seminar" else [ "AP English Literature & Composition", "Creative Writing", "Film & Literature", "Graphic Novels", "Journalism", "Science Fiction & Fantasy", "Mystery, Horror & the Supernatural", "Live, Love, & Death", "Drama", "Yearbook"]
        prior = self._courses_for_year("Freshman") | self._courses_for_year("Sophomore") | self._courses_for_year("Junior")
        return _filter(opts, self.sn_eng, self.senior_ap_count >= 3, prior)
    @rx.var
    def sn_his_opts(self) -> list[str]:
        if self.has_econ_gov_conflict:
            opts = ["AP US Government", "Participation in Government"]
        else:
            opts = ["AP Macroeconomics with Government", "AP Microeconomics with Government", "Economics", "AP US Government", "Participation in Government"]
        if self.chose_government_jr:
            opts = [o for o in opts if o != "Participation in Government"]
    
        prior = self._courses_for_year("Freshman") | self._courses_for_year("Sophomore") | self._courses_for_year("Junior")
        return _filter(opts, self.sn_his, self.senior_ap_count >= 3, prior)
            
      
    @rx.var
    def sn_ec_opts(self) -> list[str]:
        opts = [#"AP Macroeconomics with Government", 
                #"AP Microeconomics with Government", 
                "Economics"]
        prior = self._courses_for_year("Freshman") | self._courses_for_year("Sophomore") | self._courses_for_year("Junior")
        return _filter(opts, self.sn_ec, self.senior_ap_count >= 3, prior)
    @rx.var
    def sn_gov_opts(self) -> list[str]:
        opts = ["AP US Government", "Participation in Government"]
        prior = self._courses_for_year("Freshman") | self._courses_for_year("Sophomore") | self._courses_for_year("Junior")
        return _filter(opts, self.sn_gov, self.senior_ap_count >= 3, prior)


MAJOR_COURSE_COLOR = req_courses


def course_card(label: str, course_name: str) -> rx.Component:
    color = MAJOR_COURSE_COLOR if label in required_courses_labels else PlannerState.dropdown_colors[course_name]
    return rx.box(
        rx.box(
            rx.text(label, class_name="card-label", color = "rgba(250, 250, 250, 0.7)"),
            rx.text(course_name, class_name="card-title"),
            class_name="course-card",
            style={
                "background_color": theme.lighter_aa_blue,
                "border": f"1px solid color-mix(in srgb, {color} 65%, grey 35%)"
            }
        ),
        on_click=PlannerState.open_course_details(course_name),
        style={"cursor": "pointer"}, class_name="card-spacing-wrapper",
    )
def elective_card(label: str, year: str) -> rx.Component:
    color = elective_color
    return rx.box(
        rx.box(
            rx.text("Elective Course", class_name="card-label", color = "rgba(250, 250, 250, 0.7)"), 
            rx.text(label, class_name="card-title"),
            class_name="course-card", 
            on_click=PlannerState.open_course_details(label), 
            style={"cursor": "pointer", "background_color" : theme.lighter_aa_blue, "border": f"1px solid color-mix(in srgb, {color} 60%, grey 40%)"}, 
        ),
        rx.button(
            "✕", 
            on_click=[rx.stop_propagation, PlannerState.delete_course(label, year)],
            variant="ghost", 
            size="1", 
            color_scheme="red",
            style={
                "position": "absolute", "top": "50%", "transform": "translateY(-50%)", 
                "right": "20px", "font_size": "20px", "cursor": "pointer", 
                "padding": "4px", "height": "auto", "z_index": "10"
            }
            ),
        class_name="card-spacing-wrapper", 
        style={"position": "relative", "width": "100%"}
    )    
def dropdown_card(label: str, options: list[str], value: rx.Var, on_change: any) -> rx.Component:
    color = MAJOR_COURSE_COLOR if label in required_courses_labels else PlannerState.dropdown_colors[value]
    return rx.box(
        rx.box(
            rx.text(label, class_name="card-label", font_size="13px",color = "rgba(250, 250, 250, 0.7)"),
            rx.select(options, value=value, on_change=on_change, variant="ghost", class_name="reflex-dropdown-select", on_click=[rx.stop_propagation], font_size = "15px" ),
            class_name="dropdown-card-wrapper",
            style={
                "background_color": theme.lighter_aa_blue,
                "border": f"1px solid color-mix(in srgb, {color} 60%, grey 40%)"
            }
        ),
        on_click=PlannerState.open_course_details(value),
        style={"cursor": "pointer"}, class_name="card-spacing-wrapper",
    )
def deletable_dropdown_card(label: str, options: list[str], value: rx.Var, on_change: any, on_delete: any) -> rx.Component:
    color = MAJOR_COURSE_COLOR if label in required_courses_labels else PlannerState.dropdown_colors[value]
    return rx.box(
        rx.box(
            rx.text(label, class_name="card-label", color = "rgba(250, 250, 250, 0.7)"),
            rx.select(
                options, value=value, on_change=on_change, variant="ghost",
                class_name="reflex-dropdown-select", on_click=[rx.stop_propagation]
            ),
            class_name="dropdown-card-wrapper",
            on_click=PlannerState.open_course_details(value),
            style={
                "cursor": "pointer",
                "background_color": theme.lighter_aa_blue,
                "border": f"1px solid color-mix(in srgb, {color} 60%, grey 40%)"
            },
        ),
        rx.button(
            "✕",
            on_click=[rx.stop_propagation, on_delete],
            variant="ghost",
            size="1",
            color_scheme="red",
            style={
                "position": "absolute", "top": "50%", "transform": "translateY(-50%)",
                "right": "20px", "font_size": "20px", "cursor": "pointer",
                "padding": "4px", "height": "auto", "z_index": "10"
            }
        ),
        class_name="card-spacing-wrapper",
        style={"position": "relative", "width": "100%"},
    )

def course_detail_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.box(
                rx.vstack(
                    # 1. Top Header Row: Course Title & Close Button
                    rx.hstack(
                        rx.text(PlannerState.active_modal_course["name"], font_size="25px", weight="bold", color="#fafafa"),
                        rx.spacer(),
                        rx.button(
                            "✕", 
                            variant="ghost", 
                            color_scheme="gray", 
                            on_click=PlannerState.close_course_details, 
                            style={"cursor": "pointer", "font_size": "16px"}
                        ),
                        width="100%",
                        align_items="center"
                    ),
                    
                    # 2. Badges Row: Perfectly matches your Explore Page design
                    rx.hstack(
                        # Semester Length Badge
                        rx.badge(
                            rx.cond(PlannerState.active_modal_course["semesters"] == "1", "1 semester", "2 semesters"),
                            color_scheme="purple", 
                            variant="soft", 
                            radius="full",
                            size="3",
                            style={"font_size": "14px", "padding": "6px 12px"}
                        ),
                        # Period Badge
                        rx.badge(
                            rx.cond(
                                PlannerState.active_modal_course["periods"] == "1",
                                "1 period",
                                f"{PlannerState.active_modal_course['periods']} periods"
                            ),
                            color_scheme="orange", 
                            variant="soft", 
                            radius="full",
                            size="3",
                            style={"font_size": "14px", "padding": "6px 12px"}
                        ),
                        # Credits Badge
                        rx.badge(
                            f"{PlannerState.active_modal_course['credits']} credits",
                            color_scheme="teal",
                            variant="soft",
                            radius="full",
                            size="3",
                            style={"font_size": "14px", "padding": "6px 12px"}
                        ),
                        # Elective Badge
                        rx.cond(
                            PlannerState.active_modal_course["is_elective"],
                            rx.badge(
                                "Elective", 
                                color_scheme="pink", 
                                variant="soft", 
                                radius="full",
                                size="3",
                                style={"font_size": "14px", "padding": "6px 12px"}
                            )
                        ),
                        # Grade Badges (Dynamic)
                        rx.foreach(
                            PlannerState.active_modal_course["grade_badges"].to(list[str]),
                            lambda grade: rx.badge(
                                grade, 
                                color_scheme="blue", 
                                variant="soft", 
                                radius="full",
                                size="3",
                                style={"font_size": "14px", "padding": "6px 12px"}
                            )
                        ),
                                        
                        spacing="3",
                        margin_top="6px",
                        margin_bottom="12px"
                    ),
                    
                    # 3. Full Un-truncated Description: No line limits, lets long text run completely free
                    rx.text(
                        PlannerState.active_modal_course["description"], 
                        font_size="20px", 
                        color="white", 
                        line_height="1.6",
                        margin_top="4px"
                    ),
                    
                    
                    
                    align_items="start",
                    spacing="3",
                    width="100%"
                ),
                # Stretched layout style that mirrors the explore card structure beautifully but wider
                style={
                    "background_color": "#1f2937",   
                    "border": "1px solid #25354c",     
                    "border_radius": "12px",
                    "padding": "24px",
                    "width": "100%",
                    "height": "100%"
                }
            ),
            # Controls the overall modal container container boundaries (comfortable desktop size)
            style={
                "max_width": "900px", 
                "width": "90vw",
                
                "height" : "auto",
                "max_height": "900px",
                "background": "transparent", 
                "padding": "0", 
                "border": "none"
            }
        ),
        open=PlannerState.is_detail_open,
        on_open_change=lambda _: PlannerState.close_course_details(),
    )

def render_modal_course_row(course: dict, target_year: str) -> rx.Component:
    is_added = rx.cond(
        target_year == "Freshman",
        PlannerState.freshman_electives.contains(course["name"]),
        rx.cond(
            target_year == "Sophomore",
            PlannerState.sophomore_electives.contains(course["name"]),
            rx.cond(
                target_year == "Junior",
                PlannerState.junior_electives.contains(course["name"]),
                PlannerState.senior_electives.contains(course["name"])
            )
        )
    )
    
    return rx.box(
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text(course["name"], font_weight="700", font_size="16px", color=rx.cond(course["disabled"], "#52525b", "#fafafa")), 
                        rx.badge(
                            rx.cond(
                                course['periods'] == 1,
                                f"{course['periods']} period",
                                f"{course['periods']} periods"
                            ),
                            color_scheme=rx.cond(course["disabled"], "gray", "orange"), 
                            variant="soft", 
                            radius="full"
                        ),
                        spacing="2"
                    ),
                    rx.text(course["description"], font_size="14px", color=rx.cond(course["disabled"], "#51515c", "#ffffff"), max_lines=1, margin_top="2px"),
                    align_items="start",
                ),
                on_click=lambda: PlannerState.open_course_details(course["name"]),
                style={"cursor": rx.cond(course["disabled"], "not-allowed", "pointer")}, 
                width="100%"
            ),
            rx.spacer(),
            rx.cond(
                course["disabled"],
                rx.button("No room", color_scheme="gray", size="2", variant="soft", style={"cursor": "not-allowed", "opacity": "0.5", "pointer_events": "none"}),
                rx.cond(
                    is_added,
                    rx.button("Delete", on_click=lambda: PlannerState.delete_course(course["name"], target_year), color_scheme="red", variant="soft", size="1", style={"cursor": "pointer"}),
                    rx.button("Add", on_click=lambda: PlannerState.add_course(course["name"], target_year), color_scheme="blue", size="1", style={"cursor": "pointer"})
                )
            ),
            align_items="center", width="100%"
        ),
        border_bottom="1px solid #1f2937", padding_y="10px", width="100%",
        opacity=rx.cond(course["disabled"], "0.5", "1.0")
    )

def course_search_modal(period_count: rx.Var, target_year: str) -> rx.Component:
    active_button = rx.dialog.trigger(
        rx.button(
            "Add Course",
            on_click=lambda: PlannerState.open_search_for_grade(target_year),
            width="100%", margin_top="0px",
            style={
                "background_color": "#2563eb1a", "color": "#60a5fa", 
                "font_weight": "600", "cursor": "pointer",
                "_hover": {"background_color": "#2563eb33"}
            }
        )
    )

    disabled_button = rx.button(
        "Schedule Full (8/8 Pds)",
        width="100%", margin_top="0px",
        style={
            "background_color": "#2c2d30", "color": "#c3c3cf", 
            "font_weight": "600", "cursor": "not-allowed",
            "opacity": "0.6",
            "font_size" : "16px"
        }
    )

    return rx.dialog.root(
        rx.cond(
            period_count >= 8,
            disabled_button,
            active_button
        ),
        rx.dialog.content(
            rx.hstack(rx.dialog.title("Add Course", margin="0"), rx.spacer(), rx.dialog.close(rx.button("✕", variant="ghost", color_scheme="gray", style={"cursor": "pointer"})), width="100%"),
            rx.input(placeholder="Search courses...", on_change=PlannerState.set_search_query, margin_y="16px", width="100%", size="3"),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(PlannerState.filtered_catalog, lambda course: render_modal_course_row(course, target_year)),
                    width="100%", align_items="stretch"
                ),
                style={"max_height": "400px"}
            ),
            style={"max_width": "750px", "background_color": "#1f2937", "border": "1px solid #31353f", "padding": "20px"}
        )
    )

# ====================== VIEW GENERATION ======================

@rx.page(route="/", title="BTHS Planner - Plan", on_load=PlannerState.change_tab("Plan")) 
def index() -> rx.Component:
    plan_content = rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Course Plan", font_size="35px", color="#fafafa", margin_bottom="12px"),
                legend_bar(),
                rx.text("Note: Gym and Lunch are mandatory, so they are not shown for simplicity. There are technically 10 periods in a day.", font_size = "18px", font_style = "italic")
            ),
            rx.spacer(),
            rx.vstack(
                rx.text("Select your major", class_name="card-label", color = "white", font_size = "15px", font_weight = "bold"),
                styled_select(MAJORS, PlannerState.major, PlannerState.change_major, "15px"),
                rx.box(rx.text("View majors ", rx.link("here", href="https://www.bths.edu/apps/pages/index.jsp?uREC_ID=222176&type=d&termREC_ID=&pREC_ID=1201473f", is_external=True, color="white", text_decoration="underline"),font_weight="600", color="white", as_="span", size="2")),
                background_color=theme.lighter_aa_blue, padding="10px", border_radius="0.5rem", border="1px solid #31353f", width="255px", spacing="1",
                ),
        ),
        rx.hstack(
            rx.text("Select which credits you already have:", font_weight="bold", color="white", font_size="20px"),
            pre_credit_checkbox("Algebra I"),
            pre_credit_checkbox("Geometry"),
            pre_credit_checkbox("US History"),
            pre_credit_checkbox("Biology/Living Environment"),
            pre_language_checkbox(),

            align_items="center",
            spacing="5",
            padding="12px 0px",
            background_color="#0F172A",
            border_radius="8px",
            margin_top="10px",
        ),
        rx.grid(
            
            rx.hstack(
                
                rx.vstack(
                    #rx.hstack((rx.text("English:\n8 semesters of English", white_space = "pre-wrap")),(rx.text("History:\n4 semesters of Global History\n2 semesters of US History\n1 semester of Economics\n1 semester of Government", white_space = "pre-wrap")),(rx.text("Mathematics:\n2 semesters of Algebra 1\n2 semesters of Geometry\n2 semesters of Algebra 2", white_space = "pre-wrap"))),
                    rx.cond(PlannerState.major_note != "", rx.callout(rx.text(PlannerState.major_note, font_size = "16px"), icon="info", color_scheme="blue",)),
                    rx.cond(PlannerState.chose_economics_jr, rx.callout(rx.text("*Taking Economics in junior year requires students to have already passed the United States History Regents exam.", font_size = "16px"), icon="info", color_scheme="purple", margin_bottom="12px", font_size = "16px")),
                    rx.cond(PlannerState.chose_african_jr, rx.callout(rx.text("*Taking AP African American Studies in junior year requires students to have already passed the United States History Regents exam.", font_size = "16px"), icon="info", color_scheme="purple", margin_bottom="12px")),
                ),
                align="start",
                spacing="3",
            ),

            rx.grid(
                # --- FRESHMAN ---
                rx.vstack(
                    rx.heading("Freshman", size="7", margin_bottom="2px", color="#fafafa"),
                    rx.hstack(
                        rx.text(PlannerState.freshman_course_count.to(str) + " courses", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.freshman_periods.to(str) + "/8 periods", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.freshman_ap_count.to(str) + "/3 APs", size="3", color=rx.cond(PlannerState.freshman_ap_count >= 3, "#f87171", "white"), weight = "medium"),
                        spacing="2", margin_bottom="10px"
                    ),
                    
                    course_card("English Course", "English 9"),
                    rx.cond(PlannerState.major_has_aphg,
                        course_card("History Course", "Pre-AP World History"),
                        dropdown_card("History Course", DropdownOptions.f_hist_opts, PlannerState.f_hist, PlannerState.change_f_hist),),
                    dropdown_card("Science Course", DropdownOptions.f_sci_opts, PlannerState.f_sci, PlannerState.change_f_sci),
                    rx.foreach(
                        PlannerState.freshman_math_courses,
                        lambda course: course_card("Math Course", course)
                    ),
                    dropdown_card("Language Course", language_opts, PlannerState.f_lang, PlannerState.change_f_lang),
                    course_card("Required Course", "Design & Drafting for Production (DDP)"),
                    rx.vstack(
                        rx.foreach(
                            PlannerState.freshman_electives,
                            lambda course: elective_card(course, "Freshman")
                            ),
                        course_search_modal(PlannerState.freshman_periods, "Freshman"),
                        width="100%", 
                        spacing="3",
                        margin_top="0px"
                    ),
                    align_items="stretch"
                ),

                # --- SOPHOMORE ---
                rx.vstack(
                    rx.heading("Sophomore", size="7", margin_bottom="2px", color="#fafafa"),
                    rx.hstack(
                        rx.text(PlannerState.sophomore_course_count.to(str) + " courses", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.sophomore_periods.to(str) + "/8 periods", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.sophomore_ap_count.to(str) + "/3 APs", size="3", color=rx.cond(PlannerState.sophomore_ap_count >= 3, "#f87171", "white"), weight = "medium"),
                        spacing="2", margin_bottom="10px"
                    ),
                    
                    dropdown_card("English Course", DropdownOptions.so_eng_opts, PlannerState.so_eng, PlannerState.change_so_eng),
                    dropdown_card("History Course", DropdownOptions.so_hist_opts, PlannerState.so_hist, PlannerState.change_so_hist),
                    course_card("Science Course", "Regents Chemistry"),
                    rx.cond(PlannerState.math_is_accelerated, course_card("Math Course", "Pre-Calculus"), course_card("Math Course", "Algebra II")),
                    rx.cond(PlannerState.lang_is_accelerated, course_card("Language Course", PlannerState.language_base + " III"), course_card("Language Course", PlannerState.language_base + " II")),
                    course_card("Required Course", "AP Computer Science Principles"),
                    course_card("Required Course", "Health Education"),
                    rx.vstack(
                        rx.foreach(
                            PlannerState.sophomore_electives,
                            lambda course: elective_card(course, "Sophomore")
                        ),
                        course_search_modal(PlannerState.sophomore_periods, "Sophomore"),
                        width="100%", 
                        spacing="3",
                        margin_top="0px"
                    ),
                    align_items="stretch"
                ),

               # --- JUNIOR ---
                rx.vstack(
                    rx.heading("Junior", size="7", margin_bottom="2px", color="#fafafa"),
                    rx.hstack(
                        rx.text(PlannerState.junior_course_count.to(str) + " courses", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.junior_periods.to(str) + "/8 periods", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.junior_ap_count.to(str) + "/3 APs", size="3", color=rx.cond(PlannerState.junior_ap_count >= 3, "#f87171", "white"), weight = "medium"),
                        spacing="2", margin_bottom="10px"
                    ),
                    
                    
                    rx.cond(
                        PlannerState.major != "LIU Pharmacy",
                        dropdown_card("English Course", DropdownOptions.j_eng_opts, PlannerState.j_eng, PlannerState.change_j_eng),
                        rx.fragment()
                    ),
                    dropdown_card("History Course", DropdownOptions.j_his_opts, PlannerState.j_his, PlannerState.change_j_his),
                    rx.cond(
                        PlannerState.chose_economics_jr & ~PlannerState.has_econ_gov_conflict & ~PlannerState.chose_government_jr & ~PlannerState.has_gov_conflict,
                        course_card("Government Course", "Participation in Government")
                    ),
                    rx.cond(
                        PlannerState.need_regents_physics_junior,
                        rx.cond(
                            PlannerState.junior_ap_room_for_physics,
                            dropdown_card("Science Course", DropdownOptions.j_phys_opts, PlannerState.j_phys, PlannerState.change_j_phys),
                            course_card("Science Course", "Regents Physics")
                        )
                    ),
                    
                    # 2. 🎯 STANDALONE MATH SLOT: Safe fallback logic. Only shows up down here if it wasn't pulled into the major stack above!
                    rx.cond(
                        PlannerState.junior_math_override == "",
                        #rx.cond(
                            #PlannerState.math_is_accelerated,
                            #course_card("Math Course", "AP Calculus BC"),
                        dropdown_card("Math Course", DropdownOptions.j_math_opts, PlannerState.j_math, PlannerState.change_j_math)
                        
                    ),
                    
                    rx.cond(~PlannerState.lang_is_accelerated, course_card("Language Course", PlannerState.language_base + " III")),
                    
# 1. 🎯 MAJOR SEQUENCE SLOTS: Only pulls math up if a major math requirement exists
                    rx.cond(
                        PlannerState.junior_math_override != "",
                        dropdown_card("Major Course", DropdownOptions.j_math_opts, PlannerState.j_math, PlannerState.change_j_math)
                    ),
                                                
                    rx.foreach(PlannerState.filtered_junior_major_courses, lambda course: course_card("Major Course", course)),
                              
                    
                   
                    rx.vstack(
                        rx.foreach(
                            PlannerState.junior_electives,
                            lambda course: elective_card(course, "Junior")
                            ),
                        course_search_modal(PlannerState.junior_periods, "Junior"),
                        width="100%", 
                        spacing="3",
                        margin_top="0px"
                    ),
                    align_items="stretch"
                ),

                
                # --- SENIOR ---
                # --- SENIOR COLUMN ---
                rx.vstack(
                    rx.heading("Senior", size="7", margin_bottom="2px", color="#fafafa"),
                    rx.hstack(
                        rx.text(PlannerState.senior_course_count.to(str) + " courses", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.senior_periods.to(str) + "/8 periods", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.senior_ap_count.to(str) + "/3 APs", size="3", color=rx.cond(PlannerState.senior_ap_count >= 3, "#f87171", "white"), weight = "medium"),
                        spacing="2", margin_bottom="10px"
                    ),
                    
                    dropdown_card("English Course", DropdownOptions.sn_eng_opts, PlannerState.sn_eng, PlannerState.change_sn_eng),
                    rx.cond(
                        ~PlannerState.chose_economics_jr & ~PlannerState.has_macro,
                        rx.fragment(
                            dropdown_card("History Course", DropdownOptions.sn_his_opts, PlannerState.sn_his, PlannerState.change_sn_his),
                            rx.cond(
                                ((PlannerState.sn_his == "AP US Government") | (PlannerState.sn_his == "Participation in Government")) & ~PlannerState.chose_economics_jr & ~PlannerState.has_econ_gov_conflict, 
                                course_card("Economics Course", PlannerState.sn_ec)),
                            rx.cond(
                                (PlannerState.sn_his == "Economics") & ~PlannerState.chose_government_jr & ~PlannerState.has_gov_conflict, 
                                dropdown_card("Government Course", DropdownOptions.sn_gov_opts, PlannerState.sn_gov, PlannerState.change_sn_gov)),
                        ),
                    ),
                #NON-MAJOR MATH SLOT (Only displays for majors that DO NOT have math in their major requirements)
                    rx.cond(
                        PlannerState.senior_math_override == "",
                        rx.cond(
                            PlannerState.took_ap_calc_bc_junior,
                            rx.tooltip(
                                rx.box(
                                    dropdown_card("Math Course", DropdownOptions.sn_math_opts, PlannerState.sn_math, PlannerState.change_sn_math),
                                    rx.button(
                                        rx.cond(PlannerState.sn_math_active, "✕", "＋"),
                                        on_click=PlannerState.toggle_sn_math,
                                        variant="ghost", size="1",
                                        color_scheme=rx.cond(PlannerState.sn_math_active, "red", "green"),
                                        style={
                                            "position": "absolute", "top": "40px", "transform": "translateY(-50%)",
                                            "right": "20px", "font_size": "20px", "cursor": "pointer",
                                            "padding": "4px", "height": "auto", "z_index": "10"
                                        }
                                    ),
                                    style={"position": "relative", "margin_bottom": "0px", "width": "100%", "opacity": rx.cond(PlannerState.sn_math_active, "1.0", "0.4")}
                                ),
                                content = "Taking Math all four years is highly encouraged",
                                #style={"font_size": "20px !important"}
                            ),
                            dropdown_card("Math Course", DropdownOptions.sn_calcs, PlannerState.sn_math, PlannerState.change_sn_math),
                        )
                    ),
                    # MAJOR COURSES SECTION
                    rx.cond(
                        PlannerState.major == "Physics",
                        # Physics Major View (Kept intact)
                        rx.vstack(
                            rx.tooltip(
                                rx.box(
                                    rx.box(
                                        rx.text("Major Course", class_name="card-label"),
                                        rx.text("AP Physics II", class_name="card-title"),
                                        class_name="course-card",
                                        on_click=PlannerState.open_course_details("AP Physics II"),
                                        style={"cursor": "pointer", "background_color": theme.lighter_aa_blue, "border": f"1px solid color-mix(in srgb, {MAJOR_COURSE_COLOR} 85%, white 15%)"}
                                    ),
                                    rx.button(
                                        rx.cond(PlannerState.selected_senior_physics.contains("AP Physics II"), "✕", "＋"),
                                        on_click=lambda: PlannerState.toggle_senior_physics("AP Physics II"),
                                        variant="ghost", size="1",
                                        color_scheme=rx.cond(PlannerState.selected_senior_physics.contains("AP Physics II"), "red", "green"),
                                        is_disabled=(PlannerState.selected_senior_physics.length() == 1) & PlannerState.selected_senior_physics.contains("AP Physics II"),
                                        style={
                                            "position": "absolute", "top": "40px", "transform": "translateY(-50%)",
                                            "right": "20px", "font_size": "20px", "cursor": "pointer",
                                            "padding": "4px", "height": "auto", "z_index": "10"
                                        }
                                    ),
                                    style={"position": "relative", "margin_bottom": "15px", "width": "100%", "opacity": rx.cond(PlannerState.selected_senior_physics.contains("AP Physics II"), "1.0", "0.4")}
                                ),
                                content="You must keep at least one AP Physics",
                            ),
                            rx.tooltip(
                                rx.box(
                                    rx.box(
                                        rx.text("Major Course", class_name="card-label"), 
                                        rx.text("AP Physics C: Electricity & Magnetism", class_name="card-title"),
                                        class_name="course-card", 
                                        on_click=PlannerState.open_course_details("AP Physics C: Electricity & Magnetism"), 
                                        style={"cursor": "pointer", "background_color": theme.lighter_aa_blue, "border": f"1px solid color-mix(in srgb, {MAJOR_COURSE_COLOR} 85%, white 15%)"}
                                    ),
                                    rx.button(
                                        rx.cond(PlannerState.selected_senior_physics.contains("AP Physics C: Electricity & Magnetism"), "✕", "＋"), 
                                        on_click=lambda: PlannerState.toggle_senior_physics("AP Physics C: Electricity & Magnetism"),
                                        variant="ghost", size="1", 
                                        color_scheme=rx.cond(PlannerState.selected_senior_physics.contains("AP Physics C: Electricity & Magnetism"), "red", "green"),
                                        is_disabled=(PlannerState.selected_senior_physics.length() == 1) & PlannerState.selected_senior_physics.contains("AP Physics C: Electricity & Magnetism"),
                                        style={
                                            "position": "absolute", "top": "40px", "transform": "translateY(-50%)", 
                                            "right": "20px", "font_size": "20px", "cursor": "pointer", 
                                            "padding": "4px", "height": "auto", "z_index": "10",
                                        }
                                    ),
                                    style={"position": "relative", "margin_bottom": "15px", "width": "100%", "opacity": rx.cond(PlannerState.selected_senior_physics.contains("AP Physics C: Electricity & Magnetism"), "1.0", "0.4")}
                                ),
                                content="You must keep at least one AP Physics"
                            ),
                            course_card("Major Course", "Modern Physics"),
                            width="100%", spacing="3", margin_top="0px"
                        ),

                        # Math major/ liu pharm math is a major course 
                        rx.vstack(
                            # Renders all major courses except math
                            rx.cond(
                                PlannerState.senior_math_override != "",
                                rx.cond(
                                    PlannerState.took_ap_calc_bc_junior,
                                    rx.cond(
                                        PlannerState.sn_math != "",
                                        dropdown_card("Major Course", DropdownOptions.sn_math_opts, PlannerState.sn_math, PlannerState.change_sn_math),
                                        rx.fragment()
                                        ),
                                    dropdown_card("Major Course", DropdownOptions.sn_calcs, PlannerState.sn_math, PlannerState.change_sn_math),
                                )
                            ),                            
                            
                            
                            rx.foreach(PlannerState.filtered_senior_major_courses, lambda course: course_card("Major Course", course)),
                            
                            # If this major has a math requirement/override (e.g. Applied Math), place standard non-deletable dropdown inside Major Section
                            
                            width="100%", spacing="3", margin_top="0px"
                        )
                    ),

                    

                    # ELECTIVES SECTION
                    rx.vstack(
                        rx.foreach(
                            PlannerState.senior_electives,
                            lambda course: elective_card(course, "Senior")
                            ),
                        course_search_modal(PlannerState.senior_periods, "Senior"),
                        width="100%", 
                        spacing="3",
                        margin_top="0px"
                    ),
                    align_items="stretch",
                    spacing="3"
                ),
                columns={"initial": "1", "sm": "2", "md": "4"}, spacing="4", width="100%"
            ),
            grid_template_columns={"initial": "1fr", "md": "1fr 3fr"}, spacing="5", width="100%",
        ),

        course_detail_modal(),
        rx.divider(margin_y="32px", border_color="#31353f"),
        
        
        #rx.hstack(
            #rx.vstack(rx.text("Total Courses Planned", color="rgba(250, 250, 250, 0.6)", size="2"), rx.heading(PlannerState.total_course_count.to(str), color="#fafafa", size="6"), align_items="start", spacing="1"),
            #rx.vstack(rx.text("Total Credits Planned", color="rgba(250, 250, 250, 0.6)", size="2"), rx.heading(PlannerState.total_credit_count.to(str), color="#fafafa", size="6"), align_items="start", spacing="1"),
            #rx.spacer(), rx.text("By Everett Whidden", size="2", color="rgba(250, 250, 250, 0.4)"), align_items="center", width="100%"
            #not using these anymore tbh
       # ),

        
        width="100%",
        align_items="stretch"
    )
    return navigation_layout(plan_content)



@rx.page(route="/explore", title="BTHS Planner - Explore Courses", on_load=PlannerState.change_tab("Explore")) 
def explore_page() -> rx.Component:
    explore_content = rx.vstack(
        rx.vstack(
            rx.heading("Explore Course Catalog", font_size="40px", color="#fafafa"),
            rx.text("Search and browse through all academic offerings at Brooklyn Tech.", color="white", size="3"),
            
            # Live Filter Search Field
            rx.input(
                placeholder="Search titles, descriptions or keywords...",
                on_change=PlannerState.set_search_query,
                value=PlannerState.search_query,
                width="100%",
                max_width="800",
                margin_top="12px",
                margin_bottom="10px",
                size="3",
        
                background_color = theme.lighter_aa_blue
            ),

            

            rx.text("Showing " + PlannerState.filtered_catalog_count.to_string() + " courses", color="rgba(250,250,250,0.5)", size="3"),
        ), 
        
        # Fixed Grid layout setup to ensure single search results maintain standard sizing instead of stretching
        rx.grid(
            rx.foreach(
                PlannerState.filtered_catalog,
                lambda course: rx.box(
                    rx.vstack(
                        # Header Row: Course Title on top, Badges side-by-side underneath
                        rx.vstack(
                            # 1. Course Name (Top line)
                            rx.text(course["name"], size="5", weight="bold", color="#fafafa"),
                            
                            # 2. Badges Row (Bottom line, side-by-side)
                            rx.hstack(
                                # Semester Length Badge
                                rx.badge(
                                    rx.cond(course["semesters"] == 1, "1 semester", "2 semesters"),
                                    color_scheme="purple", 
                                    variant="soft", 
                                    radius="full"
                                ),
                                # Period Badge
                                rx.badge(
                                    rx.cond(
                                        course['periods'] == 1,
                                        f"{course['periods']} period",
                                        f"{course['periods']} periods"
                                    ),
                                    color_scheme="orange", 
                                    variant="soft", 
                                    radius="full"
                                ),
                                rx.badge(
                                    f"{course['credits']} credits",
                                    color_scheme="teal", 
                                    variant="soft",
                                    radius = "full"
                                ),
                                rx.cond(
                                    course["is_elective"],
                                    rx.badge("Elective", color_scheme="pink", variant="soft", radius="full")
                                ),
                                rx.foreach(
                                    course["grade_badges"].to(list[str]),
                                    lambda grade: rx.badge(grade, color_scheme="blue", variant="soft", radius="full")
                                
                                ),
                            width="100%",
                            align_items="start",
                            spacing="1",
                            )
                        ),
                        
                        # Description Container with a smooth dark-grey fade overlay at the bottom
                        rx.box(
                            rx.text(
                                course["description"], 
                                size="2", 
                                color="rgba(250, 250, 250, 0.7)", 
                                margin_top="8px"
                            ),
                            # Gradient overlay fading  into the card color 
                            rx.box(
                                position="absolute",
                                bottom="0",
                                left="0",
                                right="0",
                                height="30px",
                                background="linear-gradient(to bottom, rgba(30, 32, 37, 0) 0%, #1f2937 100%)",
                                pointer_events="none",
                            ),
                            position="relative",
                            height="75px",          
                            overflow="hidden",
                            width="100%",
                        ),
                        
                        
                        
                        rx.spacer(),
                        
                        # Action Button Context
                        rx.button(
                            "View Details",
                            width="100%",
                            background_color="#2563eb",
                            color="white",
                            cursor="pointer",
                            margin_top="16px",
                            on_click=lambda: PlannerState.open_course_details(course["name"])
                        ),
                        align_items="start",
                        height="100%",
                        spacing="2",
                    ),
                    background_color=theme.lighter_aa_blue,   # lighter aa blue for card bg
                    border="1px solid #31353f",     # Seamless matching border lines
                    border_radius="12px",
                    padding="24px",
                    # Standardized explicit sizing constraints
                    height="230px",                
                    width="100%",
                    max_width="800px",              # Keeps boxes from stretching super wide when 1 remains!
                    overflow="hidden",
                )
            ),
            # Standardized layout settings for the responsive grid
            columns={"sm": "1", "md": "2"},
            spacing="6",
            width="100%",
            justify_items="start",                  # Standardizes columns alignment
        ),
        
        course_detail_modal(),
        
        align_items="start",
        width="100%"
    )
    return navigation_layout(explore_content)

# ---------------------------------------------------------------------
# HOW IT WORKS CONTENT
# Just edit this list to add/remove/change sections. Each dict becomes
# one subheading + paragraph on the page, in order.
# "rule" (optional, True/False) makes it render like a sub-rule, indented
# under the "Rules" heading with a smaller/orange heading color.
# ---------------------------------------------------------------------
HOW_IT_WORKS_SECTIONS = [
    {
        "heading": "What is BTHS Planner?",
        "body": "BTHS Planner is built for Brooklyn Technical High School students to accurately simulate their 4-year schedule. This tool uses required core classes, major specific tracks, and electives to calculate course count, period count, and AP count. BTHS Planner is designed to enforce the credits and classes necessary for Brooklyn Tech students to recieve a Brooklyn Tech Diploma (more down below), which sets them up for a rigorous schedule that allows them to excel and stand out to colleges and universities.",
    },
    {
        "heading": "Selecting Major",
        "body": "Brooklyn Tech requires students to commit to a specific major track starting junior year. You can think of your major at Brooklyn Tech as the classes that you will be required to take during your junior and senior years. Use the drop-down menu at the top of the 'Plan' tab to pick a major. Changing your major will reset your junior and senior year schedules and swap them with the mandatory courses for that major. Swapping majors will also reset all other edited/added courses in order to meet the necessary constraints such as the 3 AP limit, 8 maximum periods, and more.",
    },
    {
        "heading": "Credits",
        "body": "At Brooklyn Tech, students are expected to take rigorous courses throughout their four years. Students are scheduled to complete an advanced regents diploma, as well as take additional courses in order to earn their Brooklyn Tech Diploma. This means earning a total of 44 credits and passing regents exams. These can be done throughout middle school and high school. These credits are described below.\n\n1 credit = 1 semester\n2 semesters = 1 year",
        "rule": True,
    },
    {
        "heading": "English (8 credits)",
        "body" : "• 8 semesters of English Language Arts (ELA)",
        "desc" : True
    },
    {
        "heading": "History (8 credits)",
        "body" : "• 4 semesters of Global History\n• 2 semesters of US History\n• 1 semester of Participation in Government\n• 1 semester of Economics",
        "desc" : True
    },
    {
        "heading": "Mathematics (6 credits)",
        "body": "• 2 semesters of Algebra 1\n• 2 semesters of Geometry\n• 2 semesters of Algebra II",

        "desc" : True
    },
    {
        "heading": "Science (6 credits)",
        "body": "• 2 semesters of Biology\n• 2 semesters of Physics\n• 2 semesters of Chemistry",

        "desc" : True
    },
    {
        "heading": "World Languages (6 credits)",
        "body": "• 6 semesters of Chinese, French, German, Italian, or Spanish.",
        "desc" : True
    },
    {
        "heading": "Arts & Engineering (2 credits)",
        "body": "• 2 semesters of Design & Drafting for Production (DDP)",
        "desc" : True
    },
    {
        "heading": "Computer Science (2 credits)",
        "body": "• 2 semesters of AP Computer Science Principles",
        "desc" : True
    },
    {
        "heading": "Physical Education (4 credits; 1 semester = 0.5 credits)",
        "body": "• 8 semesters of PE",
        "desc" : True
    },
    {
        "heading": "Health Education (1 credit)",
        "body": "• 1 semester of Health Education",
        "desc" : True
    },
    {
        "heading": "Major Courses and Electives (3 credits)",
        "body": "• Varies by major\n• Major courses cover elective requirement",
        "desc" : True
    },
    {
        "heading": "Period Limit",
        "body": "A standard day cannot exceed 10 periods. Excluding a mandatory lunch period and gym rotation period (gym, lab, free period, advisory for a semester), each student has 8 available periods that can be spent in class. Classes can be 1 or 2 periods. To see class information, you can either click on the class card in your plan, or go through the Explore page. Gym and lunch are not listed as periods for the sake of simplicity.",
        "rule": True,
    },
    {
        "heading": "AP Limit",
        "body": "Advanced Placement courses are highly demanding, so Brooklyn Tech imposes a limit of 3 AP classes per year.",
        "rule": True,
    },
    {
        "heading": "Electives",
        "body": "Elective courses allow you to customize your schedule, but they can only be added if you have open periods left in your 8 period limit (excluding lunch & gym periods) after your mandatory major and required courses.",
        "rule": True,
    },
]


def how_it_works_section(section: dict) -> rx.Component:
    is_desc = section.get("desc", False)
    return rx.vstack(
        rx.heading(
            section["heading"],
            font_size="22px" if is_desc else "28px",
            color="#ffffff", #if is_rule else "#3b82f6",
            margin_bottom="8px",
        ),
        rx.text(section["body"], color="#ffffffff") if section["body"] else rx.fragment(),
        align_items="start",
        font_size = "20px",
        spacing="1",
        width="100%",
        white_space="pre-line",
        padding_left="20px" if is_desc else "0px",
        margin_bottom="20px",
    )


@rx.page(route="/how-it-works", title="BTHS Planner - How It Works", on_load=PlannerState.change_tab("How It Works"))
def how_it_works_page() -> rx.Component:
    how_it_works_content = rx.vstack(
        # Page Header
        rx.heading("How It Works", font_size="40px", margin_bottom="8px", color="#ffffff"),
        rx.text(
            "Welcome to BTHS Planner! Here is a quick guide on how to navigate the planner and successfully map out your Brooklyn Tech high school career.",
            color="#ffffffff",
            margin_bottom="24px",
            font_size = "20px"
        ),

        *[how_it_works_section(section) for section in HOW_IT_WORKS_SECTIONS],

        align_items="start",
        width="100%",
        max_width="900px",
        padding_bottom="40px"
    )
    return navigation_layout(how_it_works_content)


hide_watermark_style = {
    "div.__reflex": {
        "display": "none !important",
    },
    "div[style*='position: fixed'][style*='bottom:']:has(a[href*='reflex.dev'])": {
        "display": "none !important",
    },
    "a[href*='reflex.dev']": {
        "display": "none !important",
    }
}

# Update your app initialization to include the style overrides
app = rx.App(
    stylesheets=["/style.css"],
    style=hide_watermark_style,
    head_components=[
        rx.el.meta(property="og:image", content="https://www.bths.edu/pics/header_logo.png"),
        rx.el.meta(name="twitter:card", content="summary_large_image"),
        rx.el.meta(name="twitter:image", content="https://www.bths.edu/pics/header_logo.png"),
        rx.el.link(rel="icon", type="image/png", href="/favicon.ico"),
    ]
)
app.add_page(index)
rx.Model.create_all()
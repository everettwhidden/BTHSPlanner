import reflex as rx
from data.courses import MAJORS

import bthsplanner.theme as theme
from bthsplanner.backend import *
from bthsplanner.components import (
    navigation_layout,
    course_card,
    elective_card,
    dropdown_card,
    plan_sidebar,
    sidebar_toggle_button,
    course_detail_modal,
    course_search_modal,
    pre_credit_checkbox,
    pre_language_checkbox,
    styled_select,
    render_major_course,
    order_dropdown,
    filter_dropdowns,
    senior_physics_cards,
    toggle_dropdown_card
)

# --- FRESHMAN ---
def freshman_column(): 
    return (
        rx.vstack(
        rx.heading("Freshman", size="5", margin_bottom="2px", color=theme.text),
        rx.hstack(
            rx.text(PlannerState.freshman_course_count.to(str) + " courses", font_size="13px", color=theme.text, weight = "bold"),
            rx.text("•", font_size="13px", color=theme.text),
            rx.text(PlannerState.freshman_periods.to(str) + "/10 periods", font_size="13px", color=theme.text, weight = "bold"),
            rx.text("•", font_size="13px", color=theme.text),
            rx.text(PlannerState.freshman_ap_count.to(str) + "/3 APs", font_size="13px", color=rx.cond(PlannerState.freshman_ap_count >= 3, "#f87171", theme.text), weight = "bold"),
            spacing="1", margin_bottom="10px"
        ),

        rx.tooltip(
            course_card("English", "English 9"),
            content = "Double period, alternates daily with DDP"
        ),

        course_card("History", "Pre-AP World History"),
            
        rx.cond(
            PlannerState.pre_credits["Biology/Living Environment"],
            dropdown_card("Science", DropdownOptions.f_sci_opts, PlannerState.f_sci, PlannerState.change_f_sci),
            course_card("Science", PlannerState.f_sci),),

        rx.foreach(
            PlannerState.freshman_math_courses,
            lambda course: course_card("Math", course)
        ),
        course_card("Language", PlannerState.f_lang),
        rx.tooltip(
            course_card("Required", "Design & Drafting for Production (DDP)"),
            content = "Double period, alternates daily with English 9"
        ),
        rx.vstack(
            rx.foreach(
                PlannerState.freshman_electives,
                lambda course: elective_card(course, "Freshman")
                ),
            course_card("Gym/Lunch", "Gym"),
            course_card("Gym/Lunch", "Lunch"),                            
            course_search_modal(PlannerState.freshman_periods, "Freshman"),
            width="100%", 
            spacing="3",
            margin_top="0px"
        ),
        align_items="stretch",
        **theme.year_box
        ),
    )
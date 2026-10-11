import reflex as rx
from data.courses.catalog import MAJORS

import bthsplanner.theme as theme
from bthsplanner.old_state import PlannerState, DropdownOptions, MAJOR_COURSE_COLOR
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

def sophomore_column():
    return(
        rx.vstack(
        rx.heading("Sophomore", size="5", margin_bottom="2px", color=theme.text),
        rx.hstack(
            rx.text(PlannerState.sophomore_course_count.to(str) + " courses", size="2", color=theme.text, weight = "bold"),
            rx.text("•", size="2", color=theme.text),
            rx.text(PlannerState.sophomore_periods.to(str) + "/10 periods", size="2", color=theme.text, weight = "bold"),
            rx.text("•", size="2", color=theme.text),
            rx.text(PlannerState.sophomore_ap_count.to(str) + "/3 APs", size="2", color=rx.cond(PlannerState.sophomore_ap_count >= 3, "#f87171", theme.text), weight = "bold"),
            spacing="2", margin_bottom="10px"
        ),
        
        dropdown_card("English", DropdownOptions.so_eng_opts, PlannerState.so_eng, PlannerState.change_so_eng),
        dropdown_card("History", DropdownOptions.so_hist_opts, PlannerState.so_hist, PlannerState.change_so_hist),
        course_card("Science", "Regents Chemistry"),
        rx.cond(PlannerState.math_is_accelerated, course_card("Math", "Pre-Calculus"), course_card("Math", "Algebra II")),
        rx.cond(PlannerState.lang_is_accelerated, course_card("Language", PlannerState.language_base + " III"), course_card("Language", PlannerState.language_base + " II")),
        course_card("Required", "AP Computer Science Principles"),
        course_card("Required", "Health Education"),
        rx.vstack(
            rx.foreach(
                PlannerState.sophomore_electives,
                lambda course: elective_card(course, "Sophomore")
            ),
            course_card("Required", "Gym"),
            course_card("Required", "Lunch"),                        
            course_search_modal(PlannerState.sophomore_periods, "Sophomore"),
            width="100%", 
            spacing="3",
            margin_top="0px"
        ),
        align_items="stretch"
    ),
)
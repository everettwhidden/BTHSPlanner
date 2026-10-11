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

def junior_column():
    return(
    rx.vstack(
        rx.heading("Junior", size="5", margin_bottom="2px", color=theme.text),
        rx.hstack(
            rx.text(PlannerState.junior_course_count.to(str) + " courses", size="2", color=theme.text, weight = "bold"),
            rx.text("•", size="2", color=theme.text),
            rx.text(PlannerState.junior_periods.to(str) + "/10 periods", size="2", color=theme.text, weight = "bold"),
            rx.text("•", size="2", color=theme.text),
            rx.text(PlannerState.junior_ap_count.to(str) + "/3 APs", size="2", color=rx.cond(PlannerState.junior_ap_count >= 3, "#f87171", theme.text), weight = "bold"),
            spacing="2", margin_bottom="10px"
        ),
        
        
        rx.cond(
            PlannerState.major != "LIU Pharmacy",
            dropdown_card("English", DropdownOptions.j_eng_opts, PlannerState.j_eng, PlannerState.change_j_eng),
            rx.fragment()
        ),
        rx.cond(
            (PlannerState.j_his == "None (free period, econ senior year)") | (PlannerState.j_his == "None (free period, gov senior year)"),
            rx.fragment(),
            dropdown_card("History", DropdownOptions.j_his_opts, PlannerState.j_his, PlannerState.change_j_his),
        ),
        rx.cond(
            PlannerState.chose_economics_jr & ~PlannerState.has_econ_gov_conflict & ~PlannerState.chose_government_jr & ~PlannerState.has_gov_conflict,
            course_card("Government", "Participation in Government")
        ),
        rx.cond(
            PlannerState.need_regents_physics_junior,
            rx.cond(
                PlannerState.junior_ap_room_for_physics,
                dropdown_card("Science", DropdownOptions.j_phys_opts, PlannerState.j_phys, PlannerState.change_j_phys),
                course_card("Science", "Regents Physics")
            )
        ),
        
        # 2. refular math card. safe fallback logic. Only shows up down here if it wasn't pulled into the major stack above!
        rx.cond(
            PlannerState.junior_math_override == "",
            #rx.cond(
                #PlannerState.math_is_accelerated,
                #course_card("Math", "AP Calculus BC"),
            dropdown_card("Math", DropdownOptions.j_math_opts, PlannerState.j_math, PlannerState.change_j_math)
            
        ),
        
        rx.cond(~PlannerState.lang_is_accelerated, course_card("Langauge", PlannerState.language_base + " III")),
        
    # 1. 🎯 MAJOR SEQUENCE SLOTS: Only pulls math up if a major math requirement exists
        rx.cond(
            PlannerState.junior_math_override != "",
            dropdown_card("Major", DropdownOptions.j_math_opts, PlannerState.j_math, PlannerState.change_j_math)
        ),
                                    

        rx.foreach(PlannerState.filtered_junior_major_courses, render_major_course),
            

        

        rx.vstack(
            rx.foreach(
                PlannerState.junior_electives,
                lambda course: elective_card(course, "Junior")
                ),
            course_card("Gym/Lunch", "Gym"),
            course_card("Gym/Lunch", "Lunch"),
            course_search_modal(PlannerState.junior_periods, "Junior"),
            width="100%", 
            spacing="3",
            margin_top="0px"
        ),
        align_items="stretch"
    ),
)
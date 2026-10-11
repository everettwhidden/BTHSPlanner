import reflex as rx
from data.courses import MAJORS

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

# --- SENIOR COLUMN ---
def senior_column():
    return(
    rx.vstack(
        rx.heading("Senior", size="5", margin_bottom="2px", color=theme.text),
        rx.hstack(
            rx.text(PlannerState.senior_course_count.to(str) + " courses", size="2", color=theme.text, weight = "bold"),
            rx.text("•", size="2", color=theme.text),
            rx.text(PlannerState.senior_periods.to(str) + "/10 periods", size="2", color=theme.text, weight = "bold"),
            rx.text("•", size="2", color=theme.text),
            rx.text(PlannerState.senior_ap_count.to(str) + "/3 APs", size="2", color=rx.cond(PlannerState.senior_ap_count >= 3, "#f87171", theme.text), weight = "bold"),
            spacing="2", margin_bottom="10px"
        ),
        
        dropdown_card("English", DropdownOptions.sn_eng_opts, PlannerState.sn_eng, PlannerState.change_sn_eng),
        rx.cond(
            ~PlannerState.chose_economics_jr & ~PlannerState.has_macro & ~PlannerState.chose_gov_jr_finance,
            rx.fragment(
                dropdown_card("History", DropdownOptions.sn_his_opts, PlannerState.sn_his, PlannerState.change_sn_his),
                rx.cond(
                    ((PlannerState.sn_his == "AP US Government") | (PlannerState.sn_his == "Participation in Government") | (PlannerState.sn_his == "AP Comparative Government")) & ~PlannerState.chose_economics_jr & ~PlannerState.has_econ_gov_conflict, 
                    course_card("Economics", PlannerState.sn_ec)),
                rx.cond(
                    (PlannerState.sn_his == "Economics") & ~PlannerState.chose_government_jr & ~PlannerState.has_gov_conflict, 
                    dropdown_card("Government", DropdownOptions.sn_gov_opts, PlannerState.sn_gov, PlannerState.change_sn_gov)),
            ),
        ),
    #NON-MAJOR MATH SLOT (Only displays for majors that DO NOT have math in their major requirements)
        rx.cond(
            PlannerState.senior_math_override == "",
            rx.cond(
                PlannerState.took_ap_calc_bc_junior,
                toggle_dropdown_card(
                    "Math",
                    DropdownOptions.sn_math_opts,
                    PlannerState.sn_math,
                    PlannerState.change_sn_math,
                    selected=PlannerState.sn_math_active,
                    on_toggle=PlannerState.toggle_sn_math,
                    tooltip="Taking Math all four years is highly encouraged",
                ),
                dropdown_card("Math", DropdownOptions.sn_calcs, PlannerState.sn_math, PlannerState.change_sn_math),
            )
        ),
        # MajorS SECTION
        rx.cond(
            PlannerState.major == "Physics",
            senior_physics_cards(),


            rx.vstack(
                rx.cond(
                    PlannerState.senior_math_override != "",
                    rx.cond(
                        PlannerState.took_ap_calc_bc_junior,
                        rx.cond(
                            PlannerState.sn_math != "",
                            dropdown_card("Major", DropdownOptions.sn_math_opts, PlannerState.sn_math, PlannerState.change_sn_math),
                            rx.fragment()
                            ),
                        dropdown_card("Major", DropdownOptions.sn_calcs, PlannerState.sn_math, PlannerState.change_sn_math),
                    )
                ),

                rx.foreach(PlannerState.filtered_senior_major_courses, render_major_course),

                width="100%", spacing="3", margin_top="0px"
            )
        ),

        

        # ELECTIVES SECTION
        rx.vstack(
            rx.foreach(
                PlannerState.senior_electives,
                lambda course: elective_card(course, "Senior")
                ),
            course_card("Required", "Gym"),
            course_card("Required", "Lunch"),
            course_search_modal(PlannerState.senior_periods, "Senior"),
            width="100%", 
            spacing="3",
            margin_top="0px"
        ),
        align_items="stretch",
        spacing="3"
    ),
)
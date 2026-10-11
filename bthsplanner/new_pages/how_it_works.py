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


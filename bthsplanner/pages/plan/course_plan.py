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
from .freshman import freshman_column
from .sophomore import sophomore_column
from .junior import junior_column
from .senior import senior_column

@rx.page(route="/", title="BTHS Planner - Plan Your Courses", description="Simulate and plan your 4-year high school course schedule at Brooklyn Tech.", on_load=PlannerState.change_tab("Plan")) 
def index() -> rx.Component:
    plan_content = rx.hstack(
        plan_sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("Course Plan", font_size="30px", color=theme.text),
                rx.cond(
                    PlannerState.major_note != "",
                    rx.callout(rx.text(PlannerState.major_note, font_size="16px"), icon="info", color_scheme="blue"),
                ),
                rx.grid(
                    freshman_column,
                    sophomore_column,
                    junior_column,
                    senior_column,
            
                    columns={"initial": "1", "sm": "2", "md": "2", "lg": "4"},
                    spacing="4",
                    width="100%",
                ),
                course_detail_modal(),
                spacing="5",
                width="100%",
                align_items="stretch",
            ),
            # these belong on the box, not the vstack
            flex="1",
            min_width="0",
            padding_top="32px",       # gap between nav bar and the heading / cards
            padding_bottom="32px",
            padding_left="32px",      # gap between sidebar and the cards
            padding_right="32px",
        ),
        align="start",
        spacing="0",
        width="100%",
    )
    return navigation_layout(plan_content, full_width=True)
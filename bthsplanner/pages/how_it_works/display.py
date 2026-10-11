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
from .content import HOW_IT_WORKS_SECTIONS

def how_it_works_section(section: dict) -> rx.Component:
    is_desc = section.get("desc", False)
    return rx.vstack(
        rx.heading(
            section["heading"],
            font_size="22px" if is_desc else "28px",
            color=theme.text,
            margin_bottom="8px",
        ),
        rx.text(section["body"], color=theme.text) if section["body"] else rx.fragment(),
        align_items="start",
        font_size = "20px",
        spacing="1",
        width="100%",
        white_space="pre-line",
        padding_left="20px" if is_desc else "0px",
        margin_bottom="20px",
    )


@rx.page(route="/how-it-works", title="BTHS Planner - How It Works", description="Learn about how BTHS Planner works.",on_load=PlannerState.change_tab("How It Works"))
def how_it_works_page() -> rx.Component:
    how_it_works_content = rx.vstack(
        # Page Header
        rx.heading("How It Works", font_size="30px", margin_bottom="8px", color=theme.text),
        rx.text(
            "Welcome to BTHS Planner! Here is a quick guide on how to navigate the planner and successfully map out your Brooklyn Tech high school career.",
            color=theme.text,
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

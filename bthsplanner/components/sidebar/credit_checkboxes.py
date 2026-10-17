import reflex as rx

import bthsplanner.theme as theme
from data.courses import (
    language_opts
)
from bthsplanner.backend import PlannerState
from .styled_select import styled_select

required_courses_labels = ["Major Course", "Required Course"]

def pre_credit_checkbox(label: str) -> rx.Component:
    return rx.hstack(
        rx.checkbox(
            checked=PlannerState.pre_credits[label],
            on_change=PlannerState.toggle_pre_credit(label),
        ),
        rx.text(label, color=theme.text, font_size="15px", font_weight="600"),
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
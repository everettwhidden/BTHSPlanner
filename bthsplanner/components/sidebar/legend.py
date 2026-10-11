import reflex as rx

import bthsplanner.theme as theme
from data.courses import (
    elective_color,
    lang_color,
    science_color,
    math_color,
    history_color,
    english_color,
    language_opts,
    req_courses,
    gym_lunch_color,
    alternates_with_gym,
    MAJORS
)
from bthsplanner.old_state import PlannerState, DropdownOptions, MAJOR_COURSE_COLOR, MAJOR_NAMES

required_courses_labels = ["Major Course", "Required Course"]

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
            color=theme.text, 
            font_size="15px",
            font_weight="600",
        ),
        align_items="center",
        spacing="2",
    )

def legend_list() -> rx.Component:
    # vertical version of the legend for the sidebar
    return rx.vstack(
        legend_item("English", english_color),
        legend_item("History", history_color),
        legend_item("Science", science_color),
        legend_item("Math", math_color),
        legend_item("Language", lang_color),
        legend_item("Major/Required", req_courses),
        legend_item("Elective", elective_color),
        legend_item("Gym/Lunch", gym_lunch_color),
        align_items="start",
        spacing="2",
    )

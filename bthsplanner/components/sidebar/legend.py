import reflex as rx

import bthsplanner.theme as theme
from data.courses import (
    elective_color,
    lang_color,
    science_color,
    math_color,
    history_color,
    english_color,
    req_courses,
    gym_lunch_color
)
from bthsplanner.backend import *

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
            font_size="14px",
            font_weight="600",
        ),
        align_items="center",
        spacing="2",
    )

def legend_list() -> rx.Component:
    # two columns for the sidebar
    return rx.grid(
        legend_item("English", english_color),
        legend_item("History", history_color),
        legend_item("Science", science_color),
        legend_item("Math", math_color),
        legend_item("Language", lang_color),
        legend_item("Required", req_courses),
        legend_item("Elective", elective_color),
        legend_item("Gym/Lunch", gym_lunch_color),
        columns="2",
        spacing="2",
        width="100%",
    )

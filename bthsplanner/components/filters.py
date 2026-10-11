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
from bthsplanner.backend import *

required_courses_labels = ["Major Course", "Required Course"]

GRADE_OPTIONS = ["Freshman", "Sophomore", "Junior", "Senior"]
ORDER_OPTIONS = ["AP First", "A-Z"]
FILTER_OPTIONS = ["Electives", "Non-electives"]

def checkbox_option(label: str, checked: rx.Var, on_change: any) -> rx.Component:
    return rx.hstack(
        rx.checkbox(checked=checked, on_change=on_change),
        rx.text(label, color=theme.text, font_size="18px", font_weight="600"),
        align_items="center",
        spacing="2",
    )


def filter_popover(trigger_label, *items) -> rx.Component:
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                trigger_label,
                rx.icon("chevron-down", size=20),
                
                style={
                    "background_color": theme.lighter_aa_blue,
                    "border": f"1px solid {theme.border}",
                    "color": theme.text,
                    "font_weight": "600",
                    "font_size" : "18px"

                },
            )
        ),
        rx.popover.content(
            rx.vstack(*items, align="start", spacing="2"),
            max_height="900px",
            overflow_y="auto",
            style={"background_color": theme.lighter_aa_blue, "border": f"1px solid {theme.border}"},
        ),
    )


def order_option(label: str) -> rx.Component:
    return rx.text(
        rx.hstack(
            rx.radio_group.item(value=label),
            label,
            align_items="center",
            spacing="2",
        ),
        as_="label",
        color= theme.text,
        font_size="18px",
        font_weight="600",
    )



def order_dropdown() -> rx.Component:
    return filter_popover(
        rx.cond(PlannerState.order == "A-Z", "Sort by: A-Z", "Sort by: AP First"),
        rx.radio_group.root(
            rx.vstack(
                *[order_option(o) for o in ORDER_OPTIONS],
                align="start",
                spacing="3",
            ),
            value=PlannerState.order,
            on_change=PlannerState.set_order,
            size="3",
        ),
    )

def elective_dropdown() -> rx.Component:
    count = PlannerState.selected_filters.length()
    return filter_popover(
        rx.cond(count > 0, "Filters (" + count.to_string() + ")", "Filter"),
        *[
            checkbox_option(f, PlannerState.selected_filters.contains(f), PlannerState.toggle_filter(f))
            for f in FILTER_OPTIONS
        ],
    )

def grade_dropdown() -> rx.Component:
    count = PlannerState.selected_grades.length()
    return filter_popover(
        rx.cond(count > 0, "Grades (" + count.to_string() + ")", "Grade"),
        *[
            checkbox_option(g, PlannerState.selected_grades.contains(g), PlannerState.toggle_grade(g))
            for g in GRADE_OPTIONS
        ],
    )


def major_dropdown() -> rx.Component:
    count = PlannerState.selected_majors.length()
    return filter_popover(
        rx.cond(count > 0, "Majors (" + count.to_string() + ")", "Major"),
        *[
            checkbox_option(m, PlannerState.selected_majors.contains(m), PlannerState.toggle_major(m))
            for m in MAJOR_NAMES
        ],
    )


def filter_dropdowns() -> rx.Component:
    return rx.hstack(
        #order_dropdown(),
        grade_dropdown(),
        major_dropdown(),
        elective_dropdown(),
        spacing="3",
        align="center",
        flex_shrink="0",
    )
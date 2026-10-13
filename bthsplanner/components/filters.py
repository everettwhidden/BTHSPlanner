import reflex as rx

import bthsplanner.theme as theme
from data.courses import *
from bthsplanner.backend import *
from bthsplanner.components import styled_select
required_courses_labels = ["Major Course", "Required Course"]

GRADE_OPTIONS = ["Freshman", "Sophomore", "Junior", "Senior"]
ORDER_OPTIONS = ["A-Z", "AP First"]
FILTER_OPTIONS = ["AP", "Elective", "Non-elective"]
PERIOD_LENGTH_OPTIONS = ["1 period", "2 periods"]
SEMESTER_OPTIONS = ["1 semester", "2 semesters"]

def checkbox_option(label, checked, on_click, font_size="16px", font_weight="600"):
    # visual-only checkbox, the row handles the click
    box = rx.box(
        rx.cond(
            checked,
            rx.icon("check", size=12, color="white"),
        ),
        width="16px",
        height="16px",
        flex_shrink="0",
        display="flex",
        align_items="center",
        justify_content="center",
        border_radius="4px",
        border=rx.cond(checked, "2px solid #3b82f6", f"2px solid #A5A5AD"),
        background_color=rx.cond(checked, "#3b82f6", "transparent"),
    )
    return rx.box(
        rx.hstack(
            box,
            rx.text(
                label,
                font_size=font_size,
                color=theme.text,
                font_weight=font_weight,
            ),
            spacing="2",
            align_items="center",
        ),
        width="100%",
        padding="8px 12px",
        min_height="36px",
        border_radius="6px",
        cursor="pointer",
        on_click=on_click,
        _hover={"background_color": "rgba(128, 128, 128, 0.2)"},
    )

def filter_popover(trigger_label, *items) -> rx.Component:
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.hstack(
                    rx.text(trigger_label, font_size="16px", font_weight="600px"),
                    rx.spacer(),
                    rx.icon("chevron-down", size=13),
                    width="100%",
                    align_items="center",
                ),
                style={
                    "background_color": theme.illini_blue,
                    "border": f"1px solid {theme.border}",
                    "color": theme.text,
                    "height": "42px",           # Adjust button height here (e.g., "36px" for smaller, "48px" for larger)
                    "width": "100%",
                    "padding": "10px 14px",
                    "border_radius": "12px",
                },
            )
        ),
        rx.popover.content(
            rx.vstack(*items, align="start", spacing="2"),
            max_height="300px",
            width="240px",
            overflow_y="auto",
            style={"background_color": theme.illini_blue, "border": f"1px solid {theme.border}"},
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
        font_size="15px",
        font_weight="600",
    )

def filter_dropdown(trigger_label: rx.Component | str, *items: rx.Component, font: str = "15px", width: str = "100%") -> rx.Component:
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.hstack(
                    rx.text(trigger_label, font_size=font, font_weight="600"),
                    rx.spacer(),
                    rx.icon("chevron-down", size=18, color=theme.text),
                    width="100%",
                    align_items="center",
                ),
                style={
                    "background_color": theme.lighter_aa_blue,
                    "padding": "12px 10px",
                    "border": f"1px solid {theme.border}",
                    "box_shadow": "none",
                    "border_radius": "0.5rem",
                    "width": width,
                    "font_weight": "600",
                    "color": theme.text,
                    "cursor": "pointer",
                    "_hover": {"background_color": "rgba(128, 128, 128, 0.25) !important"},
                },
            )
        ),
        rx.popover.content(
            rx.vstack(*items, align="start", spacing="2"),
            max_height="300px",
            width="260px",
            overflow_y="auto",
            side="bottom",
            align="start",
            style={
                "background_color": theme.lighter_aa_blue,
                "border": f"1px solid {theme.border}",
                "border_radius": "0.5rem",
                "padding": "5px",
            },
        ),
    )

def order_dropdown() -> rx.Component:
    return filter_dropdown(
        PlannerState.order,
        *[
            rx.box(
                rx.text(
                    option,
                    font_size="14px",
                    font_weight=rx.cond(PlannerState.order == option, "600", "500"),
                    color=rx.cond(PlannerState.order == option, "#3b82f6", theme.text)
                ),
                width="100%",
                padding="10px 8px",
                border_radius="6px",
                cursor="pointer",
                background_color=rx.cond(
                    PlannerState.order == option,
                    "rgba(59, 130, 246, 0.15)",
                    "transparent"
                ),
                on_click=lambda _, opt=option: PlannerState.set_order(opt),
                # selected rows stay blue on hover, just a bit stronger
                _hover={
                    "background_color": rx.cond(
                        PlannerState.order == option,
                        "rgba(59, 130, 246, 0.25)",
                        "rgba(128, 128, 128, 0.2)"
                    )
                },
            )
            for option in ORDER_OPTIONS
        ],
    )
def grade_dropdown() -> rx.Component:
    count = PlannerState.selected_grades.length()
    label = rx.cond(count > 0, "Grades (" + count.to_string() + ")", "Select grade")
    return filter_dropdown(
        label,
        *[
            checkbox_option(g, PlannerState.selected_grades.contains(g), PlannerState.toggle_grade(g), "14px")
            for g in GRADE_OPTIONS
        ],
    )

def type_dropdown() -> rx.Component:
    count = PlannerState.selected_filters.length()
    label = rx.cond(count > 0, "Type (" + count.to_string() + ")", "Select class type")
    return filter_dropdown(
        label,
        *[
            checkbox_option(f, PlannerState.selected_filters.contains(f), PlannerState.toggle_filter(f), "14px")
            for f in FILTER_OPTIONS
        ],
    )

def major_dropdown() -> rx.Component:
    count = PlannerState.selected_majors.length()
    label = rx.cond(count > 0, "Major (" + count.to_string() + ")", "Select major")
    return filter_dropdown(
        label,
        *[
            checkbox_option(m, PlannerState.selected_majors.contains(m), PlannerState.toggle_major(m), "14px")
            for m in MAJOR_NAMES
        ],
    )
def period_length_dropdown() -> rx.Component:
    count = PlannerState.selected_period_length.length()
    label = rx.cond(count > 0, "Selected Periods (" + count.to_string() + ")", "Select periods")
    return filter_dropdown(
        label,
        *[
            checkbox_option(p, PlannerState.selected_period_length.contains(p), PlannerState.toggle_period_length(p), "14px")
            for p in PERIOD_LENGTH_OPTIONS
        ],
    )

def semester_dropdown() -> rx.Component:
    count = PlannerState.selected_semesters.length()
    label = rx.cond(count > 0, "Semesters (" + count.to_string() + ")", "Select semesters")
    return filter_dropdown(
        label,
        *[
            checkbox_option(s, PlannerState.selected_semesters.contains(s), PlannerState.toggle_semester(s), "14px")
            for s in SEMESTER_OPTIONS
        ],
    )


def _sidebar_title(label: str) -> rx.Component:
    return rx.text(label, font_weight="bold", color=theme.text, font_size="15px")


def explore_sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Top Header Row: "Filters" Title + "Clear" Button
            rx.hstack(
                rx.heading("Filters", font_size="22px", font_weight="bold", color=theme.text),
                rx.spacer(),
                rx.button(
                    "Clear",
                    variant="ghost",
                    color_scheme="blue",
                    size="2",
                    on_click=PlannerState.clear_filters,  # Add your clear filters event handler here
                    style={"cursor": "pointer", "font_weight": "600"},
                ),
                width="100%",
                align_items="center",
            ),
            
            # 1. Sort By
            rx.vstack(
                _sidebar_title("Sort By"),
                order_dropdown(),
                width="100%",
                spacing="2",
                align_items="start",
            ),

            # 2. Grade / Class Level
            rx.vstack(
                _sidebar_title("Grade"),
                grade_dropdown(),
                width="100%",
                spacing="2",
                align_items="start",
            ),

            # 3. Type
            rx.vstack(
                _sidebar_title("Type"),
                type_dropdown(),
                width="100%",
                spacing="2",
                align_items="start",
            ),

            # 4. Major
            rx.vstack(
                _sidebar_title("Major"),
                major_dropdown(),
                width="100%",
                spacing="2",
                align_items="start",
            ),
            # 5. Periods
            rx.vstack(
                _sidebar_title("Periods"),
                period_length_dropdown(),
                width="100%",
                spacing="2",
                align_items="start",
            ),

            # 6. Semesters
            rx.vstack(
                _sidebar_title("Semesters"),
                semester_dropdown(),
                width="100%",
                spacing="2",
                align_items="start",
            ),

            align_items="start",
            spacing="5",
            padding="20px 16px",
            width="100%",
        ),
        width="280px",
        height="calc(100vh - 57px)",
        position="sticky",
        top="57px",
        align_self="flex-start",
        flex_shrink="0",
        overflow_y="auto",
        overflow_x="hidden",
        background_color=theme.lighter_aa_blue,
        border_right=f"1px solid {theme.border}",
        margin="0",
    )
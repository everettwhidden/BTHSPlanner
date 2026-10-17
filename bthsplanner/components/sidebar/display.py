import reflex as rx

import bthsplanner.theme as theme
from data.courses import (
    MAJORS
)
from bthsplanner.backend import PlannerState

from .styled_select import styled_select
from .credit_checkboxes import (pre_language_checkbox, pre_credit_checkbox)
from .legend import (legend_list)

required_courses_labels = ["Major Course", "Required Course"]

def sidebar_section_title(label: str) -> rx.Component:
    return rx.text(label, font_weight="bold", color=theme.text, font_size="18px")


def sidebar_toggle_button() -> rx.Component:
    return rx.icon_button(
        rx.cond(
            PlannerState.sidebar_open,
            rx.icon("panel-left-close", size=20),
            rx.icon("panel-left-open", size=20),
        ),
        on_click=PlannerState.toggle_sidebar,
        variant="ghost",
        color_scheme="gray",
        size="3",
        style={
            "cursor": "pointer",
            "color": theme.text,
            "background_color": "transparent",
            "border": "none",
            "box_shadow": "none",
            "outline": "none",
            "border_radius": "0.5rem",
            "margin": "0 !important",
            "_hover": {"background_color": "rgba(128, 128, 128, 0.25)"},
        },
    )

def plan_sidebar() -> rx.Component:
    return rx.box(
        # content fades out when collapsed
        rx.box(
            rx.vstack(
                sidebar_section_title("Major selection"),
                
                styled_select(MAJORS, PlannerState.major, PlannerState.change_major, "15px", "100%"),
                rx.text(
                    "View majors ",
                    rx.link(
                        "here",
                        href="https://www.bths.edu/apps/pages/index.jsp?uREC_ID=222176&type=d&termREC_ID=&pREC_ID=1201473f",
                        is_external=True,
                        color=theme.text,
                        text_decoration="underline",
                    ),
                    color=theme.text,
                    size="2",
                    font_weight="600",
                ),
                rx.divider(border_color=theme.border),
                

                sidebar_section_title("Credits already earned"),
                pre_credit_checkbox("Algebra I"),
                pre_credit_checkbox("Geometry"),
                pre_credit_checkbox("US History"),
                pre_credit_checkbox("Biology/Living Environment"),
                pre_language_checkbox(),
                rx.divider(border_color=theme.border),
                
                sidebar_section_title("Legend"),
                legend_list(),
                align_items="start",
                spacing="4",
                width="280px",      # fixed so it doesn't rewrap while sliding
                padding="16px",
            ),
            opacity=rx.cond(PlannerState.sidebar_open, "1", "0"),
            pointer_events=rx.cond(PlannerState.sidebar_open, "auto", "none"),
            transition="opacity 0.2s ease",
            overflow_y="auto",
            overflow_x="hidden",
            width="100%",
            height="100%",
        ),
        # toggle sits inside the sidebar, pinned to its right edge
        rx.box(
            sidebar_toggle_button(),
            position="absolute",
            top="12px",
            right="12px",
            z_index="20",
        ),
        width=rx.cond(PlannerState.sidebar_open, "280px", "56px"),
        height="calc(100vh - 57px)",    # 57px is the nav bar height
        position="sticky",
        top="57px",
        align_self="flex-start",
        flex_shrink="0",
        overflow="hidden",
        transition="width 0.25s ease",
        background_color=theme.lighter_aa_blue,
        border_right=f"1px solid {theme.border}",
    )

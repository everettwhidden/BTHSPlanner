import reflex as rx

import bthsplanner.theme as theme
from bthsplanner.backend import *

from bthsplanner.components import (
    navigation_layout,
    plan_sidebar,
    course_detail_modal,

)
from .freshman import freshman_column
from .sophomore import sophomore_column
from .junior import junior_column
from .senior import senior_column

@rx.page(route="/plan", title="BTHS Planner - Plan Your Courses", description="Simulate and plan your 4-year high school course schedule at Brooklyn Technical High School.", on_load=PlannerState.change_tab("Plan")) 
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
                    freshman_column(),
                    sophomore_column(),
                    junior_column(),
                    senior_column(),
            
                    columns={"initial": "1", "sm": "2", "md": "2", "lg": "4"},
                    spacing="3",
                    width="100%",
                ),
                rx.divider(border_color=theme.border),
                rx.text(
                    "All course information and data is found through online sources or from personal knowledge. Please contact your guidance counselor if you are unsure about any course data. Additionally, AI was used to summarize each course and create it's description. Because AI can make mistakes, some descriptions may be incorrect or inaccurate. If you notice any mistakes, please contact us directly.",
                    color=theme.text_dim,
                    size="1",
                    text_align="left",
                    width="100%",
                    max_width="600px",
                    margin_x="0px",
                    margin_top="16px",
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
            padding_left="20px",      # gap between sidebar and the cards
            padding_right="20px",
        ),
        align="start",
        spacing="0",
        width="100%",
    )
    return navigation_layout(plan_content, full_width=True)
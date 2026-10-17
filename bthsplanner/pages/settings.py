import reflex as rx
from data.courses import MAJORS

import bthsplanner.theme as theme
from bthsplanner.backend import PlannerState
from bthsplanner.components import (
    navigation_layout,
)

@rx.page(route="/settings", title="BTHS Planner - Settings", description="Provide Feedback • Change display • Settings", on_load=PlannerState.change_tab("Settings"))
def settings_page() -> rx.Component:
    settings_content = rx.vstack(
        rx.heading("Settings", font_size="30px", color=theme.text, margin_bottom="8px"),
        rx.spacer(),
        rx.heading("Provide Feedback", font_size = "28px", color=theme.text, margin_bottom="8px"),
        rx.text(
            "Noticed a bug or have any suggestions for features? ",
            rx.link(
                "Fill out this feedback form.",
                href="https://docs.google.com/forms/d/e/1FAIpQLSebmbV4Ce9doWAPPl86DheyuMYkaYKGf_dxDp0k2z1sfz0BSQ/viewform?usp=header",
                is_external=True,
                color=theme.text,
                text_decoration="underline",
            ),
            color=theme.text,
            font_size ="18px",
            font_weight="400",
            margin_bottom="8px"
        ),
        # appearance section
        rx.heading("Appearance", font_size="25px", color=theme.text, margin_bottom="8px"),
        rx.hstack(
            rx.vstack(
                rx.cond(
                    rx.color_mode == "light",
                    rx.text("Theme: Light", color=theme.text, size="3"),
                    rx.text("Theme: Dark", color=theme.text, size="3")
                ),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.switch(
                checked=rx.color_mode == "light",
                on_change=rx.toggle_color_mode,
            ),
            background_color=theme.lighter_aa_blue,
            padding="16px",
            border_radius="0.5rem",
            border=f"1px solid {theme.border}",
            width="200px",
            align="center",
        ),

        align_items="start",
        width="100%",
        max_width="900px",
        padding_bottom="40px",
    )
    return navigation_layout(settings_content)
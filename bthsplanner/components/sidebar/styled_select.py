import reflex as rx

import bthsplanner.theme as theme
from bthsplanner.backend import *

required_courses_labels = ["Major Course", "Required Course"]


def styled_select(options: list[str], value: rx.Var, on_change: any, font: str = "15px", width: str = "130px",) -> rx.Component:
    return rx.select.root(
        rx.select.trigger(
            class_name="reflex-dropdown-select",
            style={
                "background_color": theme.lighter_aa_blue,
                "padding": "15px 15px !important",
                "border": f"1px solid {theme.border}",
                "box_shadow": "none",   
                "border_radius": "0.5rem",
                "width": width,
                "font_weight": "600 !important",
                "background_image": "none !important",
                "font_size" : font
            },
        ),
        rx.select.content(
            *[rx.select.item(opt, value=opt) for opt in options]
        ),
        value=value,
        on_change=on_change,
    )
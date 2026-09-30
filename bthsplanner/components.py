"""
Reusable UI components for BTHS Planner.

Building blocks used by pages.py (course_card, dropdown_card, legend_bar,
navigation_layout, etc.). Imports state to wire up on_click/on_change
handlers, but never imports from pages.py.
"""
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
from bthsplanner.state import PlannerState, MAJOR_COURSE_COLOR, MAJOR_NAMES

required_courses_labels = ["Major Course", "Required Course"]


def styled_select(options: list[str], value: rx.Var, on_change: any, font: str = "18px", width: str = "160px",) -> rx.Component:
    return rx.select.root(
        rx.select.trigger(
            class_name="reflex-dropdown-select",
            style={
                "background_color": theme.illini_blue,
                "padding": "8px 12px !important",
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
            font_size="18px",
            font_weight="600",
        ),
        align_items="center",
        spacing="2",
    )

def legend_bar() -> rx.Component:
    """Main horizontal legend bar component."""
    return rx.hstack(
        # Main label
        rx.text(
            "Legend:",
            font_weight="bold",
            color=theme.text,
            font_size="20px",
            #margin_right="8px",
        ),
        # Color indicator items matching your image
        legend_item("English", english_color),  
        legend_item("History", history_color),   
        legend_item("Science", science_color),    
        legend_item("Math", math_color),  
        legend_item("Language", lang_color),   
        legend_item("Major/Required", req_courses),
        legend_item("Elective", elective_color), 
        legend_item("Gym/Lunch", gym_lunch_color),

        align_items="center",
        spacing="5",
        padding="12px 0px",
        background_color=theme.illini_blue,  # Dark background matching image
        border_radius="8px",
    )
def pre_credit_checkbox(label: str) -> rx.Component:
    return rx.hstack(
        rx.checkbox(
            checked=PlannerState.pre_credits[label],
            on_change=PlannerState.toggle_pre_credit(label),
        ),
        rx.text(label, color=theme.text, font_size="18px", font_weight="600"),
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
def nav_link(label: str, href: str) -> rx.Component:
    # one tab in the top nav, highlights when it's the active tab
    is_active = PlannerState.active_tab == label
    return rx.link(
        rx.text(
            label,
            size="5",
            color=rx.cond(is_active, theme.text, theme.text_dim),
            weight=rx.cond(is_active, "medium", "normal"),
        ),
        href=href,
        text_decoration="none",
        padding_x="12px",
        padding_y="8px",
        border_bottom=rx.cond(is_active, "2px solid #3b82f6", "2px solid transparent"),
    )

def navigation_layout(content: rx.Component) -> rx.Component:
    return rx.vstack(
        # Auth Modal Condition
        
        
        # Navigation Bar
        rx.box(
            rx.hstack(
                # Logo & Brand
                rx.hstack(
                    rx.image(
                        src="/header_logo.png",
                        width="55px",
                        height="55px",
                        object_fit="contain",
                        border_radius="4px",
                    ),
                    rx.text(
                        "BTHS Planner", size="7", weight="bold", color=theme.text,
                    ),
                    spacing="3",
                    align_items="center",
                ),
                # Navigation Links
                                
                rx.hstack(
                    nav_link("Plan", "/"),
                    nav_link("Explore", "/explore"),
                    nav_link("How It Works", "/how-it-works"),
                    nav_link("Settings", "/settings"),
                    spacing="4",
                    margin_left="24px",
                ),
                rx.spacer(),
                # Action Buttons
                rx.hstack(
                    
                    rx.button(
                        "Export to Excel",
                        on_click=PlannerState.export_to_excel,
                        color_scheme="blue",
                        size="3",
                    ),
                    
                    
                    spacing="3",
                    align_items="center",
                ),
                align_items="center",
                width="100%",
                max_width="1400px",
                margin="0 auto",
            ),
            position="sticky",
            top="0",
            z_index="100",
            background_color=theme.lighter_aa_blue,  # color of tab bar
            border_bottom=f"1px solid {theme.border}",
            padding_x="40px",
            padding_y="16px",
            width="100%",
        ),
        # Page Content Container
        rx.box(
            content,
            padding_x="32px",
            padding_y="40px",
            width="100%",
            max_width="1400px",
            margin="0 auto",
        ),
        width="100%",
        min_height="100vh",
        background_color=theme.illini_blue, #main color on every page 
        spacing="0",
    )


def course_card(label: str, course_name: str) -> rx.Component:
    color = MAJOR_COURSE_COLOR if label in required_courses_labels else PlannerState.dropdown_colors[course_name]
    return rx.box(
        rx.box(
            rx.text(label, class_name="card-label", color = theme.text),
            rx.text(course_name, class_name="card-title"),
            class_name="course-card",
            style={
                "background_color": theme.lighter_aa_blue,
                "border": f"2px solid color-mix(in srgb, {color} 85%, {theme.border} 15%)"
            }
        ),
        on_click=PlannerState.open_course_details(course_name),
        style={"cursor": "pointer"}, class_name="card-spacing-wrapper",
    )
def elective_card(label: str, year: str) -> rx.Component:
    color = elective_color
    return rx.box(
        rx.box(
            rx.text("Elective Course", class_name="card-label", color = theme.text), 
            rx.text(label, class_name="card-title"),
            class_name="course-card", 
            on_click=PlannerState.open_course_details(label), 
            style={"cursor": "pointer", "background_color" : theme.lighter_aa_blue, "border": f"2px solid color-mix(in srgb, {color} 85%, {theme.border} 15%)"}, 
        ),
        rx.button(
            "✕", 
            on_click=[rx.stop_propagation, PlannerState.delete_course(label, year)],
            variant="ghost", 
            size="1", 
            color_scheme="red",
            style={
                "position": "absolute", "top": "50%", "transform": "translateY(-50%)", 
                "right": "20px", "font_size": "20px", "cursor": "pointer", 
                "padding": "4px", "height": "auto", "z_index": "10"
            }
            ),
        class_name="card-spacing-wrapper", 
        style={"position": "relative", "width": "100%"}
    )    
def dropdown_card(label: str, options: list[str], value: rx.Var, on_change: any) -> rx.Component:
    color = MAJOR_COURSE_COLOR if label in required_courses_labels else PlannerState.dropdown_colors[value]
    return rx.box(
        rx.box(
            rx.text(label, class_name="card-label", font_size="13px",color = theme.text),
            rx.select(options, value=value, on_change=on_change, variant="ghost", class_name="reflex-dropdown-select", on_click=[rx.stop_propagation], font_size = "15px" ),
            class_name="dropdown-card-wrapper",
            style={
                "background_color": theme.lighter_aa_blue,
                "border": f"2px solid color-mix(in srgb, {color} 85%, {theme.border} 15%)"
            }
        ),
        on_click=PlannerState.open_course_details(value),
        style={"cursor": "pointer"}, class_name="card-spacing-wrapper",
    )

def render_major_course(course: rx.Var[str]) -> rx.Component:
    
    return rx.cond(
        PlannerState.partner_map.contains(course),
        rx.tooltip(
            course_card("Major Course", course),
            content=f"Double period, alternates daily with {PlannerState.partner_map[course]}",
        ),
        rx.cond(
            rx.Var.create(alternates_with_gym).contains(course),
            rx.tooltip(
                course_card("Major Course", course),
                content = "Double period, alternates daily with Gym"
            ),
        
        course_card("Major Course", course),
        ),
    )



def course_detail_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.box(
                rx.vstack(
                    # 1. Top Header Row: Course Title & Close Button
                    rx.hstack(
                        rx.text(PlannerState.active_modal_course["name"], font_size="25px", weight="bold", color=theme.text),
                        rx.spacer(),
                        rx.button(
                            "✕", 
                            variant="ghost", 
                            color_scheme="gray", 
                            on_click=PlannerState.close_course_details, 
                            style={"cursor": "pointer", "font_size": "16px"}
                        ),
                        width="100%",
                        align_items="center"
                    ),
                    
                    # 2. Badges Row: Perfectly matches your Explore Page design
                    rx.hstack(
                        # Semester Length Badge
                        rx.badge(
                            rx.cond(PlannerState.active_modal_course["semesters"] == "1", "1 semester", "2 semesters"),
                            color_scheme="purple", 
                            variant="soft", 
                            radius="full",
                            size="3",
                            style={"font_size": "14px", "padding": "6px 12px"}
                        ),
                        # Period Badge
                        rx.badge(
                            rx.cond(
                                PlannerState.active_modal_course["periods"] == "1",
                                "1 period",
                                f"{PlannerState.active_modal_course['periods']} periods"
                            ),
                            color_scheme="orange", 
                            variant="soft", 
                            radius="full",
                            size="3",
                            style={"font_size": "14px", "padding": "6px 12px"}
                        ),
                        # Credits Badge
                        rx.badge(
                            f"{PlannerState.active_modal_course['credits']} credits",
                            color_scheme="teal",
                            variant="soft",
                            radius="full",
                            size="3",
                            style={"font_size": "14px", "padding": "6px 12px"}
                        ),
                        # Elective Badge
                        rx.cond(
                            PlannerState.active_modal_course["is_elective"],
                            rx.badge(
                                "Elective", 
                                color_scheme="pink", 
                                variant="soft", 
                                radius="full",
                                size="3",
                                style={"font_size": "14px", "padding": "6px 12px"}
                            )
                        ),
                        # Grade Badges (Dynamic)
                        rx.foreach(
                            PlannerState.active_modal_course["grade_badges"].to(list[str]),
                            lambda grade: rx.badge(
                                grade, 
                                color_scheme="blue", 
                                variant="soft", 
                                radius="full",
                                size="3",
                                style={"font_size": "14px", "padding": "6px 12px"}
                            )
                        ),
                                        
                        spacing="3",
                        margin_top="6px",
                        margin_bottom="12px"
                    ),
                    
                    # 3. Full Un-truncated Description: No line limits, lets long text run completely free
                    rx.text(
                        PlannerState.active_modal_course["description"], 
                        font_size="20px", 
                        color=theme.text, 
                        line_height="1.6",
                        margin_top="4px"
                    ),
                    
                    
                    
                    align_items="start",
                    spacing="3",
                    width="100%"
                ),
                # Stretched layout style that mirrors the explore card structure beautifully but wider
                style={
                    "background_color": theme.lighter_aa_blue,   
                    "border": f"1px solid {theme.border}",     
                    "border_radius": "12px",
                    "padding": "24px",
                    "width": "100%",
                    "height": "100%"
                }
            ),
            # Controls the overall modal container container boundaries (comfortable desktop size)
            style={
                "max_width": "900px", 
                "width": "90vw",
                
                "height" : "auto",
                "max_height": "900px",
                "background": "transparent", 
                "padding": "0", 
                "border": "none"
            }
        ),
        open=PlannerState.is_detail_open,
        on_open_change=lambda _: PlannerState.close_course_details(),
    )

def render_modal_course_row(course: dict, target_year: str) -> rx.Component:
    is_added = rx.cond(
        target_year == "Freshman",
        PlannerState.freshman_electives.contains(course["name"]),
        rx.cond(
            target_year == "Sophomore",
            PlannerState.sophomore_electives.contains(course["name"]),
            rx.cond(
                target_year == "Junior",
                PlannerState.junior_electives.contains(course["name"]),
                PlannerState.senior_electives.contains(course["name"])
            )
        )
    )
    
    return rx.box(
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text(course["name"], font_weight="700", font_size="16px", color=rx.cond(course["disabled"], "#52525b", theme.text)), 
                        rx.badge(
                            rx.cond(
                                course['periods'] == 1,
                                f"{course['periods']} period",
                                f"{course['periods']} periods"
                            ),
                            color_scheme=rx.cond(course["disabled"], "gray", "orange"), 
                            variant="soft", 
                            radius="full"
                        ),
                        spacing="2"
                    ),
                    rx.text(course["description"], font_size="14px", color=rx.cond(course["disabled"], "#51515c", theme.text), max_lines=1, margin_top="2px"),
                    align_items="start",
                ),
                on_click=lambda: PlannerState.open_course_details(course["name"]),
                style={"cursor": rx.cond(course["disabled"], "not-allowed", "pointer")}, 
                width="100%"
            ),
            rx.spacer(),
            rx.cond(
                course["disabled"],
                rx.button("No room", color_scheme="gray", size="2", variant="soft", style={"cursor": "not-allowed", "opacity": "0.5", "pointer_events": "none"}),
                rx.cond(
                    is_added,
                    rx.button("Delete", on_click=lambda: PlannerState.delete_course(course["name"], target_year), color_scheme="red", variant="soft", size="1", style={"cursor": "pointer"}),
                    rx.button("Add", on_click=lambda: PlannerState.add_course(course["name"], target_year), color_scheme="blue", size="1", style={"cursor": "pointer"})
                )
            ),
            align_items="center", width="100%"
        ),
        border_bottom=f"1px solid {theme.border}", padding_y="10px", width="100%",
        opacity=rx.cond(course["disabled"], "0.5", "1.0")
    )

def course_search_modal(period_count: rx.Var, target_year: str) -> rx.Component:
    active_button = rx.dialog.trigger(
        rx.button(
            "Add Course",
            on_click=lambda: PlannerState.open_search_for_grade(target_year),
            width="100%", margin_top="0px",
            style={
                "background_color": "#2563eb1a", "color": "#60a5fa", 
                "font_weight": "600", "cursor": "pointer",
                "_hover": {"background_color": "#2563eb33"}
            }
        )
    )

    disabled_button = rx.button(
        "Schedule Full (10/10 Pds)",
        width="100%", margin_top="0px",
        style={
            "background_color": theme.lighter_aa_blue, "color": theme.text_dim, 
            "font_weight": "600", "cursor": "not-allowed",
            "opacity": "0.6",
            "font_size" : "16px"
        }
    )

    return rx.dialog.root(
        rx.cond(
            period_count >= 10,
            disabled_button,
            active_button
        ),
        rx.dialog.content(
            rx.hstack(rx.dialog.title("Add Course", margin="0"), rx.spacer(), rx.dialog.close(rx.button("✕", variant="ghost", color_scheme="gray", style={"cursor": "pointer"})), width="100%"),
            rx.input(placeholder="Search courses...", on_change=PlannerState.set_search_query, margin_y="16px", width="100%", size="3"),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(PlannerState.filtered_catalog, lambda course: render_modal_course_row(course, target_year)),
                    width="100%", align_items="stretch"
                ),
                style={"max_height": "400px"}
            ),
            style={"max_width": "750px", "background_color": theme.illini_blue, "border": f"1px solid {theme.border}", "padding": "20px"}
        )
    )

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
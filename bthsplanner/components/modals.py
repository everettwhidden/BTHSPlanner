import reflex as rx

import bthsplanner.theme as theme
from bthsplanner.backend import PlannerState

required_courses_labels = ["Major Course", "Required Course"]

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
            "background_color": theme.illini_blue, "color": theme.text_dim, 
            "font_weight": "600", "cursor": "not-allowed",
            "opacity": "0.6",
            "font_size" : "14px"
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
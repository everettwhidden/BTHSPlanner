import reflex as rx
from data.courses import MAJORS

import bthsplanner.theme as theme
from bthsplanner.backend import *
from bthsplanner.components import (
    navigation_layout,
    course_card,
    elective_card,
    dropdown_card,
    plan_sidebar,
    sidebar_toggle_button,
    course_detail_modal,
    course_search_modal,
    pre_credit_checkbox,
    pre_language_checkbox,
    styled_select,
    render_major_course,
    order_dropdown,
    filter_dropdowns,
    senior_physics_cards,
    toggle_dropdown_card,
    explore_sidebar
)
@rx.page(route="/explore", title="BTHS Planner - Explore Courses", description="Explore all of the course offerings at Brooklyn Technical High School.", on_load=PlannerState.change_tab("Explore")) 
def explore_page() -> rx.Component:
    explore_main = rx.vstack(
        rx.heading("Explore Courses", font_size="30px", margin_bottom="8px", color=theme.text),
        rx.input(
            placeholder="Search titles, descriptions or keywords...",
            on_change=PlannerState.set_explore_search_query,
            value=PlannerState.explore_search_query,
            width="100%",
            max_width="800px",
            margin_top="12px",
            margin_bottom="10px",
            size="3",
            background_color=theme.lighter_aa_blue,
        ),

        rx.text("Showing " + PlannerState.explore_catalog_count.to_string() + " courses", color="rgba(250,250,250,0.5)", size="3"),

        
        # Fixed Grid layout setup to ensure single search results maintain standard sizing instead of stretching
        rx.grid(
            rx.foreach(
                PlannerState.explore_catalog,
                lambda course: rx.box(
                    rx.vstack(
                        # Header Row: Course Title on top, Badges side-by-side underneath
                        rx.vstack(
                            # 1. Course Name (Top line)
                            rx.text(course["name"], size="5", weight="bold", color=theme.text),
                            
                            # 2. Badges Row (Bottom line, side-by-side)
                            rx.hstack(
                                # Semester Length Badge
                                rx.badge(
                                    rx.cond(course["semesters"] == 1, "1 semester", "2 semesters"),
                                    color_scheme="purple", 
                                    variant="soft", 
                                    radius="full"
                                ),
                                # Period Badge
                                rx.badge(
                                    rx.cond(
                                        course['periods'] == 1,
                                        f"{course['periods']} period",
                                        f"{course['periods']} periods"
                                    ),
                                    color_scheme="orange", 
                                    variant="soft", 
                                    radius="full"
                                ),
                                rx.badge(
                                    f"{course['credits']} credits",
                                    color_scheme="teal", 
                                    variant="soft",
                                    radius = "full"
                                ),
                                rx.cond(
                                    course["is_elective"],
                                    rx.badge("Elective", color_scheme="pink", variant="soft", radius="full")
                                ),
                                rx.foreach(
                                    course["grade_badges"].to(list[str]),
                                    lambda grade: rx.badge(grade, color_scheme="blue", variant="soft", radius="full")
                                
                                ),
                            width="100%",
                            align_items="start",
                            spacing="1",
                            )
                        ),
                        
                        # Description Container with a smooth dark-grey fade overlay at the bottom
                        rx.box(
                            rx.text(
                                course["description"], 
                                size="2", 
                                color=theme.text, 
                                margin_top="8px"
                            ),
                            # Gradient overlay fading  into the card color 
                            rx.box(
                                position="absolute",
                                bottom="0",
                                left="0",
                                right="0",
                                height="30px",
                                background=f"linear-gradient(to bottom, transparent 0%, {theme.lighter_aa_blue} 100%)",
                                pointer_events="none",
                            ),
                            position="relative",
                            height="75px",          
                            overflow="hidden",
                            width="100%",
                        ),
                        
                        
                        
                        rx.spacer(),
                        
                        # Action Button Context
                        rx.button(
                            "View Details",
                            width="100%",
                            background_color="#2563eb",
                            color="white",
                            cursor="pointer",
                            margin_top="16px",
                            on_click=lambda: PlannerState.open_course_details(course["name"])
                        ),
                        align_items="start",
                        height="100%",
                        spacing="2",
                    ),
                    background_color=theme.lighter_aa_blue,   # lighter aa blue for card bg
                    border=f"1px solid {theme.border}",     # Seamless matching border lines
                    border_radius="12px",
                    padding="24px",
                    # Standardized explicit sizing constraints
                    height="230px",                
                    width="100%",
                    max_width="800px",              # Keeps boxes from stretching super wide when 1 remains!
                    overflow="hidden",
                )
            ),
            # Standardized layout settings for the responsive grid
            columns={"sm": "1", "md": "2"},
            spacing="6",
            width="100%",
            justify_items="start",                  # Standardizes columns alignment
        ),
        
        course_detail_modal(),
        
        align_items="start",
        width="100%"
    )
    explore_content = rx.hstack(
        explore_sidebar(),
        rx.box(
            explore_main,
            flex="1",
            min_width="0",
            padding_x="32px",
            padding_y="25px",
        ),
        align="start",
        spacing="0",
        width="100%",
        margin="0",
    )
    return navigation_layout(explore_content, full_width = True)


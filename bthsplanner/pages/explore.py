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
    explore_sidebar
)
def pagination_bar() -> rx.Component:
    on_first = PlannerState.explore_page_num <= 1
    on_last = PlannerState.explore_page_num >= PlannerState.explore_total_pages
    return rx.hstack(
        rx.button(
            rx.icon("chevron-left", size=16),
            "Previous",
            on_click=PlannerState.prev_explore_page,
            disabled=on_first,
            variant="ghost",
            color_scheme="gray",
            size="3",
            style={
                "color": rx.cond(on_first, theme.text_dim, theme.text),
                "cursor": rx.cond(on_first, "not-allowed", "pointer"),
                "font_weight": "500",
            },
        ),
        rx.text(
            "Page ",
            rx.text.span(PlannerState.explore_page_num.to_string(), font_weight="700", color=theme.text),
            " of " + PlannerState.explore_total_pages.to_string(),
            color=theme.text_dim,
            size="3",
        ),
        rx.button(
            "Next",
            rx.icon("chevron-right", size=16),
            on_click=PlannerState.next_explore_page,
            disabled=on_last,
            variant="ghost",
            color_scheme="gray",
            size="3",
            style={
                "color": rx.cond(on_last, theme.text_dim, theme.text),
                "cursor": rx.cond(on_last, "not-allowed", "pointer"),
                "font_weight": "500",
            },
        ),
        justify="center",
        align="center",
        spacing="6",
        width="100%",
        margin_top="24px",
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

        rx.text(
            "Showing " + PlannerState.explore_page_count.to_string() + "/" + PlannerState.explore_catalog_count.to_string() + " courses",
            color=theme.text,
            size="3",
        ),

        
        # Fixed Grid layout setup to ensure single search results maintain standard sizing instead of stretching
        rx.box(
            rx.foreach(
                PlannerState.explore_page_catalog,
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
                    background_color=theme.lighter_aa_blue,
                    border=f"1px solid {theme.border}",
                    border_radius="12px",
                    padding="24px",
                    height="230px",
                    flex="1 1 560px",
                    max_width="800px",
                    overflow="hidden",
                )
            
            ),
            # Standardized layout settings for the responsive grid

            style={
                "display": "flex",
                "flex_wrap": "wrap",
                "justify_content": "center",
                "gap": "24px",
            },
            width="100%",
        ),
        pagination_bar(),
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


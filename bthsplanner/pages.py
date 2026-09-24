"""
Page-level layouts for BTHS Planner: Plan (/), Explore (/explore),
and How It Works (/how-it-works). Assembles components.py pieces
using state from state.py. app.add_page(...) calls stay in
bthsplanner.py, not here.
"""
import reflex as rx
from data.courses import MAJORS

import bthsplanner.theme as theme
from bthsplanner.state import PlannerState, DropdownOptions, MAJOR_COURSE_COLOR
from bthsplanner.components import (
    navigation_layout,
    course_card,
    elective_card,
    dropdown_card,

    course_detail_modal,
    course_search_modal,
    legend_bar,
    pre_credit_checkbox,
    pre_language_checkbox,
    styled_select,
    render_major_course,
    filter_dropdowns
)


@rx.page(route="/", title="BTHS Planner - Plan", on_load=PlannerState.change_tab("Plan")) 
def index() -> rx.Component:
    plan_content = rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Course Plan", font_size="35px", color="#fafafa", margin_bottom="12px"),
                legend_bar(),
            ),
            rx.spacer(),
            rx.vstack(
                rx.text("Select your major", class_name="card-label", color = "white", font_size = "15px", font_weight = "bold"),
                styled_select(MAJORS, PlannerState.major, PlannerState.change_major, "15px"),
                rx.box(rx.text("View majors ", rx.link("here", href="https://www.bths.edu/apps/pages/index.jsp?uREC_ID=222176&type=d&termREC_ID=&pREC_ID=1201473f", is_external=True, color="white", text_decoration="underline"),font_weight="600", color="white", as_="span", size="2")),
                background_color=theme.lighter_aa_blue, padding="10px", border_radius="0.5rem", border="1px solid #31353f", width="255px", spacing="1",
                ),
        ),
        rx.hstack(
            rx.text("Select which credits you already have:", font_weight="bold", color="white", font_size="20px"),
            pre_credit_checkbox("Algebra I"),
            pre_credit_checkbox("Geometry"),
            pre_credit_checkbox("US History"),
            pre_credit_checkbox("Biology/Living Environment"),
            pre_language_checkbox(),

            align_items="center",
            spacing="5",
            padding="12px 0px",
            background_color="#0F172A",
            border_radius="8px",
            margin_top="10px",
        ),
        rx.grid(
            
            rx.hstack(
                
                rx.vstack(
                    rx.cond(PlannerState.major_note != "", rx.callout(rx.text(PlannerState.major_note, font_size = "16px"), icon="info", color_scheme="blue",)),
                    #rx.cond(PlannerState.chose_economics_jr, rx.callout(rx.text("*Taking Economics in junior year requires students to have already passed the United States History Regents exam.", font_size = "16px"), icon="info", color_scheme="purple", margin_bottom="12px", font_size = "16px")),
                    #rx.cond(PlannerState.chose_african_jr, rx.callout(rx.text("*Taking AP African American Studies in junior year requires students to have already passed the United States History Regents exam.", font_size = "16px"), icon="info", color_scheme="purple", margin_bottom="12px")),
                ),
                align="start",
                spacing="3",
            ),

            rx.grid(
                # --- FRESHMAN ---
                rx.vstack(
                    rx.heading("Freshman", size="7", margin_bottom="2px", color="#fafafa"),
                    rx.hstack(
                        rx.text(PlannerState.freshman_course_count.to(str) + " courses", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.freshman_periods.to(str) + "/10 periods", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.freshman_ap_count.to(str) + "/3 APs", size="3", color=rx.cond(PlannerState.freshman_ap_count >= 3, "#f87171", "white"), weight = "medium"),
                        spacing="2", margin_bottom="10px"
                    ),
                    
                    rx.tooltip(
                        course_card("English Course", "English 9"),
                        content = "Double period, alternates daily with DDP"
                    ),
                    rx.cond(PlannerState.major_has_aphg,
                        course_card("History Course", "Pre-AP World History"),
                        dropdown_card("History Course", DropdownOptions.f_hist_opts, PlannerState.f_hist, PlannerState.change_f_hist),),
                    rx.cond(
                        PlannerState.pre_credits["Biology/Living Environment"],
                        dropdown_card("Science Course", DropdownOptions.f_sci_opts, PlannerState.f_sci, PlannerState.change_f_sci),
                        course_card("Science Course", PlannerState.f_sci),),
                    
                    rx.foreach(
                        PlannerState.freshman_math_courses,
                        lambda course: course_card("Math Course", course)
                    ),
                    course_card("Language Course", PlannerState.f_lang),
                    rx.tooltip(
                        course_card("Required Course", "Design & Drafting for Production (DDP)"),
                        content = "Double period, alternates daily with English 9"
                    ),
                    rx.vstack(
                        rx.foreach(
                            PlannerState.freshman_electives,
                            lambda course: elective_card(course, "Freshman")
                            ),
                        course_card("Required Period", "Gym"),
                        course_card("Required Period", "Lunch"),                            
                        course_search_modal(PlannerState.freshman_periods, "Freshman"),
                        width="100%", 
                        spacing="3",
                        margin_top="0px"
                    ),
                    align_items="stretch"
                ),

                # --- SOPHOMORE ---
                rx.vstack(
                    rx.heading("Sophomore", size="7", margin_bottom="2px", color="#fafafa"),
                    rx.hstack(
                        rx.text(PlannerState.sophomore_course_count.to(str) + " courses", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.sophomore_periods.to(str) + "/10 periods", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.sophomore_ap_count.to(str) + "/3 APs", size="3", color=rx.cond(PlannerState.sophomore_ap_count >= 3, "#f87171", "white"), weight = "medium"),
                        spacing="2", margin_bottom="10px"
                    ),
                    
                    dropdown_card("English Course", DropdownOptions.so_eng_opts, PlannerState.so_eng, PlannerState.change_so_eng),
                    dropdown_card("History Course", DropdownOptions.so_hist_opts, PlannerState.so_hist, PlannerState.change_so_hist),
                    course_card("Science Course", "Regents Chemistry"),
                    rx.cond(PlannerState.math_is_accelerated, course_card("Math Course", "Pre-Calculus"), course_card("Math Course", "Algebra II")),
                    rx.cond(PlannerState.lang_is_accelerated, course_card("Language Course", PlannerState.language_base + " III"), course_card("Language Course", PlannerState.language_base + " II")),
                    course_card("Required Course", "AP Computer Science Principles"),
                    course_card("Required Course", "Health Education"),
                    rx.vstack(
                        rx.foreach(
                            PlannerState.sophomore_electives,
                            lambda course: elective_card(course, "Sophomore")
                        ),
                        course_card("Required Period", "Gym"),
                        course_card("Required Period", "Lunch"),                        
                        course_search_modal(PlannerState.sophomore_periods, "Sophomore"),
                        width="100%", 
                        spacing="3",
                        margin_top="0px"
                    ),
                    align_items="stretch"
                ),

               # --- JUNIOR ---
                rx.vstack(
                    rx.heading("Junior", size="7", margin_bottom="2px", color="#fafafa"),
                    rx.hstack(
                        rx.text(PlannerState.junior_course_count.to(str) + " courses", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.junior_periods.to(str) + "/10 periods", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.junior_ap_count.to(str) + "/3 APs", size="3", color=rx.cond(PlannerState.junior_ap_count >= 3, "#f87171", "white"), weight = "medium"),
                        spacing="2", margin_bottom="10px"
                    ),
                    
                    
                    rx.cond(
                        PlannerState.major != "LIU Pharmacy",
                        dropdown_card("English Course", DropdownOptions.j_eng_opts, PlannerState.j_eng, PlannerState.change_j_eng),
                        rx.fragment()
                    ),
                    rx.cond(
                        PlannerState.j_his == "None (free period, econ senior year)",
                        rx.fragment(),
                        dropdown_card("History Course", DropdownOptions.j_his_opts, PlannerState.j_his, PlannerState.change_j_his),
                    ),
                    rx.cond(
                        PlannerState.chose_economics_jr & ~PlannerState.has_econ_gov_conflict & ~PlannerState.chose_government_jr & ~PlannerState.has_gov_conflict,
                        course_card("Government Course", "Participation in Government")
                    ),
                    rx.cond(
                        PlannerState.need_regents_physics_junior,
                        rx.cond(
                            PlannerState.junior_ap_room_for_physics,
                            dropdown_card("Science Course", DropdownOptions.j_phys_opts, PlannerState.j_phys, PlannerState.change_j_phys),
                            course_card("Science Course", "Regents Physics")
                        )
                    ),
                    
                    # 2. refular math card. safe fallback logic. Only shows up down here if it wasn't pulled into the major stack above!
                    rx.cond(
                        PlannerState.junior_math_override == "",
                        #rx.cond(
                            #PlannerState.math_is_accelerated,
                            #course_card("Math Course", "AP Calculus BC"),
                        dropdown_card("Math Course", DropdownOptions.j_math_opts, PlannerState.j_math, PlannerState.change_j_math)
                        
                    ),
                    
                    rx.cond(~PlannerState.lang_is_accelerated, course_card("Language Course", PlannerState.language_base + " III")),
                    
# 1. 🎯 MAJOR SEQUENCE SLOTS: Only pulls math up if a major math requirement exists
                    rx.cond(
                        PlannerState.junior_math_override != "",
                        dropdown_card("Major Course", DropdownOptions.j_math_opts, PlannerState.j_math, PlannerState.change_j_math)
                    ),
                                                
                
                    rx.foreach(PlannerState.filtered_junior_major_courses, render_major_course),
                        
                
                    
                   
                    rx.vstack(
                        rx.foreach(
                            PlannerState.junior_electives,
                            lambda course: elective_card(course, "Junior")
                            ),
                        course_card("Required Period", "Gym"),
                        course_card("Required Period", "Lunch"),
                        course_search_modal(PlannerState.junior_periods, "Junior"),
                        width="100%", 
                        spacing="3",
                        margin_top="0px"
                    ),
                    align_items="stretch"
                ),

                
                # --- SENIOR ---
                # --- SENIOR COLUMN ---
                rx.vstack(
                    rx.heading("Senior", size="7", margin_bottom="2px", color="#fafafa"),
                    rx.hstack(
                        rx.text(PlannerState.senior_course_count.to(str) + " courses", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.senior_periods.to(str) + "/10 periods", size="3", color="white", weight = "medium"),
                        rx.text("•", size="3", color="white"),
                        rx.text(PlannerState.senior_ap_count.to(str) + "/3 APs", size="3", color=rx.cond(PlannerState.senior_ap_count >= 3, "#f87171", "white"), weight = "medium"),
                        spacing="2", margin_bottom="10px"
                    ),
                    
                    dropdown_card("English Course", DropdownOptions.sn_eng_opts, PlannerState.sn_eng, PlannerState.change_sn_eng),
                    rx.cond(
                        ~PlannerState.chose_economics_jr & ~PlannerState.has_macro,
                        rx.fragment(
                            dropdown_card("History Course", DropdownOptions.sn_his_opts, PlannerState.sn_his, PlannerState.change_sn_his),
                            rx.cond(
                                ((PlannerState.sn_his == "AP US Government") | (PlannerState.sn_his == "Participation in Government")) & ~PlannerState.chose_economics_jr & ~PlannerState.has_econ_gov_conflict, 
                                course_card("Economics Course", PlannerState.sn_ec)),
                            rx.cond(
                                (PlannerState.sn_his == "Economics") & ~PlannerState.chose_government_jr & ~PlannerState.has_gov_conflict, 
                                dropdown_card("Government Course", DropdownOptions.sn_gov_opts, PlannerState.sn_gov, PlannerState.change_sn_gov)),
                        ),
                    ),
                #NON-MAJOR MATH SLOT (Only displays for majors that DO NOT have math in their major requirements)
                    rx.cond(
                        PlannerState.senior_math_override == "",
                        rx.cond(
                            PlannerState.took_ap_calc_bc_junior,
                            rx.tooltip(
                                rx.box(
                                    dropdown_card("Math Course", DropdownOptions.sn_math_opts, PlannerState.sn_math, PlannerState.change_sn_math),
                                    rx.button(
                                        rx.cond(PlannerState.sn_math_active, "✕", "＋"),
                                        on_click=PlannerState.toggle_sn_math,
                                        variant="ghost", size="1",
                                        color_scheme=rx.cond(PlannerState.sn_math_active, "red", "green"),
                                        style={
                                            "position": "absolute", "top": "40px", "transform": "translateY(-50%)",
                                            "right": "20px", "font_size": "20px", "cursor": "pointer",
                                            "padding": "4px", "height": "auto", "z_index": "10"
                                        }
                                    ),
                                    style={"position": "relative", "margin_bottom": "0px", "width": "100%", "opacity": rx.cond(PlannerState.sn_math_active, "1.0", "0.4")}
                                ),
                                content = "Taking Math all four years is highly encouraged",
                                #style={"font_size": "20px !important"}
                            ),
                            dropdown_card("Math Course", DropdownOptions.sn_calcs, PlannerState.sn_math, PlannerState.change_sn_math),
                        )
                    ),
                    # MAJOR COURSES SECTION
                    rx.cond(
                        PlannerState.major == "Physics",
                        # Physics Major View (Kept intact)
                        rx.vstack(
                            rx.tooltip(
                                rx.box(
                                    rx.box(
                                        rx.text("Major Course", class_name="card-label"),
                                        rx.text("AP Physics II", class_name="card-title"),
                                        class_name="course-card",
                                        on_click=PlannerState.open_course_details("AP Physics II"),
                                        style={"cursor": "pointer", "background_color": theme.lighter_aa_blue, "border": f"1px solid color-mix(in srgb, {MAJOR_COURSE_COLOR} 85%, white 15%)"}
                                    ),
                                    rx.button(
                                        rx.cond(PlannerState.selected_senior_physics.contains("AP Physics II"), "✕", "＋"),
                                        on_click=lambda: PlannerState.toggle_senior_physics("AP Physics II"),
                                        variant="ghost", size="1",
                                        color_scheme=rx.cond(PlannerState.selected_senior_physics.contains("AP Physics II"), "red", "green"),
                                        is_disabled=(PlannerState.selected_senior_physics.length() == 1) & PlannerState.selected_senior_physics.contains("AP Physics II"),
                                        style={
                                            "position": "absolute", "top": "40px", "transform": "translateY(-50%)",
                                            "right": "20px", "font_size": "20px", "cursor": "pointer",
                                            "padding": "4px", "height": "auto", "z_index": "10"
                                        }
                                    ),
                                    style={"position": "relative", "margin_bottom": "15px", "width": "100%", "opacity": rx.cond(PlannerState.selected_senior_physics.contains("AP Physics II"), "1.0", "0.4")}
                                ),
                                content="You must keep at least one AP Physics",
                            ),
                            rx.tooltip(
                                rx.box(
                                    rx.box(
                                        rx.text("Major Course", class_name="card-label"), 
                                        rx.text("AP Physics C: Electricity & Magnetism", class_name="card-title"),
                                        class_name="course-card", 
                                        on_click=PlannerState.open_course_details("AP Physics C: Electricity & Magnetism"), 
                                        style={"cursor": "pointer", "background_color": theme.lighter_aa_blue, "border": f"1px solid color-mix(in srgb, {MAJOR_COURSE_COLOR} 85%, white 15%)"}
                                    ),
                                    rx.button(
                                        rx.cond(PlannerState.selected_senior_physics.contains("AP Physics C: Electricity & Magnetism"), "✕", "＋"), 
                                        on_click=lambda: PlannerState.toggle_senior_physics("AP Physics C: Electricity & Magnetism"),
                                        variant="ghost", size="1", 
                                        color_scheme=rx.cond(PlannerState.selected_senior_physics.contains("AP Physics C: Electricity & Magnetism"), "red", "green"),
                                        is_disabled=(PlannerState.selected_senior_physics.length() == 1) & PlannerState.selected_senior_physics.contains("AP Physics C: Electricity & Magnetism"),
                                        style={
                                            "position": "absolute", "top": "40px", "transform": "translateY(-50%)", 
                                            "right": "20px", "font_size": "20px", "cursor": "pointer", 
                                            "padding": "4px", "height": "auto", "z_index": "10",
                                        }
                                    ),
                                    style={"position": "relative", "margin_bottom": "15px", "width": "100%", "opacity": rx.cond(PlannerState.selected_senior_physics.contains("AP Physics C: Electricity & Magnetism"), "1.0", "0.4")}
                                ),
                                content="You must keep at least one AP Physics"
                            ),
                            course_card("Major Course", "Modern Physics"),
                            width="100%", spacing="3", margin_top="0px"
                        ),

                        # Math major/ liu pharm math is a major course 
                        rx.vstack(
                            # Renders all major courses except math
                            rx.cond(
                                PlannerState.senior_math_override != "",
                                rx.cond(
                                    PlannerState.took_ap_calc_bc_junior,
                                    rx.cond(
                                        PlannerState.sn_math != "",
                                        dropdown_card("Major Course", DropdownOptions.sn_math_opts, PlannerState.sn_math, PlannerState.change_sn_math),
                                        rx.fragment()
                                        ),
                                    dropdown_card("Major Course", DropdownOptions.sn_calcs, PlannerState.sn_math, PlannerState.change_sn_math),
                                )
                            ),                            
                            
                            
                            rx.foreach(PlannerState.filtered_senior_major_courses, render_major_course),
                            
                            # If this major has a math requirement/override (e.g. Applied Math), place standard non-deletable dropdown inside Major Section
                            
                            width="100%", spacing="3", margin_top="0px"
                        )
                    ),

                    

                    # ELECTIVES SECTION
                    rx.vstack(
                        rx.foreach(
                            PlannerState.senior_electives,
                            lambda course: elective_card(course, "Senior")
                            ),
                        course_card("Required Period", "Gym"),
                        course_card("Required Period", "Lunch"),
                        course_search_modal(PlannerState.senior_periods, "Senior"),
                        width="100%", 
                        spacing="3",
                        margin_top="0px"
                    ),
                    align_items="stretch",
                    spacing="3"
                ),
                columns={"initial": "1", "sm": "2", "md": "4"}, spacing="4", width="100%"
            ),
            grid_template_columns={"initial": "1fr", "md": "1fr 3fr"}, spacing="5", width="100%",
        ),

        course_detail_modal(),
        rx.divider(margin_y="32px", border_color="#31353f"),
        
        


        
        width="100%",
        align_items="stretch"
    )
    return navigation_layout(plan_content)




@rx.page(route="/explore", title="BTHS Planner - Explore Courses", on_load=PlannerState.change_tab("Explore")) 
def explore_page() -> rx.Component:
    explore_content = rx.vstack(
        rx.vstack(
            rx.heading("Explore Course Catalog", font_size="40px", color="#fafafa"),
            rx.text("Search and browse through all academic offerings at Brooklyn Tech.", color="white", size="3"),
            
            # Live Filter Search Field
            rx.hstack(
                rx.input(
                    placeholder="Search titles, descriptions or keywords...",
                    on_change=PlannerState.set_explore_search_query,
                    value=PlannerState.explore_search_query,
                    width="100%",
                    max_width="800",
                    margin_top="12px",
                    margin_bottom="10px",
                    size="3",
                    background_color = theme.lighter_aa_blue
                ),
                filter_dropdowns(),
                width="100%",
                align="center",
            ),
            rx.text("Showing " + PlannerState.explore_catalog_count.to_string() + " courses", color="rgba(250,250,250,0.5)", size="3"),
            width="100%",
            align="start",
        ),
        
        # Fixed Grid layout setup to ensure single search results maintain standard sizing instead of stretching
        rx.grid(
            rx.foreach(
                PlannerState.explore_catalog,
                lambda course: rx.box(
                    rx.vstack(
                        # Header Row: Course Title on top, Badges side-by-side underneath
                        rx.vstack(
                            # 1. Course Name (Top line)
                            rx.text(course["name"], size="5", weight="bold", color="#fafafa"),
                            
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
                                color="rgba(250, 250, 250, 0.7)", 
                                margin_top="8px"
                            ),
                            # Gradient overlay fading  into the card color 
                            rx.box(
                                position="absolute",
                                bottom="0",
                                left="0",
                                right="0",
                                height="30px",
                                background="linear-gradient(to bottom, rgba(30, 32, 37, 0) 0%, #1f2937 100%)",
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
                    border="1px solid #31353f",     # Seamless matching border lines
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
    return navigation_layout(explore_content)

# ---------------------------------------------------------------------
# HOW IT WORKS CONTENT
# Just edit this list to add/remove/change sections. Each dict becomes
# one subheading + paragraph on the page, in order.
# "rule" (optional, True/False) makes it render like a sub-rule, indented
# under the "Rules" heading with a smaller/orange heading color.
# ---------------------------------------------------------------------
HOW_IT_WORKS_SECTIONS = [
    {
        "heading": "What is BTHS Planner?",
        "body": "BTHS Planner is built for Brooklyn Technical High School students to accurately simulate their 4-year schedule. This tool uses required classes, major specific classes, and electives to calculate course count, period count, and AP count. BTHS Planner is designed to enforce the credits and classes necessary for Brooklyn Tech students to recieve a Brooklyn Tech Diploma (more down below).",
    },
    {
        "heading": "Selecting Major",
        "body": "Brooklyn Tech requires students to commit to a specific major starting junior year. You can think of your major at Brooklyn Tech as the classes that you will be required to take during your junior and senior years. Use the drop-down menu at the top of the 'Plan' tab to pick a major. Changing your major will reset your junior and senior year schedules and swap them with the mandatory courses for that major. Swapping majors will also reset all other edited/added courses in order to meet the necessary constraints such as the 3 AP limit, 10 maximum periods, and more.",
    },
    {
        "heading": "Credits",
        "body": "At Brooklyn Tech, students are expected to take rigorous courses throughout their four years. Students are scheduled to complete an advanced regents diploma, as well as take additional courses in order to earn their Brooklyn Tech Diploma. This means earning a total of 44 credits and passing necessary Regents exams, which can be done throughout middle school and high school. These credits are described below.\n\n1 credit = 1 semester\n2 semesters = 1 year",
        "rule": True,
    },
    {
        "heading": "English (8 credits)",
        "body" : "• 8 semesters of English Language Arts (ELA)",
        "desc" : True
    },
    {
        "heading": "History (8 credits)",
        "body" : "• 4 semesters of Global History\n• 2 semesters of US History\n• 1 semester of Participation in Government\n• 1 semester of Economics",
        "desc" : True
    },
    {
        "heading": "Mathematics (6 credits)",
        "body": "• 2 semesters of Algebra 1\n• 2 semesters of Geometry\n• 2 semesters of Algebra II",

        "desc" : True
    },
    {
        "heading": "Science (6 credits)",
        "body": "• 2 semesters of Biology\n• 2 semesters of Physics\n• 2 semesters of Chemistry",

        "desc" : True
    },
    {
        "heading": "World Languages (6 credits)",
        "body": "• 6 semesters of Chinese, French, German, Italian, or Spanish.",
        "desc" : True
    },
    {
        "heading": "Arts & Engineering (2 credits)",
        "body": "• 2 semesters of Design & Drafting for Production (DDP)",
        "desc" : True
    },
    {
        "heading": "Computer Science (2 credits)",
        "body": "• 2 semesters of AP Computer Science Principles",
        "desc" : True
    },
    {
        "heading": "Physical Education (4 credits; 1 semester = 0.5 credits)",
        "body": "• 8 semesters of PE (Gym)",
        "desc" : True
    },
    {
        "heading": "Health Education (1 credit)",
        "body": "• 1 semester of Health Education",
        "desc" : True
    },
    {
        "heading": "Major Courses and Electives (3 credits)",
        "body": "• Varies by major\n• Major courses cover elective requirement",
        "desc" : True
    },
    {
        "heading": "Period Limit",
        "body": "A standard day cannot exceed 10 periods. Excluding a mandatory lunch period and gym rotation period (gym, lab, free period, advisory for a semester), each student has 8 available periods that can be spent in class. Classes can be 1 or 2 periods. To see class information, you can either click on the class card in your plan, or go through the Explore page.",
        "rule": True,
    },
    {
        "heading": "AP Limit",
        "body": "Advanced Placement courses are highly demanding, so Brooklyn Tech imposes a limit of 3 AP classes per year.",
        "rule": True,
    },
    {
        "heading": "Electives",
        "body": "Elective courses allow you to customize your schedule, but they can only be added if you have open periods left in your 10 period limit after your mandatory major and required courses.",
        "rule": True,
    },
]


def how_it_works_section(section: dict) -> rx.Component:
    is_desc = section.get("desc", False)
    return rx.vstack(
        rx.heading(
            section["heading"],
            font_size="22px" if is_desc else "28px",
            color="#ffffff", #if is_rule else "#3b82f6",
            margin_bottom="8px",
        ),
        rx.text(section["body"], color="#ffffffff") if section["body"] else rx.fragment(),
        align_items="start",
        font_size = "20px",
        spacing="1",
        width="100%",
        white_space="pre-line",
        padding_left="20px" if is_desc else "0px",
        margin_bottom="20px",
    )


@rx.page(route="/how-it-works", title="BTHS Planner - How It Works", on_load=PlannerState.change_tab("How It Works"))
def how_it_works_page() -> rx.Component:
    how_it_works_content = rx.vstack(
        # Page Header
        rx.heading("How It Works", font_size="40px", margin_bottom="8px", color="#ffffff"),
        rx.text(
            "Welcome to BTHS Planner! Here is a quick guide on how to navigate the planner and successfully map out your Brooklyn Tech high school career.",
            color="#ffffffff",
            margin_bottom="24px",
            font_size = "20px"
        ),

        *[how_it_works_section(section) for section in HOW_IT_WORKS_SECTIONS],

        align_items="start",
        width="100%",
        max_width="900px",
        padding_bottom="40px"
    )
    return navigation_layout(how_it_works_content)


hide_watermark_style = {
    "div.__reflex": {
        "display": "none !important",
    },
    "div[style*='position: fixed'][style*='bottom:']:has(a[href*='reflex.dev'])": {
        "display": "none !important",
    },
    "a[href*='reflex.dev']": {
        "display": "none !important",
    }
}


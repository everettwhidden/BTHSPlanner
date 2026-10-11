import reflex as rx
from data.courses import *

import bthsplanner.theme as theme
from bthsplanner.backend import *



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
        "heading": "Majors and Electives (7 credits)",
        "body": "• Varies by major\n• Majors cover elective requirement",
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
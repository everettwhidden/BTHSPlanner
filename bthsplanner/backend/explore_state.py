import math

import reflex as rx

from .constants import EXPLORE_PAGE_SIZE
from .explore_helpers import filter_explore_catalog


def _toggle(items: list[str], item: str):
    if item in items:
        items.remove(item)
    else:
        items.append(item)


class ExploreState(rx.State):
    explore_search_query: str = ""
    order: str = "A-Z"
    selected_grades: list[str] = []
    selected_majors: list[str] = []
    selected_filters: list[str] = []
    selected_period_length: list[str] = []
    selected_semesters: list[str] = []
    explore_page_num: int = 1

    def clear_filters(self):
        self.order = "A-Z"
        self.selected_grades = []
        self.selected_majors = []
        self.selected_filters = []
        self.selected_period_length = []
        self.selected_semesters = []
        self.explore_page_num = 1

    def set_explore_search_query(self, val: str):
        self.explore_search_query = val
        self.explore_page_num = 1

    def set_order(self, val: str):
        self.order = val
        self.explore_page_num = 1

    def toggle_grade(self, grade: str):
        _toggle(self.selected_grades, grade)
        self.explore_page_num = 1

    def toggle_filter(self, filter_name: str):
        _toggle(self.selected_filters, filter_name)
        self.explore_page_num = 1

    def toggle_major(self, major: str):
        _toggle(self.selected_majors, major)
        self.explore_page_num = 1

    def toggle_period_length(self, period_length: str):
        _toggle(self.selected_period_length, period_length)
        self.explore_page_num = 1

    def toggle_semester(self, semester: str):
        _toggle(self.selected_semesters, semester)
        self.explore_page_num = 1

    def next_explore_page(self):
        if self.explore_page_num < self.explore_total_pages:
            self.explore_page_num += 1
            return rx.call_script("window.scrollTo(0, 0)")

    def prev_explore_page(self):
        if self.explore_page_num > 1:
            self.explore_page_num -= 1
            return rx.call_script("window.scrollTo(0, 0)")

    @rx.var
    def explore_catalog(self) -> list[dict]:
        return filter_explore_catalog(
            query=self.explore_search_query,
            order=self.order,
            grades=self.selected_grades,
            majors=self.selected_majors,
            filters=self.selected_filters,
            period_lengths=self.selected_period_length,
            semesters=self.selected_semesters,
        )

    @rx.var
    def explore_catalog_count(self) -> int:
        return len(self.explore_catalog)

    @rx.var
    def explore_total_pages(self) -> int:
        return max(1, math.ceil(len(self.explore_catalog) / EXPLORE_PAGE_SIZE))

    @rx.var
    def explore_page_catalog(self) -> list[dict]:
        start = (self.explore_page_num - 1) * EXPLORE_PAGE_SIZE
        return self.explore_catalog[start:start + EXPLORE_PAGE_SIZE]

    
    @rx.var
    def explore_page_count(self) -> int:
        return len(self.explore_page_catalog)
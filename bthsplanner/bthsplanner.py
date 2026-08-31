import reflex as rx

from bthsplanner.pages import index, explore_page, how_it_works_page

config = rx.Config(
    app_name="bthsplanner",
)


class User(rx.Model, table=True):
    __tablename__ = "user"

    saved_progress: str  # Stores JSON string of course/major selections


hide_watermark_style = {
    "div.__reflex": {
        "display": "none !important",
    },
    "div[style*='position: fixed'][style*='bottom:']:has(a[href*='reflex.dev'])": {
        "display": "none !important",
    },
    "a[href*='reflex.dev']": {
        "display": "none !important",
    },
}

app = rx.App(
    stylesheets=["/style.css"],
    style=hide_watermark_style,
    head_components=[
        rx.el.meta(property="og:image", content="https://www.bths.edu/pics/header_logo.png"),
        rx.el.meta(name="twitter:card", content="summary_large_image"),
        rx.el.meta(name="twitter:image", content="https://www.bths.edu/pics/header_logo.png"),
        rx.el.link(rel="icon", type="image/png", href="/favicon.ico"),
    ],
)
app.add_page(index)
rx.Model.create_all()
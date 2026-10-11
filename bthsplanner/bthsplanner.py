import reflex as rx

from bthsplanner.pages import *

config = rx.Config(
    app_name="bthsplanner",
    default_color_mode = "dark",
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
        rx.el.script(
            src="https://umami-production-07b7.up.railway.app/script.js",
            defer=True,
            custom_attrs={"data-website-id": "779aee42-e79c-4289-b881-65d70df59e21"},
        ),
    ],
)
app.add_page(index)
rx.Model.create_all()
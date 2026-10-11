import reflex as rx

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

"""Convert tabbar SVG icons to PNG (WeChat mini-program requires PNG/JPG, not SVG).

Icons are simple line-art drawn in a 24x24 viewBox. We redraw them with Pillow
at 81x81 px (WeChat tabBar recommended size), scaling coordinates by 81/24.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "assets", "tabbar")
SIZE = 81
SCALE = SIZE / 24.0  # 3.375

# Each icon: name -> list of primitives drawn in 24x24 space.
# Types: ('line', x1,y1,x2,y2,width), ('poly', [(x,y)...], width, close),
#        ('cubic', p0, c1, c2, p1, width)  -- cubic bezier, sampled smoothly,
#        ('circle', cx,cy,r,width), ('rect', x,y,w,h,width)
ICONS = {
    "home": {
        "gray": [
            ("poly", [(3, 12), (12, 3), (21, 12)], 1.5, False),
            ("poly", [(5, 10), (5, 20), (19, 20), (19, 10)], 1.5, False),
            ("poly", [(10, 20), (10, 14), (14, 14), (14, 20)], 1.5, False),
        ],
        "blue": [
            ("poly", [(3, 12), (12, 3), (21, 12)], 2.0, False),
            ("poly", [(5, 10), (5, 20), (19, 20), (19, 10)], 2.0, False),
            ("poly", [(10, 20), (10, 14), (14, 14), (14, 20)], 2.0, False),
        ],
    },
    "learn": {
        "gray": [
            ("poly", [(4, 6), (12, 3), (20, 6), (20, 14), (12, 17), (4, 14)], 1.5, True),
            ("poly", [(4, 14), (4, 18), (12, 21), (20, 18), (20, 14)], 1.5, False),
            ("poly", [(8, 8), (8, 12), (12, 14), (16, 12), (16, 8)], 1.5, True),
        ],
        "blue": [
            ("poly", [(4, 6), (12, 3), (20, 6), (20, 14), (12, 17), (4, 14)], 2.0, True),
            ("poly", [(4, 14), (4, 18), (12, 21), (20, 18), (20, 14)], 2.0, False),
            ("poly", [(8, 8), (8, 12), (12, 14), (16, 12), (16, 8)], 2.0, True),
        ],
    },
    "project": {
        "gray": [
            ("rect", 3, 3, 7, 7, 1.5),
            ("rect", 14, 3, 7, 7, 1.5),
            ("rect", 3, 14, 7, 7, 1.5),
            ("rect", 14, 14, 7, 7, 1.5),
        ],
        "blue": [
            ("rect", 3, 3, 7, 7, 2.0),
            ("rect", 14, 3, 7, 7, 2.0),
            ("rect", 3, 14, 7, 7, 2.0),
            ("rect", 14, 14, 7, 7, 2.0),
        ],
    },
    "mine": {
        "gray": [
            ("circle", 12, 8, 4, 1.5),
            ("cubic", (4, 21), (4, 16.58), (7.58, 13), (12, 13), 1.5),
            ("cubic", (12, 13), (16.42, 13), (20, 16.58), (20, 21), 1.5),
        ],
        "blue": [
            ("circle", 12, 8, 4, 2.0),
            ("cubic", (4, 21), (4, 16.58), (7.58, 13), (12, 13), 2.0),
            ("cubic", (12, 13), (16.42, 13), (20, 16.58), (20, 21), 2.0),
        ],
    },
}

GRAY = "#999999"
BLUE = "#165dff"


def bezier_points(p0, c1, c2, p1, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * c1[0] + 3 * mt * t**2 * c2[0] + t**3 * p1[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * c1[1] + 3 * mt * t**2 * c2[1] + t**3 * p1[1]
        pts.append((x, y))
    return pts


def draw_primitives(draw, prims, color):
    for p in prims:
        kind = p[0]
        w = round(p[-1] * SCALE, 1)
        width = max(1, int(round(w)))
        if kind == "poly":
            pts = [(x * SCALE, y * SCALE) for (x, y) in p[1]]
            close = p[2]
            if close:
                draw.line(pts + [pts[0]], fill=color, width=width, joint="curve")
            else:
                draw.line(pts, fill=color, width=width, joint="curve")
        elif kind == "cubic":
            p0, c1, c2, p1 = p[1], p[2], p[3], p[4]
            pts = [(x * SCALE, y * SCALE) for (x, y) in bezier_points(p0, c1, c2, p1)]
            draw.line(pts, fill=color, width=width, joint="curve")
        elif kind == "circle":
            cx, cy, r = p[1], p[2], p[3]
            draw.ellipse(
                [(cx - r) * SCALE, (cy - r) * SCALE, (cx + r) * SCALE, (cy + r) * SCALE],
                outline=color,
                width=width,
            )
        elif kind == "rect":
            x, y, w2, h = p[1], p[2], p[3], p[4]
            draw.rectangle(
                [x * SCALE, y * SCALE, (x + w2) * SCALE, (y + h) * SCALE],
                outline=color,
                width=width,
            )


def main():
    for name, variants in ICONS.items():
        for variant, prims in variants.items():
            color = BLUE if variant == "blue" else GRAY
            img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw_primitives(draw, prims, color)
            out = os.path.join(SRC, f"{name}-{variant}.png")
            img.save(out, "PNG")
            print(f"  wrote {os.path.basename(out)}  ({img.size})")
    print("Done. 8 PNG icons generated.")


if __name__ == "__main__":
    main()

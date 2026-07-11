def hex_to_rgba(hex_color, alpha):
    hex_color = hex_color.strip().lstrip("#")

    if len(hex_color) != 6:
        return f"rgba(255, 255, 255, {alpha})"

    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    return f"rgba({red}, {green}, {blue}, {alpha:.2f})"


def scope_selector(selector):
    return f".ks-preview {selector}"


def selector_block(selectors):
    return ",\n".join(scope_selector(selector) for selector in selectors)


def border_css(border):
    width = int(border["width"])
    position = border["position"]

    if width <= 0 or position == "none":
        return "    border: 0;\n"

    color = hex_to_rgba(border["color"], float(border["alpha"]))

    if position == "bottom":
        return f"    border: 0;\n    border-bottom: {width}px solid {color};\n"

    if position == "left":
        return f"    border: 0;\n    border-left: {width}px solid {color};\n"

    if position == "full":
        return f"    border: {width}px solid {color};\n"

    return "    border: 0;\n"


def role_css(role):
    selectors = selector_block(role["selectors"])
    background = hex_to_rgba(
        role["background"]["color"],
        float(role["background"]["alpha"]),
    )

    css = f"""
{selectors} {{
    background-image: none;
    background-color: {background};
    border-radius: {int(role["border"]["radius"])}px;
    padding: {int(role["padding"])}px;
    margin: {int(role["margin"])}px;
{border_css(role["border"])} }}
"""

    if role["text_selectors"]:
        text_selectors = selector_block(role["text_selectors"])
        text_color = hex_to_rgba(
            role["text"]["color"],
            float(role["text"]["alpha"]),
        )

        css += f"""
{text_selectors} {{
    color: {text_color};
}}
"""

    return css


def generate_preview_css(theme_model):
    css = """
.ks-preview * {
    color: #fdf6e3;
    font-size: 18px;
    text-shadow: none;
    box-shadow: none;
    border: 0;
}

.ks-preview {
    background-color: #13181C;
}

.ks-preview button {
    background-image: none;
    transition: padding 0s;
}

.ks-preview button label {
    color: #fdf6e3;
}

.ks-preview .title_bar {
    min-height: 48px;
}

.ks-preview .action_bar {
    min-width: 110px;
}

.ks-preview .heatergraph {
    min-height: 220px;
}
"""

    for role in theme_model.roles.values():
        css += role_css(role)

    return css
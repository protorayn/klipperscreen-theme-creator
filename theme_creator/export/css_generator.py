def hex_to_rgba(hex_color, alpha):
    hex_color = hex_color.strip().lstrip("#")

    if len(hex_color) != 6:
        return f"rgba(255, 255, 255, {alpha})"

    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    return f"rgba({red}, {green}, {blue}, {alpha:.2f})"


def safe_css_name(name):
    return (
        name.replace(".", "_")
        .replace("-", "_")
        .replace(" ", "_")
        .lower()
    )


def color_var_name(role_name, color_type):
    return f"{safe_css_name(role_name)}_{color_type}"


def color_ref(role_name, color_type):
    return f"@{color_var_name(role_name, color_type)}"


def scope_selector(selector, preview=False):
    if preview:
        return f".ks-preview {selector}"

    return selector


def selector_block(selectors, preview=False):
    return ",\n".join(scope_selector(selector, preview) for selector in selectors)


def border_css(role_name, border, use_color_refs=False):
    width = int(border["width"])
    position = border["position"]

    if width <= 0 or position == "none":
        return "    border: 0;\n"

    if use_color_refs:
        color = color_ref(role_name, "border")
    else:
        color = hex_to_rgba(border["color"], float(border["alpha"]))

    if position == "bottom":
        return f"    border: 0;\n    border-bottom: {width}px solid {color};\n"

    if position == "left":
        return f"    border: 0;\n    border-left: {width}px solid {color};\n"

    if position == "full":
        return f"    border: {width}px solid {color};\n"

    return "    border: 0;\n"


def text_shadow_css(role_name, role, use_color_refs=False):
    shadow = role.get("text_shadow", {})

    if not shadow.get("enabled", False):
        return "    text-shadow: none;\n"

    if use_color_refs:
        color = color_ref(role_name, "shadow")
    else:
        color = hex_to_rgba(
            shadow.get("color", "#000000"),
            float(shadow.get("alpha", 0.75)),
        )

    x = int(shadow.get("x", 2))
    y = int(shadow.get("y", 2))
    blur = int(shadow.get("blur", 4))

    return f"    text-shadow: {x}px {y}px {blur}px {color};\n"


def role_css(role_name, role, preview=False, use_color_refs=False):
    selectors = selector_block(role["selectors"], preview=preview)

    if use_color_refs:
        background = color_ref(role_name, "bg")
    else:
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
{border_css(role_name, role["border"], use_color_refs=use_color_refs)} }}
"""

    if role["text_selectors"]:
        text_selectors = selector_block(role["text_selectors"], preview=preview)

        if use_color_refs:
            text_color = color_ref(role_name, "text")
        else:
            text_color = hex_to_rgba(
                role["text"]["color"],
                float(role["text"]["alpha"]),
            )

        css += f"""
{text_selectors} {{
    color: {text_color};
{text_shadow_css(role_name, role, use_color_refs=use_color_refs)} }}
"""

    return css


def generate_color_definitions(theme_model):
    css = "/* Color palette */\n"

    for role_name, role in theme_model.roles.items():
        css += (
            f"@define-color {color_var_name(role_name, 'bg')} "
            f"{hex_to_rgba(role['background']['color'], float(role['background']['alpha']))};\n"
        )

        if role["text_selectors"]:
            css += (
                f"@define-color {color_var_name(role_name, 'text')} "
                f"{hex_to_rgba(role['text']['color'], float(role['text']['alpha']))};\n"
            )

        border = role["border"]
        if int(border["width"]) > 0 and border["position"] != "none":
            css += (
                f"@define-color {color_var_name(role_name, 'border')} "
                f"{hex_to_rgba(border['color'], float(border['alpha']))};\n"
            )

        shadow = role.get("text_shadow", {})
        if shadow.get("enabled", False):
            css += (
                f"@define-color {color_var_name(role_name, 'shadow')} "
                f"{hex_to_rgba(shadow.get('color', '#000000'), float(shadow.get('alpha', 0.75)))};\n"
            )

    return css


def generate_role_css(theme_model, preview=False, use_color_refs=False):
    css = ""

    for role_name, role in theme_model.roles.items():
        css += role_css(
            role_name,
            role,
            preview=preview,
            use_color_refs=use_color_refs,
        )

    return css


def generate_preview_css(theme_model):
    css = f"""
.ks-preview * {{
    color: #fdf6e3;
    font-size: {int(theme_model.preview_font_size)}px;
    text-shadow: none;
    box-shadow: none;
    border: 0;
}}

.ks-preview {{
    background-color: #13181C;
}}

.ks-preview button {{
    background-image: none;
    transition: padding 0s;
}}

.ks-preview button label {{
    color: #fdf6e3;
}}

.ks-preview .title_bar {{
    min-height: 48px;
}}

.ks-preview .action_bar {{
    min-width: 110px;
}}

.ks-preview .heatergraph {{
    min-height: 220px;
}}
"""

    css += generate_role_css(theme_model, preview=True, use_color_refs=False)

    return css


def generate_theme_css(theme_model):
    css = f"""/*
Generated by KlipperScreen Theme Creator.

Copy this file to:
~/KlipperScreen/styles/{theme_model.theme_name}/style.css
*/

"""

    css += generate_color_definitions(theme_model)

    css += f"""

/* Base rules */
* {{
    font-size: {int(theme_model.preview_font_size)}px;
    text-shadow: none;
    box-shadow: none;
}}

button {{
    background-image: none;
}}

/* Role styles */
"""

    css += generate_role_css(theme_model, preview=False, use_color_refs=True)

    return css
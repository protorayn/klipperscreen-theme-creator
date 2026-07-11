import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")

from gi.repository import Gdk, Gtk, Pango


DEFAULT_TEXT_SHADOW = {
    "enabled": False,
    "color": "#000000",
    "alpha": 0.75,
    "x": 2,
    "y": 2,
    "blur": 4,
}


def rgba_from_hex(hex_color, alpha=1.0):
    rgba = Gdk.RGBA()
    rgba.parse(hex_color)
    rgba.alpha = alpha
    return rgba


def hex_from_rgba(rgba):
    red = round(rgba.red * 255)
    green = round(rgba.green * 255)
    blue = round(rgba.blue * 255)
    return f"#{red:02x}{green:02x}{blue:02x}"


class PropertyPanel(Gtk.Box):
    def __init__(
        self,
        on_property_changed=None,
        on_resolution_changed=None,
        initial_width=1024,
        initial_height=600,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.on_property_changed = on_property_changed
        self.on_resolution_changed = on_resolution_changed
        self.current_role_name = None
        self.current_role = None
        self.loading = False
        self.loading_resolution = False

        self.get_style_context().add_class("property-panel")
        self.set_hexpand(False)
        self.set_vexpand(True)
        self.set_size_request(340, -1)

        title = Gtk.Label(label="Inspector")
        title.get_style_context().add_class("inspector-title")
        title.set_xalign(0)

        self.selected_label = Gtk.Label(label="Selected: none")
        self.selected_label.set_xalign(0)

        self.pack_start(title, False, False, 0)
        self.pack_start(self.build_resolution_controls(initial_width, initial_height), False, False, 0)
        self.pack_start(Gtk.Separator(), False, False, 4)
        self.pack_start(self.selected_label, False, False, 0)

        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        viewport = Gtk.Viewport()
        viewport.add(self.controls_box)

        self.controls_scroll = Gtk.ScrolledWindow()
        self.controls_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.controls_scroll.add(viewport)

        self.pack_start(self.controls_scroll, True, True, 0)

        self.show_empty_state()

    def build_resolution_controls(self, initial_width, initial_height):
        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        wrapper.get_style_context().add_class("resolution-controls")

        label = Gtk.Label(label="Preview Resolution")
        label.set_xalign(0)
        label.get_style_context().add_class("inspector-section-title")
        wrapper.pack_start(label, False, False, 0)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.width_spin = Gtk.SpinButton()
        self.width_spin.set_range(320, 3840)
        self.width_spin.set_increments(10, 100)
        self.width_spin.set_value(int(initial_width))
        self.width_spin.set_numeric(True)
        self.width_spin.connect("value-changed", self.on_resolution_spin_changed)

        x_label = Gtk.Label(label="×")

        self.height_spin = Gtk.SpinButton()
        self.height_spin.set_range(240, 2160)
        self.height_spin.set_increments(10, 100)
        self.height_spin.set_value(int(initial_height))
        self.height_spin.set_numeric(True)
        self.height_spin.connect("value-changed", self.on_resolution_spin_changed)

        row.pack_start(self.width_spin, True, True, 0)
        row.pack_start(x_label, False, False, 0)
        row.pack_start(self.height_spin, True, True, 0)

        wrapper.pack_start(row, False, False, 0)

        return wrapper

    def on_resolution_spin_changed(self, _spin):
        if self.loading_resolution or self.on_resolution_changed is None:
            return

        width = int(self.width_spin.get_value())
        height = int(self.height_spin.get_value())
        self.on_resolution_changed(width, height)

    def clear_controls(self):
        for child in list(self.controls_box.get_children()):
            self.controls_box.remove(child)

    def show_empty_state(self):
        self.clear_controls()

        note = Gtk.Label(label="Click a preview element to edit its style.")
        note.set_line_wrap(True)
        note.set_xalign(0)

        self.controls_box.pack_start(note, False, False, 0)
        self.show_all()

    def set_selected_role(self, role_name, role_data):
        self.current_role_name = role_name
        self.current_role = role_data

        if role_data is None:
            self.selected_label.set_text("Selected: none")
            self.show_empty_state()
            return

        role_data.setdefault("text_shadow", DEFAULT_TEXT_SHADOW.copy())

        self.selected_label.set_text(f"Selected: {role_data['label']}")

        self.loading = True
        self.clear_controls()

        self.add_section_label("Fill")
        self.add_color_control(
            "Background",
            role_data["background"]["color"],
            ("background", "color"),
        )
        self.add_scale_control(
            "Background opacity",
            role_data["background"]["alpha"],
            0.0,
            1.0,
            0.01,
            ("background", "alpha"),
        )

        self.add_section_label("Text")
        self.add_color_control(
            "Text",
            role_data["text"]["color"],
            ("text", "color"),
        )

        if role_data.get("text_selectors"):
            self.add_section_label("Text Shadow")

            self.add_switch_control(
                "Enabled",
                role_data["text_shadow"]["enabled"],
                ("text_shadow", "enabled"),
            )
            self.add_color_control(
                "Shadow color",
                role_data["text_shadow"]["color"],
                ("text_shadow", "color"),
            )
            self.add_scale_control(
                "Shadow opacity",
                role_data["text_shadow"]["alpha"],
                0.0,
                1.0,
                0.01,
                ("text_shadow", "alpha"),
            )
            self.add_scale_control(
                "Shadow X",
                role_data["text_shadow"]["x"],
                -10,
                10,
                1,
                ("text_shadow", "x"),
            )
            self.add_scale_control(
                "Shadow Y",
                role_data["text_shadow"]["y"],
                -10,
                10,
                1,
                ("text_shadow", "y"),
            )
            self.add_scale_control(
                "Shadow blur",
                role_data["text_shadow"]["blur"],
                0,
                20,
                1,
                ("text_shadow", "blur"),
            )

        self.add_section_label("Border")
        self.add_color_control(
            "Border",
            role_data["border"]["color"],
            ("border", "color"),
        )
        self.add_combo_control(
            "Border style",
            role_data["border"]["position"],
            [
                ("none", "None"),
                ("full", "Full"),
                ("bottom", "Bottom"),
                ("left", "Left"),
            ],
            ("border", "position"),
        )
        self.add_scale_control(
            "Border width",
            role_data["border"]["width"],
            0,
            20,
            1,
            ("border", "width"),
        )
        self.add_scale_control(
            "Border radius",
            role_data["border"]["radius"],
            0,
            40,
            1,
            ("border", "radius"),
        )

        self.loading = False
        self.show_all()

    def add_section_label(self, text):
        label = Gtk.Label(label=text)
        label.set_xalign(0)
        label.get_style_context().add_class("inspector-section-title")
        self.controls_box.pack_start(label, False, False, 4)

    def add_color_control(self, label_text, color_hex, path):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        label = Gtk.Label(label=label_text, hexpand=True)
        label.set_xalign(0)
        label.set_max_width_chars(18)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        button = Gtk.ColorButton()
        button.set_rgba(rgba_from_hex(color_hex))
        button.connect("color-set", self.on_color_changed, path)

        row.pack_start(label, True, True, 0)
        row.pack_start(button, False, False, 0)

        self.controls_box.pack_start(row, False, False, 0)

    def add_scale_control(self, label_text, value, minimum, maximum, step, path):
        label = Gtk.Label(label=f"{label_text}: {value}")
        label.set_xalign(0)

        adjustment = Gtk.Adjustment(
            value=float(value),
            lower=float(minimum),
            upper=float(maximum),
            step_increment=float(step),
            page_increment=float(step),
            page_size=0,
        )

        scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=adjustment,
        )
        scale.set_digits(2 if step < 1 else 0)
        scale.set_hexpand(False)
        scale.set_size_request(190, -1)
        scale.connect("value-changed", self.on_scale_changed, label, label_text, path)

        self.controls_box.pack_start(label, False, False, 0)
        self.controls_box.pack_start(scale, False, False, 0)

    def add_combo_control(self, label_text, active_value, options, path):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        label = Gtk.Label(label=label_text, hexpand=True)
        label.set_xalign(0)
        label.set_max_width_chars(18)
        label.set_ellipsize(Pango.EllipsizeMode.END)

        combo = Gtk.ComboBoxText()
        for value, display_text in options:
            combo.append(value, display_text)

        combo.set_active_id(active_value)
        combo.connect("changed", self.on_combo_changed, path)

        row.pack_start(label, True, True, 0)
        row.pack_start(combo, False, False, 0)

        self.controls_box.pack_start(row, False, False, 0)

    def add_switch_control(self, label_text, active, path):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        label = Gtk.Label(label=label_text, hexpand=True)
        label.set_xalign(0)
        label.set_max_width_chars(18)
        label.set_ellipsize(Pango.EllipsizeMode.END)

        switch = Gtk.Switch(active=bool(active))
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("notify::active", self.on_switch_changed, path)

        row.pack_start(label, True, True, 0)
        row.pack_start(switch, False, False, 0)

        self.controls_box.pack_start(row, False, False, 0)

    def on_color_changed(self, color_button, path):
        if self.loading:
            return

        rgba = color_button.get_rgba()
        self.emit_change(path, hex_from_rgba(rgba))

    def on_scale_changed(self, scale, value_label, label_text, path):
        if self.loading:
            return

        value = scale.get_value()

        if path[-1] in {"width", "radius", "padding", "margin", "x", "y", "blur"}:
            value = int(round(value))
            value_label.set_text(f"{label_text}: {value}")
        else:
            value = round(value, 2)
            value_label.set_text(f"{label_text}: {value:.2f}")

        self.emit_change(path, value)

    def on_combo_changed(self, combo, path):
        if self.loading:
            return

        value = combo.get_active_id()
        if value is None:
            return

        self.emit_change(path, value)

    def on_switch_changed(self, switch, _gparam, path):
        if self.loading:
            return

        self.emit_change(path, switch.get_active())

    def emit_change(self, path, value):
        if self.on_property_changed is None or self.current_role_name is None:
            return

        self.on_property_changed(self.current_role_name, path, value)
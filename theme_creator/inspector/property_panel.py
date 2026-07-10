import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk


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
    def __init__(self, on_property_changed=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.on_property_changed = on_property_changed
        self.current_role_name = None
        self.current_role = None
        self.loading = False

        self.get_style_context().add_class("property-panel")
        self.set_size_request(340, -1)

        title = Gtk.Label(label="Inspector")
        title.get_style_context().add_class("inspector-title")
        title.set_xalign(0)

        self.selected_label = Gtk.Label(label="Selected: none")
        self.selected_label.set_xalign(0)

        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.pack_start(title, False, False, 0)
        self.pack_start(self.selected_label, False, False, 0)
        self.pack_start(Gtk.Separator(), False, False, 4)
        self.pack_start(self.controls_box, False, False, 0)

        self.show_empty_state()

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

        self.selected_label.set_text(f"Selected: {role_data['label']}")

        self.loading = True
        self.clear_controls()

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
        self.add_color_control(
            "Text",
            role_data["text"]["color"],
            ("text", "color"),
        )
        self.add_color_control(
            "Border",
            role_data["border"]["color"],
            ("border", "color"),
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

    def add_label(self, text):
        label = Gtk.Label(label=text)
        label.set_xalign(0)
        self.controls_box.pack_start(label, False, False, 0)
        return label

    def add_color_control(self, label_text, color_hex, path):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        label = Gtk.Label(label=label_text, hexpand=True)
        label.set_xalign(0)

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
        scale.set_hexpand(True)
        scale.connect("value-changed", self.on_scale_changed, label, label_text, path)

        self.controls_box.pack_start(label, False, False, 0)
        self.controls_box.pack_start(scale, False, False, 0)

    def on_color_changed(self, color_button, path):
        if self.loading:
            return

        rgba = color_button.get_rgba()
        self.emit_change(path, hex_from_rgba(rgba))

    def on_scale_changed(self, scale, value_label, label_text, path):
        if self.loading:
            return

        value = scale.get_value()

        if path[-1] in {"width", "radius", "padding", "margin"}:
            value = int(round(value))
            value_label.set_text(f"{label_text}: {value}")
        else:
            value = round(value, 2)
            value_label.set_text(f"{label_text}: {value:.2f}")

        self.emit_change(path, value)

    def emit_change(self, path, value):
        if self.on_property_changed is None or self.current_role_name is None:
            return

        self.on_property_changed(self.current_role_name, path, value)
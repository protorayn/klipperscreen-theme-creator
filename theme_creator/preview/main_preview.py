import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MainPreview(Gtk.Box):
    def __init__(self, on_role_selected=None, target_width=1024, target_height=600):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.on_role_selected = on_role_selected
        self.selected_widget = None
        self.target_width = int(target_width)
        self.target_height = int(target_height)
        self.action_bar = None
        self.graph = None

        self.get_style_context().add_class("ks-preview")
        self.get_style_context().add_class("preview-window")

        self.set_hexpand(True)
        self.set_vexpand(True)

        title_bar = self.build_title_bar()
        body = self.build_body()

        self.pack_start(title_bar, False, False, 0)
        self.pack_start(body, True, True, 0)

        self.connect("size-allocate", self.on_size_allocate)

    def set_target_resolution(self, width, height):
        self.target_width = int(width)
        self.target_height = int(height)
        self.queue_resize()

    def on_size_allocate(self, _widget, allocation):
        width = allocation.width
        height = allocation.height

        if self.action_bar is not None:
            action_bar_width = max(70, int(width * 0.10))
            self.action_bar.set_size_request(action_bar_width, -1)

        if self.graph is not None:
            graph_width = max(160, int(width * 0.22))
            graph_height = max(120, int(height * 0.32))
            self.graph.set_size_request(graph_width, graph_height)

    def select_role(self, widget, role_name):
        if self.selected_widget is not None:
            self.selected_widget.get_style_context().remove_class("tc-selected")

        self.selected_widget = widget
        self.selected_widget.get_style_context().add_class("tc-selected")

        if self.on_role_selected is not None:
            self.on_role_selected(role_name)

    def make_clickable_container(self, widget, role_name):
        event_box = Gtk.EventBox()
        event_box.add(widget)
        event_box.connect(
            "button-press-event",
            lambda clicked_widget, event: self.select_role(clicked_widget, role_name),
        )
        return event_box

    def make_clickable_button(self, button, role_name):
        button.connect("clicked", lambda clicked_widget: self.select_role(clicked_widget, role_name))
        return button

    def build_title_bar(self):
        title_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_bar.get_style_context().add_class("title_bar")

        title = Gtk.Label(label="KlipperScreen Preview", hexpand=True)
        title.set_xalign(0)

        temp = Gtk.Label(label="Extruder 215°  Bed 60°")
        clock = Gtk.Label(label="12:45")

        title_bar.pack_start(title, True, True, 8)
        title_bar.pack_start(temp, False, False, 8)
        title_bar.pack_start(clock, False, False, 8)

        return self.make_clickable_container(title_bar, "title_bar")

    def build_body(self):
        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        body.set_hexpand(True)
        body.set_vexpand(True)

        action_bar = self.build_action_bar()
        content = self.build_content()

        body.pack_start(action_bar, False, False, 0)
        body.pack_start(content, True, True, 0)

        return body

    def build_action_bar(self):
        self.action_bar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.action_bar.get_style_context().add_class("action_bar")
        self.action_bar.set_hexpand(False)
        self.action_bar.set_vexpand(True)

        for label in ["Back", "Home", "MMU", "Alert", "Power"]:
            button = Gtk.Button(label=label)
            self.make_clickable_button(button, "action_bar_button")
            self.action_bar.pack_start(button, True, True, 0)

        return self.make_clickable_container(self.action_bar, "action_bar")

    def build_content(self):
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        content.get_style_context().add_class("content")
        content.set_hexpand(True)
        content.set_vexpand(True)

        heater_panel = self.build_heater_panel()
        menu_grid = self.build_menu_grid()

        content.pack_start(heater_panel, False, False, 0)
        content.pack_start(menu_grid, True, True, 0)

        return self.make_clickable_container(content, "content")

    def build_heater_panel(self):
        heater_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        heater_panel.set_size_request(240, -1)
        heater_panel.get_style_context().add_class("heater-list")

        heater_title = Gtk.Label(label="Heaters")
        heater_panel.pack_start(heater_title, False, False, 0)

        for label in ["Extruder 215/220°", "Bed 60/60°", "Chamber 34°"]:
            button = Gtk.Button(label=label)
            button.get_style_context().add_class("graph_label")
            self.make_clickable_button(button, "heater_row")
            heater_panel.pack_start(button, False, False, 0)

        self.graph = Gtk.DrawingArea()
        self.graph.get_style_context().add_class("heatergraph")

        heater_panel.pack_start(
            self.make_clickable_container(self.graph, "heatergraph"),
            True,
            True,
            0,
        )

        return self.make_clickable_container(heater_panel, "heater_list")

    def build_menu_grid(self):
        menu_grid = Gtk.Grid(row_homogeneous=True, column_homogeneous=True)
        menu_grid.set_row_spacing(6)
        menu_grid.set_column_spacing(6)
        menu_grid.set_hexpand(True)
        menu_grid.set_vexpand(True)

        buttons = [
            ("Print", "color1"),
            ("Move", "color2"),
            ("Temperature", "color3"),
            ("Files", "color4"),
            ("Settings", "color1"),
            ("System", "color2"),
            ("Power", "color3"),
            ("Console", "color4"),
        ]

        for index, (label, style_class) in enumerate(buttons):
            button = Gtk.Button(label=label)
            button.get_style_context().add_class(style_class)
            self.make_clickable_button(button, f"button.{style_class}")
            menu_grid.attach(button, index % 4, index // 4, 1, 1)

        return self.make_clickable_container(menu_grid, "menu_grid")
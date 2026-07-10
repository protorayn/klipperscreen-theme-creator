import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from theme_creator.app_style import APP_CSS
from theme_creator.export.css_generator import generate_preview_css
from theme_creator.inspector.property_panel import PropertyPanel
from theme_creator.model.theme_model import ThemeModel
from theme_creator.preview.main_preview import MainPreview


class ThemeCreatorWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="KlipperScreen Theme Creator")

        self.set_default_size(1200, 700)

        self.theme_model = ThemeModel()

        self.app_css_provider = Gtk.CssProvider()
        self.preview_css_provider = Gtk.CssProvider()

        screen = Gdk.Screen.get_default()

        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.app_css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.preview_css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1,
        )

        self.root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.root.get_style_context().add_class("app-root")
        self.root.set_margin_top(8)
        self.root.set_margin_bottom(8)
        self.root.set_margin_start(8)
        self.root.set_margin_end(8)
        self.add(self.root)

        self.inspector = PropertyPanel(on_property_changed=self.on_property_changed)
        self.preview = MainPreview(on_role_selected=self.on_role_selected)

        self.root.pack_start(self.preview, True, True, 0)
        self.root.pack_start(self.inspector, False, False, 0)

        self.apply_app_css()
        self.apply_preview_css()

    def on_role_selected(self, role_name):
        self.theme_model.select_role(role_name)
        role_data = self.theme_model.get_selected_role()
        self.inspector.set_selected_role(self.theme_model.selected_role, role_data)

    def on_property_changed(self, role_name, path, value):
        self.theme_model.update_role_value(role_name, path, value)
        self.apply_preview_css()

    def apply_app_css(self):
        self.app_css_provider.load_from_data(APP_CSS.encode("utf-8"))

    def apply_preview_css(self):
        css = generate_preview_css(self.theme_model)
        self.preview_css_provider.load_from_data(css.encode("utf-8"))


class ThemeCreatorApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="local.klipperscreen.themecreator")

    def do_activate(self):
        win = ThemeCreatorWindow(self)
        win.show_all()
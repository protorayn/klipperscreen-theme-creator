import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from theme_creator.app_style import APP_CSS
from theme_creator.export.css_generator import generate_preview_css, generate_theme_css
from theme_creator.inspector.property_panel import PropertyPanel
from theme_creator.model.theme_model import ThemeModel
from theme_creator.preview.main_preview import MainPreview


class ThemeCreatorWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="KlipperScreen Theme Creator")

        self.set_default_size(1200, 700)
        self.set_size_request(900, 550)

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

        self.preview = MainPreview(
            on_role_selected=self.on_role_selected,
            target_width=self.theme_model.target_width,
            target_height=self.theme_model.target_height,
        )

        self.preview_frame = Gtk.AspectFrame(
            label=None,
            xalign=0.5,
            yalign=0.5,
            ratio=self.get_preview_ratio(),
            obey_child=False,
        )
        self.preview_frame.get_style_context().add_class("preview-frame")
        self.preview_frame.set_hexpand(True)
        self.preview_frame.set_vexpand(True)
        self.preview_frame.add(self.preview)

        self.inspector = PropertyPanel(
            on_property_changed=self.on_property_changed,
            on_resolution_changed=self.on_resolution_changed,
            on_export_requested=self.on_export_requested,
            initial_width=self.theme_model.target_width,
            initial_height=self.theme_model.target_height,
        )

        self.inspector.set_hexpand(False)
        self.inspector.set_vexpand(True)
        self.inspector.set_size_request(340, -1)

        self.root.pack_start(self.preview_frame, True, True, 0)
        self.root.pack_start(self.inspector, False, False, 0)

        self.apply_app_css()
        self.apply_preview_css()

    def get_preview_ratio(self):
        return self.theme_model.target_width / self.theme_model.target_height

    def on_role_selected(self, role_name):
        self.theme_model.select_role(role_name)
        role_data = self.theme_model.get_selected_role()
        self.inspector.set_selected_role(self.theme_model.selected_role, role_data)

    def on_property_changed(self, role_name, path, value):
        self.theme_model.update_role_value(role_name, path, value)
        self.apply_preview_css()

    def on_resolution_changed(self, width, height):
        self.theme_model.set_target_resolution(width, height)
        self.preview.set_target_resolution(width, height)
        self.preview_frame.set_property("ratio", self.get_preview_ratio())
        self.preview_frame.queue_resize()

    def apply_app_css(self):
        self.app_css_provider.load_from_data(APP_CSS.encode("utf-8"))

    def apply_preview_css(self):
        css = generate_preview_css(self.theme_model)
        self.preview_css_provider.load_from_data(css.encode("utf-8"))

    def on_export_requested(self):
        dialog = Gtk.FileChooserDialog(
            title="Export style.css",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )

        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )

        dialog.set_current_name("style.css")
        dialog.set_do_overwrite_confirmation(True)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            css = generate_theme_css(self.theme_model)

            with open(filename, "w", encoding="utf-8") as css_file:
                css_file.write(css)

        dialog.destroy()


class ThemeCreatorApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="local.klipperscreen.themecreator")

    def do_activate(self):
        win = ThemeCreatorWindow(self)
        win.show_all()
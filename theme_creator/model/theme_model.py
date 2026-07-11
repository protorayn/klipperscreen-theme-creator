from copy import deepcopy


DEFAULT_ROLES = {
    "title_bar": {
        "label": "Title Bar",
        "selectors": [".title_bar"],
        "text_selectors": [".title_bar label"],
        "background": {"color": "#002b36", "alpha": 0.95},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#3a4a55",
            "alpha": 1.0,
            "width": 0,
            "radius": 0,
            "position": "none",
        },
        "padding": 6,
        "margin": 0,
    },
    "action_bar": {
        "label": "Action Bar",
        "selectors": [".action_bar"],
        "text_selectors": [".action_bar label"],
        "background": {"color": "#002b36", "alpha": 0.85},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#3a4a55",
            "alpha": 1.0,
            "width": 0,
            "radius": 0,
            "position": "none",
        },
        "padding": 6,
        "margin": 0,
    },
    "action_bar_button": {
        "label": "Action Bar Button",
        "selectors": [".action_bar button"],
        "text_selectors": [".action_bar button label"],
        "background": {"color": "#073642", "alpha": 0.95},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#3a4a55",
            "alpha": 1.0,
            "width": 0,
            "radius": 14,
            "position": "left",
        },
        "padding": 10,
        "margin": 4,
    },
    "content": {
        "label": "Content Area",
        "selectors": [".content"],
        "text_selectors": [".content label"],
        "background": {"color": "#000000", "alpha": 0.30},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#3a4a55",
            "alpha": 1.0,
            "width": 0,
            "radius": 0,
            "position": "none",
        },
        "padding": 8,
        "margin": 0,
    },
    "heater_list": {
        "label": "Heater List Panel",
        "selectors": [".heater-list"],
        "text_selectors": [".heater-list label"],
        "background": {"color": "#002b36", "alpha": 0.75},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#3a4a55",
            "alpha": 1.0,
            "width": 0,
            "radius": 0,
            "position": "none",
        },
        "padding": 8,
        "margin": 0,
    },
    "heater_row": {
        "label": "Heater Row",
        "selectors": [".graph_label"],
        "text_selectors": [".graph_label label"],
        "background": {"color": "#073642", "alpha": 0.95},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#ff5f57",
            "alpha": 1.0,
            "width": 6,
            "radius": 14,
            "position": "left",
        },
        "padding": 10,
        "margin": 4,
    },
    "heatergraph": {
        "label": "Heater Graph",
        "selectors": [".heatergraph"],
        "text_selectors": [],
        "background": {"color": "#ffffff", "alpha": 0.12},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#3a4a55",
            "alpha": 1.0,
            "width": 0,
            "radius": 10,
            "position": "none",
        },
        "padding": 0,
        "margin": 0,
    },
    "button.color1": {
        "label": "Menu Button Color 1",
        "selectors": ["button.color1"],
        "text_selectors": ["button.color1 label"],
        "background": {"color": "#073642", "alpha": 0.95},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#ff8a3d",
            "alpha": 1.0,
            "width": 6,
            "radius": 14,
            "position": "bottom",
        },
        "padding": 10,
        "margin": 4,
    },
    "button.color2": {
        "label": "Menu Button Color 2",
        "selectors": ["button.color2"],
        "text_selectors": ["button.color2 label"],
        "background": {"color": "#073642", "alpha": 0.95},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#ff5fc8",
            "alpha": 1.0,
            "width": 6,
            "radius": 14,
            "position": "bottom",
        },
        "padding": 10,
        "margin": 4,
    },
    "button.color3": {
        "label": "Menu Button Color 3",
        "selectors": ["button.color3"],
        "text_selectors": ["button.color3 label"],
        "background": {"color": "#073642", "alpha": 0.95},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#38d6c2",
            "alpha": 1.0,
            "width": 6,
            "radius": 14,
            "position": "bottom",
        },
        "padding": 10,
        "margin": 4,
    },
    "button.color4": {
        "label": "Menu Button Color 4",
        "selectors": ["button.color4"],
        "text_selectors": ["button.color4 label"],
        "background": {"color": "#073642", "alpha": 0.95},
        "text": {"color": "#fdf6e3", "alpha": 1.0},
        "border": {
            "color": "#b7ff3d",
            "alpha": 1.0,
            "width": 6,
            "radius": 14,
            "position": "bottom",
        },
        "padding": 10,
        "margin": 4,
    },
}


class ThemeModel:
    def __init__(self):
        self.theme_name = "new_theme"
        self.selected_role = None
        self.roles = deepcopy(DEFAULT_ROLES)

    def select_role(self, role_name):
        if role_name in self.roles:
            self.selected_role = role_name
        else:
            self.selected_role = None

    def get_role(self, role_name):
        return self.roles.get(role_name)

    def get_selected_role(self):
        if self.selected_role is None:
            return None
        return self.get_role(self.selected_role)

    def update_role_value(self, role_name, path, value):
        role = self.get_role(role_name)
        if role is None:
            return

        target = role
        for key in path[:-1]:
            target = target[key]

        target[path[-1]] = value
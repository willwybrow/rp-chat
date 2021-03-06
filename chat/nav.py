from flask_login import current_user
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup
from flask import current_app

def navbar():
    return Navbar(current_app.config.get('SITE_NAME'),
                  View('Home', 'home'))

def login_aware_navbar():
    basic_navbar = list(navbar().items)

    if current_user.is_authenticated:
        basic_navbar.extend([
            View('Campaigns', 'campaigns'),
            View('Characters', 'characters'),
            Subgroup('DM', View('Campaigns', 'dm_campaigns'), View('NPCs', 'dm_characters')),
            View('Profile', 'my_profile'),
            View('Logout', 'logout')])
    else:
        basic_navbar.extend([View('Login', 'login')])

    return Navbar(current_app.config.get('SITE_NAME'), *basic_navbar)


def configure_nav(app):
    nav = Nav()
    nav.register_element('basic_navbar', navbar)
    nav.register_element('login_aware_navbar', login_aware_navbar)
    nav.init_app(app)

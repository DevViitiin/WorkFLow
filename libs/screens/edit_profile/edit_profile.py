import json
import os
import re
import cloudinary
import cloudinary.uploader
import cloudinary.api
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, get_color_from_hex
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from plyer import filechooser
from PIL import Image


class EditProfile(MDScreen):
    # Properties
    telefone = StringProperty('(62) 99356-0986')
    city = StringProperty()
    state = StringProperty()
    email = StringProperty('viitiinmec@gmail.com')
    company = StringProperty()
    name_user = StringProperty('Solitude')
    function = StringProperty()
    dont = StringProperty('Sim')  # Changed to StringProperty for consistency
    avatar = StringProperty('https://res.cloudinary.com/dsmgwupky/image/upload/v1742508462/Homen%20de%20ferro.jpg')

    # Constants
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
    CLOUDINARY_CONFIG = {
        "cloud_name": "dsmgwupky",
        "api_key": "256987432736353",
        "api_secret": "K8oSFMvqA6N2eU4zLTnLTVuArMU"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Window setup
        Window.softinput_mode = 'below_target'
        Window.bind(on_keyboard=self.events)
        Window.bind(on_keyboard_height=self.on_keyboard_height)
        self.keyboard_height = 0
        self.manager_open = False

        # Cloudinary configuration
        cloudinary.config(**self.CLOUDINARY_CONFIG)

        self.key = ''
        self.screen_finalize()

    def on_enter(self):
        """Called when the screen enters the window."""
        self.screen_finalize()
        self.update_ui_from_properties()

    def update_ui_from_properties(self):
        """Update UI elements from properties"""
        self.ids.name_user.text = self.name_user
        self.ids.perfil.source = self.avatar

        if 'Não definido' not in (self.telefone, self.email):
            self.ids.telefone.text = self.telefone
            self.ids.email.text = self.email

    # Screen initialization and UI methods
    def screen_finalize(self):
        """Initialize the finalization screen elements"""
        # Error icon
        icone_erro = MDIconButton(
            icon='alert-circle',
            theme_font_size='Custom',
            font_size='55sp',
            theme_icon_color='Custom',
            pos_hint={'center_x': .5, 'center_y': .6},
            icon_color='red'
        )
        self.ids['error'] = icone_erro

        # Success icon
        icone_acerto = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1736292941/true-fotor-20250107203414-removebg-preview_ajd1xd.png',
            size_hint=(None, None),
            size=("100dp", "150dp"),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            allow_stretch=True
        )
        self.ids['acerto'] = icone_acerto

        # Card container
        self.card = MDCard(
            id='carregando',
            style='elevated',
            size_hint=(1, 1),
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            padding="16dp",
            md_bg_color=(1, 1, 1, 1),
            theme_bg_color="Custom",
            theme_shadow_offset="Custom",
            shadow_offset=(1, -2),
            theme_shadow_softness="Custom",
            shadow_softness=1,
            theme_elevation_level="Custom",
            elevation_level=2
        )
        self.ids['card'] = self.card

        # RelativeLayout for content
        relative = MDRelativeLayout()
        self.ids['relative'] = relative

        # Progress indicator
        circle = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=("60dp", "60dp"),
            pos_hint={'center_x': .5, 'center_y': .7}
        )
        self.ids['progress'] = circle

        # Loading text
        label = MDLabel(
            text='Carregando...',
            font_style='Headline',
            role='medium',
            halign='center',
            bold=True,
            text_color='black',
            pos_hint={'center_x': .5, 'center_y': .9}
        )
        self.ids['texto_carregando'] = label

        # Success message
        label_2 = MDLabel(
            text='Os dados do seu perfil já foram devidamente alterados',
            font_style='Title',
            role='small',
            halign='center',
            bold=False,
            text_color='gray',
            pos_hint={'center_x': .5, 'center_y': .5}
        )

        # OK button
        button = MDButton(
            MDButtonText(
                text='Ok',
                theme_text_color='Custom',
                text_color='black',
                font_style='Title',
                role='medium',
                halign='center',
                bold=True,
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            ),
            theme_bg_color='Custom',
            md_bg_color=(0.0, 1.0, 0.0, 1.0),
            pos_hint={'center_x': .5, 'center_y': .35},
            style='tonal',
            theme_width='Custom',
            size_hint_x=.4,
        )
        self.ids['ok'] = button
        self.ids.ok.on_release = self.login_variables

        # Add widgets to RelativeLayout
        relative.add_widget(button)
        relative.add_widget(icone_acerto)
        relative.add_widget(circle)
        relative.add_widget(label)
        relative.add_widget(label_2)

        # Add RelativeLayout to card
        self.card.add_widget(relative)

    # Keyboard handling
    def on_keyboard_height(self, window, height):
        """Called when keyboard height changes"""
        self.keyboard_height = height
        if height == 0:  # Keyboard closed
            self.pos = (0, 0)  # Reset position
        else:  # Keyboard open
            self.pos = (0, height * 0.1)  # Move interface up

    def on_touch_down(self, touch):
        """Close keyboard when tapping outside text fields"""
        if self.keyboard_height > 0:  # Keyboard is open
            fields_focused = any(
                self.ids[field].collide_point(*touch.pos) for field in ['email', 'name_user', 'telefone'])
            if not fields_focused:
                for field in ['email', 'name_user', 'telefone']:
                    if hasattr(self.ids[field], 'focus'):
                        self.ids[field].focus = False
                self.pos = (0, 0)  # Reset position
        return super().on_touch_down(touch)

    def events(self, window, key, scancode, codepoint, modifier):
        """Handle key events"""
        if key == 27:  # ESC key
            self.pos = (0, 0)  # Reset position
            return True
        return False

    def scroll_to_widget(self, widget):
        """Scroll the screen to make a widget visible when it's focused"""

        def _scroll(*args):
            scrollview = self.ids.get("scroll")
            if scrollview:
                keyboard_height = Window.keyboard_height * Window.height
                widget_y = widget.to_window(*widget.pos)[1]
                if widget_y < keyboard_height + dp(50):
                    scrollview.scroll_y = max(0, 1 - (keyboard_height / Window.height))

        Clock.schedule_once(_scroll, 0.1)

    # Image handling
    def recortar_imagem_circular(self, imagem_path):
        """Upload and crop image to circular shape using Cloudinary"""
        try:
            response = cloudinary.uploader.upload(
                imagem_path,
                public_id=self.name_user,
                overwrite=True,
                transformation=[
                    {'width': 1000, 'height': 1000, 'crop': 'thumb', 'gravity': 'face', 'radius': 'max'}
                ]
            )
            self.ids.perfil.source = response['secure_url']
            self.step_one()
            return response['secure_url']
        except Exception as e:
            self.show_error(f"Erro ao cortar a imagem: {e}")
            return None

    def open_gallery(self):
        """Open gallery to select an image"""
        if self.dont == 'Não':
            self.show_message('Galeria não disponível')
            return

        try:
            filechooser.open_file(
                filters=["*.jpg", "*.png", "*.jpeg"],
                on_selection=self.select_path
            )
        except Exception as e:
            self.show_error(f"Erro ao abrir a galeria: {e}")

    def select_path(self, selection):
        """Handle selected image file"""
        if selection:
            path = selection[0]
            self.recortar_imagem_circular(path)
            self.show_message(f"Arquivo selecionado: {path}")

    # Validation methods
    def is_email_valid(self, text):
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, text) is not None

    def on_text_two(self, instance, numero):
        """Format phone number"""
        numero = re.sub(r'\D', '', numero)
        if len(numero) == 11:
            self.ids.telefone.text = f"({numero[0:2]}) {numero[2:7]}-{numero[7:]}"
            self.ids.telefone.focus = False
        else:
            self.ids.telefone.error = True

    # Form validation and submission
    def step_one(self):
        """Validate form fields and submit if valid"""
        # Check for empty fields
        for field_id, name in [('telefone', 'telefone'), ('email', 'e-mail'), ('name_user', 'nome')]:
            if not self.ids[field_id].text:
                self.ids[field_id].focus = True
                self.show_error(f"Por favor, preencha o campo {name}")
                return

        # Validate email
        if not self.is_email_valid(self.ids.email.text):
            self.ids.email.focus = True
            self.show_error("Por favor, insira um e-mail válido")
            return

        # Check for changes in any field
        if (self.ids.email.text != self.email or
                self.ids.telefone.text != self.telefone or
                self.ids.name_user.text != self.name_user or
                self.avatar != self.ids.perfil.source):
            self.update_database()
        else:
            self.show_message("Apresente novos dados para atualização", color='#00b894')

    # Firebase database operations
    def update_database(self):
        """Initialize database update process"""
        url = f'{self.FIREBASE_URL}/Users'
        UrlRequest(
            url=f'{url}/.json',
            on_success=self.update_database_2,
            on_error=self.handle_error,
            on_failure=self.handle_error,
            on_progress=self.show_progress,
            timeout=10
        )

    def update_database_2(self, req, users):
        """Find the user record in the database"""
        if not users:
            self.show_error("Nenhum usuário encontrado")
            return

        name = self.name_user
        for key, value in users.items():
            if value.get('name') == name:
                self.key = key
                self.update_database_3(key)
                return

        self.show_error("Usuário não encontrado")

    def update_database_3(self, key):
        """Update the user data in Firebase"""
        url = f'{self.FIREBASE_URL}/Users/{key}'
        data = {
            'name': str(self.ids.name_user.text).replace(' ', ''),
            'email': self.ids.email.text,
            'perfil': self.ids.perfil.source,
            'telefone': self.ids.telefone.text
        }

        UrlRequest(
            f'{url}/.json',
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.database_success,
            on_error=self.handle_error,
            on_progress=self.show_progress,
            timeout=10
        )

    def database_success(self, req, result):
        """Handle successful user data update"""
        # Update functions and employees
        functions_url = f'{self.FIREBASE_URL}/Functions/.json'
        employees_url = f'{self.FIREBASE_URL}/Funcionarios/.json'

        UrlRequest(
            url=functions_url,
            on_success=self.get_functions,
            on_error=self.handle_error
        )

        UrlRequest(
            url=employees_url,
            on_success=self.get_employees,
            on_error=self.handle_error,
            timeout=10
        )

    def get_functions(self, req, result):
        """Find and update functions linked to this user"""
        if not result:
            return

        update_count = 0
        for func_id, info in result.items():
            if info.get('Contractor') == self.name_user:
                self.change_function(func_id)
                update_count += 1

        if update_count == 0:
            # No functions to update, check if employees are done
            self.check_updates_complete()

    def get_employees(self, req, result):
        """Find and update employees linked to this user"""
        if not result:
            return

        update_count = 0
        for emp_id, info in result.items():
            if info.get('contractor') == self.name_user:
                self.change_employee(emp_id)
                update_count += 1

        if update_count == 0:
            # No employees to update, check if functions are done
            self.check_updates_complete()

    def change_function(self, func_id):
        """Update a function record"""
        url = f'{self.FIREBASE_URL}/Functions/{func_id}/.json'
        data = {
            'Contractor': self.ids.name_user.text
        }
        UrlRequest(
            url,
            req_body=json.dumps(data),
            method='PATCH',
            on_success=self.handle_function_update,
            on_error=self.handle_error,
            timeout=10
        )

    def change_employee(self, emp_id):
        """Update an employee record"""
        url = f'{self.FIREBASE_URL}/Funcionarios/{emp_id}/.json'
        data = {
            'contractor': self.ids.name_user.text
        }
        UrlRequest(
            url,
            req_body=json.dumps(data),
            method='PATCH',
            on_success=self.handle_employee_update,
            on_error=self.handle_error,
            timeout=10
        )

    # Update handlers
    def handle_function_update(self, req, result):
        """Handle successful function update"""
        self.check_updates_complete()

    def handle_employee_update(self, req, result):
        """Handle successful employee update"""
        self.check_updates_complete()

    def check_updates_complete(self):
        """Check if all updates are complete and finalize"""
        # This is a simplified approach; you might need a more robust solution
        # for tracking multiple async requests
        Clock.schedule_once(lambda dt: self.login_variables(), 1)

    # Utility methods
    def show_progress(self, request, current_size, total_size):
        """Display progress of network operations"""
        if total_size > 0:
            progress_percent = (current_size / total_size) * 100
            print(f"Progresso: {progress_percent:.2f}%")

    def show_message(self, message, color='#2196F3'):
        """Display a snackbar message"""
        MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.8,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color)
        ).open()

    def show_error(self, error_message):
        """Display an error message"""
        self.show_message(error_message, color='#FF0000')
        print(f"Error: {error_message}")

    def handle_error(self, req, result):
        """Handle request errors"""
        self.show_error(f"Erro na operação: {result}")

    # Screen transitions
    def next_page(self):
        """Navigate to the next page and pass data"""
        app = MDApp.get_running_app()
        screen_manager = app.root
        edit_two = screen_manager.get_screen('EditProfileTwo')

        # Transfer data to next screen
        edit_two.name_user = self.ids.name_user.text
        edit_two.company = self.company
        edit_two.state = self.state
        edit_two.city = self.city
        edit_two.telefone = self.ids.telefone.text
        edit_two.avatar = self.ids.perfil.source
        edit_two.email = self.ids.email.text
        edit_two.function = self.function

        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'EditProfileTwo'

    def login(self):
        """Return to profile screen"""
        app = MDApp.get_running_app()
        screen_manager = app.root
        perfil = screen_manager.get_screen('Perfil')
        perfil.avatar = self.ids.perfil.source

        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Perfil'

    def login_variables(self):
        """Return to profile screen with updated variables"""
        app = MDApp.get_running_app()
        screen_manager = app.root
        perfil = screen_manager.get_screen('Perfil')

        # Transfer updated data to profile screen
        perfil.telefone = self.ids.telefone.text
        perfil.username = self.ids.name_user.text
        perfil.email = self.ids.email.text
        perfil.company = self.company
        perfil.state = self.state
        perfil.avatar = self.ids.perfil.source

        # Clean up and transition
        if hasattr(self, 'card') and self.card in self.children:
            self.remove_widget(self.card)
        self.manager.current = 'Perfil'
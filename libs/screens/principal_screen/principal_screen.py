from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


class PerfilScreen(MDScreen):
    username = StringProperty()
    avatar = StringProperty()
    key = StringProperty()
    city = StringProperty()
    state = StringProperty()
    company = StringProperty()
    telefone = StringProperty()
    local_id = StringProperty()
    token_id = StringProperty()
    email = StringProperty()
    refresh_token = StringProperty()
    contratando = 'Sim'
    function = StringProperty()
    adicionado = 0
    cont = 0
    table = BooleanProperty(False)
    current_nav_state = StringProperty('perfil')

    def on_enter(self, *args):
        print('Local id do usuario: ', self.local_id)
        print('Token id do usuario: ', self.token_id)
        print('Key do funcionario: ', self.key)
        print('Refresh Token: ', self.refresh_token)
        self.ids.perfil.source = self.avatar
        self.ids.username.text = self.username
        self.ids.company.text = self.company
        if 'Não definido' in (self.city, self.state):
            self.ids.locate.text = f'Não definido'
        else:
            self.ids.locate.text = f'{self.city}, {self.state}'
        self.ids.function.text = f'{self.function}'
        self.ids.telefone.text = f'{self.telefone}'
        self.ids.email.text = f'{self.email}'

    def page(self):
        self.manager.current = 'Function'

    def functions(self):
        if self.contratando == 'Sim':
            self.manager.transition = SlideTransition(direction='left')
            app = MDApp.get_running_app()
            screen_manager = app.root
            edit = screen_manager.get_screen('FunctionsScreen')
            edit.contractor = self.username
            edit.occupation = self.function
            edit.token_id = self.token_id
            edit.local_id = self.local_id
            edit.refresh_token = self.refresh_token
            edit.email = self.email
            edit.key_contractor = self.key
            edit.telephone = self.telefone
            edit.company = self.company
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'FunctionsScreen'

    def edit_profile(self):
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        edit = screen_manager.get_screen('EditProfile')
        edit.name_user = self.username
        edit.email = self.email
        edit.telefone = self.telefone
        edit.state = self.state
        edit.city = self.city
        edit.company = self.company
        edit.avatar = self.avatar
        edit.function = self.function
        self.manager.current = 'EditProfile'

    def search(self):
        app = MDApp.get_running_app()
        print('Passando essa key pra tela de search:', self.key)
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('VacancyContractor')
        bricklayer.key_contractor = self.key
        bricklayer.username = self.username
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = True
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'search'
        screen_manager.current = 'VacancyContractor'

    def request(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('RequestContractor')
        bricklayer.key = self.key
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = True
        bricklayer.current_nav_state = 'request'
        bricklayer.name_contractor = self.username
        screen_manager.current = 'RequestContractor'

    def bricklayer(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('Table')
        bricklayer.key = self.key
        bricklayer.username = self.username
        bricklayer.ids.table.active = True
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'table'
        screen_manager.current = 'Table'


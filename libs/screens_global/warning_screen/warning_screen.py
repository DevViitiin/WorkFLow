from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
import ast
from kivy.uix.screenmanager import SlideTransition
import json
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock

class WarningScreen(MDScreen):
    data_user = ObjectProperty()
    local_id = StringProperty()
    token_id = StringProperty()
    refresh_token = StringProperty()
    api_key = StringProperty()
    type_user = StringProperty()
    motive = StringProperty()
    type = StringProperty()
    description = StringProperty()
    data = StringProperty()
    can_next = False
    
    
    def on_enter(self, *args):
        """Organiza os componentes visuais da tela de warning"""
        self.ids.data.text = f'{self.data}'
        self.ids.motive.text = f'{self.motive}'
        self.ids.description.text = f'{self.description}'
        
        if self.type in "leve":
            self.ids.warning_bg.md_bg_color = get_color_from_hex("#FFFFFF")
            self.ids.warning_text.text = "[color=#000000ff]Infração[/color] [color=#00FF00]Leve[/color]"
        
        elif self.type in "médio":
            self.ids.warning_bg.md_bg_color = get_color_from_hex("#FFFFFF")
            self.ids.warning_text.text = "[color=#000000ff]Infração[/color] [color=#F2DC5D]média[/color]"
        
        elif self.type in "grave":
            self.ids.warning_bg.md_bg_color = get_color_from_hex("#FFFFFF")
            self.ids.warning_text.text = "[color=#000000ff]Infração[/color] [color=#D00000]grave[/color]"

        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)
        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.remove_warning)
        )
        self.dialog_not_net_database = DialogNoNet(
            subtitle='Não foi carregar funções. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_handle(self.remove_warning_contractor)
        )
        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')

    def next_screen(self, *args):

        if self.type_user in 'employee':
            self.remove_warning()

        else:
            self.remove_warning_contractor()
            
        
    def remove_warning(self):
        url = f"{firebase_url()}/Funcionarios/{self.local_id}/warnings.json?auth={self.token_id}"
        # Dados que você quer enviar (todos os campos em branco)
        dados = {
            "motive": "",
            "description": "",
            "type": "",
            "data": ""
        }

        headers = {'Content-Type': 'application/json'}

        UrlRequest(
            url,
            req_body=json.dumps(dados),
            req_headers=headers,
            on_success=self.finnaly_employee,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure,
            method='PATCH'  # usa PATCH pra atualizar só esses campos
        )
    
    def remove_warning_contractor(self):
        url = f"{firebase_url()}/Users/{self.local_id}/warnings.json?auth={self.token_id}"
        
        # Dados que você quer enviar (todos os campos em branco)
        dados = {
            "motive": "",
            "description": "",
            "type": "",
            "data": ""
        }

        headers = {'Content-Type': 'application/json'}

        UrlRequest(
            url,
            req_body=json.dumps(dados),
            req_headers=headers,
            on_success=self.end_task,
            on_erro=self.signcontroller.on_error,
            on_failure=self.signcontroller.on_failure,
            method='PATCH'  # usa PATCH pra atualizar só esses campos
        )
            
    def finnaly_employee(self, req, result):
        try:
            self.signcontroller.close_all_dialogs()
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('PrincipalScreenEmployee')

            # Atribui os dados do funcionário à tela de perfil
            perfil.employee_name = self.data_user.get('Name', '')
            perfil.contractor = self.data_user.get('contractor', '')
            perfil.employee_function = self.data_user.get('function', '')
            perfil.employee_mail = self.data_user.get('email', '')
            perfil.request = ast.literal_eval(self.data_user.get('request', '[]'))
            perfil.employee_telephone = self.data_user.get('telefone', '')
            perfil.avatar = self.data_user.get('avatar', '')
            perfil.city = self.data_user.get('city', '')
            perfil.api_key = self.api_key
            perfil.salary = self.data_user['salary']
            perfil.data_contractor = self.data_user['data_contractor']
            perfil.state = self.data_user.get('state', '')
            perfil.employee_summary = self.data_user.get('sumary', '')
            perfil.skills = self.data_user.get('skills', '[]')
            perfil.api_key = self.api_key
            perfil.refresh_token = self.refresh_token
            perfil.token_id = self.token_id
            perfil.local_id = self.local_id
            
            # Navega para a tela principal do funcionário
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'
        except:
            self.dialog_error_unknown()

    def end_task(self, req, result):
        try:
            self.signcontroller.close_all_dialogs()
            app = MDApp.get_running_app()
            screen_manager = app.root
            perfil = screen_manager.get_screen('Perfil')

            # Atribui os dados do contratante à tela de perfil
            perfil.function = self.data_user.get('function', '')
            perfil.username = self.data_user.get('name', '')
            perfil.avatar = self.data_user.get('perfil', '')
            perfil.telefone = self.data_user.get('telefone', '')
            perfil.state = self.data_user.get('state', '')
            perfil.city = self.data_user.get('city', '')
            perfil.company = self.data_user.get('company', '')
            perfil.email = self.data_user.get('email', '')
            perfil.local_id = self.local_id
            perfil.token_id = self.token_id
            perfil.refresh_token = self.refresh_token
            perfil.api_key = self.api_key

            self.type = self.data_user.get('type', '')
            self.manager.transition = SlideTransition(direction='left')
            
            self.manager.current = 'Perfil'
        except:
            self.dialog_error_unknown()
        

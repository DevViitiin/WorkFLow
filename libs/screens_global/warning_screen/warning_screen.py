from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
import ast
from kivy.uix.screenmanager import SlideTransition
import json
from kivy.network.urlrequest import UrlRequest


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
    
    def next_screen(self, *args):
        print('Dados do usuario: ', self.data_user)
        print('Tipo de usuario: ', self.type_user)
        if self.type_user in 'employee':
            self.remove_warning(self.local_id)
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

        else:
            app = MDApp.get_running_app()
            screen_manager = app.root
            self.remove_warning_contractor()
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
        
    def remove_warning(self, local_id):
        print('Removendo a advertência')
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}/warnings.json?auth={self.token_id}"
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
            method='PATCH'  # usa PATCH pra atualizar só esses campos
        )
    
    def remove_warning_contractor(self):
        print('Removendo a advertência rsrsrsrsrsrss')
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Users/{self.local_id}/warnings.json?auth={self.token_id}"
        
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
            method='PATCH'  # usa PATCH pra atualizar só esses campos
        )
            

    def end_task(self, req, result):
        print('Task finalizada rsrsrsrsrsrsrsrsrsrsrsrsrrsrsrsrsrs')            
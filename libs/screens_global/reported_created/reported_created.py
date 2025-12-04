# main.py
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.animation import Animation
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer, MDDialogContentContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
import time
from kivymd.app import MDApp
import ast
from kivy.uix.screenmanager import SlideTransition
from kivy.network.urlrequest import UrlRequest


class ReportedCreated(MDScreen):
    # variaveis necessarias para fazer requisições 
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    perso = StringProperty()

    def on_enter(self):
        # Animação de entrada do ícone
        icon = self.ids.icon_success
        icon.opacity = 0
        anim = Animation(opacity=1, duration=0.8, t='out_cubic')
        anim.start(icon)
        
        # Animação de pulso no ícone
        def animate_pulse(dt):
            anim_pulse = Animation(font_size=dp(110), duration=0.5, t='out_quad') + \
                        Animation(font_size=dp(105), duration=0.5, t='in_quad')
            anim_pulse.repeat = True
            anim_pulse.start(icon)
        
        Clock.schedule_once(animate_pulse, 0.8)
    
    def show_error_dialog(self):
        """Mostra dialog moderno de erro de requisição"""

        if not hasattr(self, 'error_dialog') or not self.error_dialog:
            self.error_dialog = MDDialog(
                MDDialogIcon(
                    icon="wifi-off",
                    theme_icon_color="Custom",
                    icon_color=(0.95, 0.26, 0.21, 1),
                ),
                MDDialogHeadlineText(
                    text="Ops! Algo deu errado", 
                    halign="center",
                ),
                MDDialogSupportingText(
                    text="[size=15]Não conseguimos conectar ao servidor.[/size]\n\n"
                        "[b]Verifique:[/b]\n"
                        "  •  Conexão com a internet\n"
                        "  •  Se o problema persiste\n\n"
                        "[size=13][color=#666666]Ainda com problemas?[/color][/size]\n"
                        "[b]Entre em contato:[/b] [ref=copy][u]suporteobra@gmail.com[/u][/ref]  [size=12]📋[/size]",
                    halign="left",
                    markup=True,
                    on_ref_press=lambda instance, ref: self.copy_email()
                ),
            MDDialogButtonContainer(
                
                MDButton(
                    MDButtonText(
                        text="FECHAR",
                        font_style='Label',
                        role='medium',
                        theme_text_color='Custom',
                        text_color='black',
                        ),
                    style="text",
                    on_release=lambda x: self.error_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(
                        text="TENTAR NOVAMENTE",
                        font_style='Label',
                        role='medium',
                        bold=True,
                        theme_text_color='Custom',
                        text_color='white',
                        halign='center',
                        pos_hint={'center_x': 0.5, 'center_y': 0.5}
                        ),

                    style="text",
                    theme_bg_color='Custom',
                    md_bg_color='blue',
                    theme_width="Custom",
                    on_release=lambda x: self.retry_connection()
                ),
                spacing=dp(12),
            ),
                
            )
        self.error_dialog.open()
    
    def retry_connection(self):
        """Chamando a verificação denovo"""
        self.next_screen()

    def next_screen(self, *args):
        """Voltar para a tela principal"""
        if self.perso == 'Employee':
            print('O usuario é funcionario chamar principalscreenemployee')
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}.json?auth={self.token_id}'
            UrlRequest(
                url,
                method='GET',
                on_success=self.next_employee,
                on_error=self.error,
                on_failure=self.error,
                on_cancel=self.error,
                req_headers={"Content-Type": "application/json"}
            )
        else:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Users/{self.local_id}.json?auth={self.token_id}'
            UrlRequest(
                url,
                method='GET',
                on_success=self.next_contractor,
                on_error=self.error,
                on_failure=self.error,
                on_cancel=self.error,
                req_headers={"Content-Type": "application/json"}
            )


    def next_employee(self, req, result):
        """Chama a tela do funcionario """
        if result:
            app = MDApp.get_running_app()
            screenmanager = app.root
            perfil = screenmanager.get_screen('PrincipalScreenEmployee')

            # Atribui os dados do funcionário à tela de perfil
            perfil.employee_name = result.get('Name', '')
            perfil.contractor = result.get('contractor', '')
            perfil.employee_function = result.get('function', '')
            perfil.employee_mail = result.get('email', '')
            perfil.request = ast.literal_eval(result.get('request', '[]'))
            perfil.employee_telephone = result.get('telefone', '')
            perfil.avatar = result.get('avatar', '')
            perfil.city = result.get('city', '')
            perfil.api_key = self.api_key
            perfil.salary = result['salary']
            perfil.data_contractor = result['data_contractor']
            perfil.state = result.get('state', '')
            perfil.employee_summary = result.get('sumary', '')
            perfil.skills = result.get('skills', '[]')
            perfil.refresh_token = self.refresh_token
            perfil.token_id = self.token_id
            perfil.local_id = self.local_id
            print('O local id do employee: ', self.local_id)
            print('O token id do employee: ', self.token_id)
            # Navega para a tela principal do funcionário
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'PrincipalScreenEmployee'
        else:
            print('Por algum motivo o resultado voltou none')

    def next_contractor(self, req, result):
        """Chama a tela principal do contratante """
        # Login normal - passa tokens para AMBAS as telas
        app = MDApp.get_running_app()
        screen_manager = app.root
        
        # 2. Configura tela Perfil (IMPORTANTE: passar os tokens aqui também!)
        perfil_screen = screen_manager.get_screen('Perfil')
        perfil_screen.function = result.get('function', '')
        perfil_screen.username = result.get('name', '')
        perfil_screen.avatar = result.get('perfil', '')
        perfil_screen.telefone = result.get('telefone', '')
        perfil_screen.state = result.get('state', '')
        perfil_screen.city = result.get('city', '')
        perfil_screen.company = result.get('company', '')
        perfil_screen.email = result.get('email', '')
        perfil_screen.local_id = self.local_id
        perfil_screen.token_id = self.token_id
        perfil_screen.refresh_token = self.refresh_token
        perfil_screen.api_key = self.api_key
        screen_manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Perfil'
            

    def created_other_reported(self, *args):
        """Função para criar chamar a tela e criar outra denúncia"""
        app = MDApp.get_running_app()
        screenmanager = app.root
        report = screenmanager.get_screen('ReportScreen')
        report.token_id = self.token_id
        report.local_id = self.local_id
        report.refresh_token = self.refresh_token
        report.api_key = self.api_key
        report.perso = self.perso
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'ReportScreen'

    def error(self, req, error):
        """Chama um dialog de erro na tela"""
        print('Deu erro nessa budega KKKKKKKKKK')
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.lang.builder import Builder
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController



Builder.load_file('libs/screens_global/identify_perfil/identify_perfil.kv')
class IdentifyPerfil(MDScreen):
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    local_id = StringProperty()
    avatar = StringProperty()
    nami = StringProperty()
    type = StringProperty()
    email = StringProperty()
    perso = StringProperty()
    key_accused = StringProperty()
    
    def on_enter(self, *args):
        """Inicializa as variaveis e funções necessarias"""
        if self.type == 'Employee':
            self.ids.type.text = 'Funcionário'
        else:
            self.ids.type.text = 'Contratante'
        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')
        print('Key do denunciado: ', self.key_accused)

    def back_screen(self, *args):
        """Voltando para a tela anterior"""
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            report = screenmanager.get_screen('ReportScreen')
            report.token_id = self.token_id
            report.local_id = self.local_id
            report.name_sender = self.name_sender
            report.email_sender = self.email_sender
            report.refresh_token = self.refresh_token
            report.api_key = self.api_key
            report.perso = self.perso
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'ReportScreen'
        except:
            self.dialog_error_unknown()
        
    def next_screen(self, *args):
        """Vai para a tela de denunciar contratante"""
        print('=' * 50)
        print('Indo para tela ReportContractor')
        
        # Agenda a navegação para o próximo tick do Clock
        Clock.schedule_once(lambda dt: self._navigate_to_report(), 0.1)
        print('=' * 50)

    def _navigate_to_report(self):
        """Navega para a tela de perfil (executado após o delay)"""
        try:
            # Pega a tela que já sabemos que existe
            ind_perfil = self.manager.get_screen('ReportContractor')
            print("✅ Tela encontrada!")
            
            # Define as propriedades
            ind_perfil.token_id = self.token_id
            ind_perfil.refresh_token = self.refresh_token
            ind_perfil.local_id = self.local_id
            ind_perfil.api_key = self.api_key
            ind_perfil.perso = self.perso
            ind_perfil.type = self.type
            ind_perfil.name_sender = self.name_sender
            ind_perfil.email_sender = self.email_sender
            ind_perfil.key_accused = self.key_accused
            # ✅ Use este método alternativo que FORÇA a mudança
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'ReportContractor'  # Em vez de self.manager.current
            
            print("✅ Navegação concluída!")
            
        except Exception as e:
            print(f"❌ Erro ao trocar de tela: {e}")
            self.dialog_error_unknown()
    
    def back_screen(self, *args):
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            home = screenmanager.get_screen('IdentifyContractor')
            home.token_id = self.token_id
            home.perso = self.perso
            home.local_id = self.local_id
            home.refresh_token = self.refresh_token
            home.api_key = self.api_key
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'IdentifyContractor'
        except:
            self.dialog_error_unknown()
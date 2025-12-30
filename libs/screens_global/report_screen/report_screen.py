from kivymd.uix.screen import MDScreen
import smtplib
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.text import MIMEText
from kivy.properties import StringProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp


class ReportScreen(MDScreen):
    # informações necessarias para a criação da denuncia
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    api_key = StringProperty()
    perso = StringProperty()
    email_sender = StringProperty()
    name_sender = StringProperty()
    
    # Enviar email após
    def next_screen_contractor(self, *args):
        """Chamar a tela de indentificar contratante"""
        app = MDApp.get_running_app()
        screenmanager = app.root
        
        # Verificar se a tela existe, se não, adicionar novamente
        if not screenmanager.has_screen('IdentifyContractor'):
            from libs.screens_global.identify_contractor.identify_contractor import IdentifyContractor
            screenmanager.add_widget(IdentifyContractor(name='IdentifyContractor'))
        
        report = screenmanager.get_screen('IdentifyContractor')
        report.token_id = self.token_id
        report.local_id = self.local_id
        report.refresh_token = self.refresh_token
        report.name_sender = self.name_sender
        report.email_sender = self.email_sender
        report.api_key = self.api_key
        report.perso = self.perso
        report.type = 'Contractor'
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'IdentifyContractor'
    
    def next_screen_employee(self, *args):
        """Chamar a tela de indentificar funcionario"""
        app = MDApp.get_running_app()
        screenmanager = app.root
        
        # Verificar se a tela existe, se não, adicionar novamente
        if not screenmanager.has_screen('IdentifyContractor'):
            from libs.screens_global.identify_contractor.identify_contractor import IdentifyContractor
            screenmanager.add_widget(IdentifyContractor(name='IdentifyContractor'))
        
        report = screenmanager.get_screen('IdentifyContractor')
        report.token_id = self.token_id
        report.local_id = self.local_id
        report.refresh_token = self.refresh_token
        report.name_sender = self.name_sender
        report.email_sender = self.email_sender
        report.api_key = self.api_key
        report.perso = self.perso
        report.type = 'Employee'
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'IdentifyContractor'
    
    def back_screen(self, *args):
        """Volta para a tela anterior"""
        if self.perso == 'Employee':
            app = MDApp.get_running_app()
            screenmanager = app.root
            home = screenmanager.get_screen('PrincipalScreenEmployee')
            home.token_id = self.token_id
            home.local_id = self.local_id
            home.refresh_token = self.refresh_token
            home.api_key = self.api_key
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'PrincipalScreenEmployee'
        else:
            app = MDApp.get_running_app()
            screenmanager = app.root
            home = screenmanager.get_screen('Perfil')
            home.token_id = self.token_id
            home.local_id = self.local_id
            home.refresh_token = self.refresh_token
            home.api_key = self.api_key
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'Perfil'
            
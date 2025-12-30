from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from threading import Thread
import smtplib
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.text import MIMEText
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window
import ast
from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import get_color_from_hex
import json
from kivy.properties import StringProperty, BooleanProperty
from configurations import (DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, 
                           firebase_url, SignController)


class ReportChat(MDScreen):
    # ==================== PROPERTIES ====================
    FIREBASE_URL = firebase_url()
    
    # User Info
    avatar = StringProperty()
    username = StringProperty()
    name_sender = StringProperty()
    email_sender = StringProperty()
    
    # Auth
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    
    # Report Info
    chat_id = StringProperty()
    perso = StringProperty()
    type = StringProperty()
    key_accused = StringProperty()
    
    # State
    is_submitting = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_motive = None

    # ==================== LIFECYCLE METHODS ====================
    def on_enter(self):
        """Inicializa a tela quando entra"""
        print('🏗️ Tela ReportChat carregada')
        
        # Define o tipo baseado na persona
        if self.perso == 'Employee':
            self.type = 'contractor'
        else:
            self.type = 'employee'

        print('='*50)
        print(f'🔑 Token: {self.token_id[:20]}...')
        print(f'👤 Persona: {self.perso}')
        print(f'🎯 Tipo reportado: {self.type}')
        print('='*50)
        
        # Inicializa os dialogs
        self._setup_dialogs()
        
        # Verifica token
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        
        # Carrega menu de motivos
        self.menu_motive()
    
    def on_leave(self):
        """Limpa recursos ao sair da tela"""
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            print("⏱️ Clock do token cancelado ao sair da tela")
        
        # Fecha menu se estiver aberto
        try:
            if self.menu_motive:
                self.menu_motive.dismiss()
        except:
            pass

    def _setup_dialogs(self):
        """Configura os dialogs de erro"""
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name='ReportChat')
        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível enviar a denúncia. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.step_two)
        )
        
        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')

    # ==================== TOKEN MANAGEMENT ====================
    def verific_token(self, *args):
        """Verifica se o token ainda é válido"""
        if not self.get_parent_window():
            return
            
        print('🔎 Verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_token_success,
            on_failure=self.on_token_failure,
            on_error=self.on_token_failure,
            method="GET"
        )

    def on_token_success(self, req, result):
        """Token válido"""
        print('✅ Token válido, usuário encontrado')

    def on_token_failure(self, req, result):
        """Token inválido, tenta renovar"""
        print('❌ Token inválido, tentando atualizar...', result)
        self.refresh_id_token()

    def refresh_id_token(self):
        """Renova o token de autenticação"""
        refresh_url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        data = "&".join([f"{k}={v}" for k, v in payload.items()])

        UrlRequest(
            refresh_url,
            on_success=self.on_refresh_success,
            on_failure=self.on_refresh_failure,
            on_error=self.on_refresh_failure,
            req_body=data,
            req_headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )

    def on_refresh_success(self, req, result):
        """Token renovado com sucesso"""
        self.token_id = result["id_token"]
        self.refresh_token = result.get("refresh_token", self.refresh_token)
        print("🔄 Token renovado com sucesso")

    def on_refresh_failure(self, req, result):
        """Falha ao renovar token"""
        print("❌ Erro ao renovar token:", result)
        self.show_message('O token não foi renovado', color='#FF0000')
        Clock.schedule_once(
            lambda dt: self.show_message('Refaça login no aplicativo', color='#FF0000'), 
            1
        )

    # ==================== MENU SETUP ====================
    def menu_motive(self, *args):
        """Carrega o menu de motivos pela denúncia"""
        motives = [
            "Assédio moral ou sexual no chat",
            "Discriminação no chat (raça, gênero, idade, etc.)",
            "Ameaças ou intimidação no chat",
            "Linguagem ofensiva ou xingamentos",
            "Envio de conteúdo impróprio",
            "Spam ou envio excessivo de mensagens",
            "Solicitações abusivas no chat",
            "Outro motivo relacionado ao chat"
        ]

        menu_itens = [
            {'text': state, 'on_release': lambda x=state: self.replace_motive(x)}
            for state in motives
        ]

        self.menu_motive = MDDropdownMenu(
            caller=self.ids.motive_card,
            items=menu_itens,
            position='bottom',
            max_height=dp(300),
            size_hint_x=None,
            elevation=8,
            radius=[10, 10, 10, 10],
            pos_hint={'center_x': 0.5},
            border_margin=12,
            ver_growth="down",
        )

    def definir_largura(self, dt):
        """Define largura do menu"""
        if self.menu_motive:
            self.menu_motive.width = Window.width * 0.8

    def open_menu(self, *args):
        """Abre o menu de motivos"""
        if self.menu_motive:
            self.menu_motive.open()
            Clock.schedule_once(self.definir_largura, 0.1)

    def replace_motive(self, text):
        """Substitui o texto do motivo selecionado"""
        self.ids.motive_text.text = text
        self.ids.motive_text.text_color = get_color_from_hex('#FF3F00')
        if self.menu_motive:
            self.menu_motive.dismiss()

    # ==================== EMAIL SENDING ====================
    def enviar_email_thread(self, name, email_recipient, motive):
        """Envia email em thread separada para não travar a UI"""
        def send():
            try:
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                email_remetente = "suportemaodeobra@gmail.com"
                senha = "zrpm knjk mvjp cwlb"
                meses = [
                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
                ]
                now = datetime.now()

                html = f"""
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Denúncia de Chat</title>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 40px 20px;
                            margin: 0 auto;
                            max-width: 60%
                        }}
                        .email-container {{
                            max-width: 600px;
                            margin: 0 auto;
                            background: #ffffff;
                            border-radius: 16px;
                            overflow: hidden;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        }}
                        .email-header {{
                            padding: 40px 30px;
                            text-align: center;
                            color: white;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .icon-circle {{
                            width: 80px;
                            height: 80px;
                            background: rgba(255,255,255,0.2);
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin: 0 auto 20px;
                            backdrop-filter: blur(10px);
                        }}
                        .email-header h1 {{
                            margin: 0;
                            font-size: 28px;
                            font-weight: 700;
                        }}
                        .email-header p {{
                            margin: 10px 0 0;
                            opacity: 0.9;
                            font-size: 16px;
                        }}
                        .email-body {{
                            padding: 40px 30px;
                        }}
                        .email-body h2 {{
                            color: #1F2937;
                            font-size: 20px;
                            margin: 0 0 15px;
                        }}
                        .email-body p {{
                            color: #6B7280;
                            line-height: 1.6;
                            margin: 0 0 15px;
                            font-size: 15px;
                        }}
                        .info-box {{
                            background: #F9FAFB;
                            border-left: 4px solid #667eea;
                            padding: 20px;
                            border-radius: 8px;
                            margin: 25px 0;
                        }}
                        .info-box h3 {{
                            margin: 0 0 10px;
                            color: #1F2937;
                            font-size: 16px;
                        }}
                        .info-row {{
                            display: flex;
                            justify-content: space-between;
                            padding: 8px 0;
                            border-bottom: 1px solid #E5E7EB;
                        }}
                        .info-row:last-child {{
                            border-bottom: none;
                        }}
                        .info-label {{
                            font-weight: 600;
                            color: #4B5563;
                        }}
                        .info-value {{
                            color: #1F2937;
                        }}
                        .status-badge {{
                            display: inline-block;
                            padding: 8px 16px;
                            border-radius: 20px;
                            font-weight: 600;
                            font-size: 13px;
                            margin: 10px 0;
                            background: #DBEAFE;
                            color: #1E40AF;
                        }}
                        .divider {{
                            height: 1px;
                            background: linear-gradient(to right, transparent, #E5E7EB, transparent);
                            margin: 30px 0;
                        }}
                        .email-footer {{
                            background: #F9FAFB;
                            padding: 30px;
                            text-align: center;
                            color: #6B7280;
                            font-size: 14px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="email-header">
                            <div class="icon-circle">
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="40" height="40">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <h1>Denúncia de Chat Recebida</h1>
                            <p>Sua denúncia foi registrada em nosso sistema</p>
                        </div>
                        
                        <div class="email-body">
                            <h2>Olá, {name} 👋</h2>
                            <p>Recebemos sua denúncia relacionada ao chat e queremos agradecer por nos ajudar a manter nossa comunidade segura e respeitosa.</p>
                            
                            <div class="info-box">
                                <h3>💬 Detalhes da Denúncia de Chat</h3>
                                <div class="info-row">
                                    <span class="info-label">Data:</span>
                                    <span class="info-value">{datetime.today().day} de {meses[now.month - 1]}, {datetime.today().year} às {now.strftime('%H:%M')}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Motivo:</span>
                                    <span class="info-value">{motive}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Status:</span>
                                    <span class="status-badge">Recebida</span>
                                </div>
                            </div>

                            <div class="divider"></div>

                            <h3 style="color: #1F2937; font-size: 18px;">📌 O que acontece agora?</h3>
                            
                            <p style="background: #EFF6FF; padding: 15px; border-radius: 8px; border-left: 3px solid #3B82F6;">
                                <strong>⏱️ Tempo estimado:</strong> A análise geralmente leva entre 24-48 horas. Casos complexos podem levar um pouco mais.
                            </p>
                        </div>
                        
                        <div class="email-footer">
                            <p><strong>WorkFlow</strong></p>
                            <p>Este é um email automático. Para dúvidas, responda este email.</p>
                            <p style="margin-top: 20px;">© 2024 WorkFlow. Todos os direitos reservados.</p>
                        </div>
                    </div>
                </body>
                </html>
                """

                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Denúncia de chat em análise"
                msg["From"] = email_remetente
                msg["To"] = email_recipient
                msg.attach(MIMEText(html, "html"))

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(email_remetente, senha)
                    server.send_message(msg)

                print("✅ Email enviado com sucesso!")
                
            except Exception as e:
                print(f"❌ Erro ao enviar email: {e}")
        
        thread = Thread(target=send)
        thread.daemon = True
        thread.start()

    # ==================== REPORT SUBMISSION ====================
    def step_one(self, *args):
        """Verifica se os campos estão preenchidos"""
        # Evita múltiplas submissões
        if self.is_submitting:
            return
        
        motive_text = self.ids.motive_text.text
        description = self.ids.description_field.text

        # Validações
        if motive_text == 'Selecione o motivo':
            self.show_message(
                '⚠️ Selecione o motivo da denúncia',
                color='#FF9800'
            )
            return
        
        if not description or description.strip() == '':
            self.show_message(
                '⚠️ Descreva o que aconteceu',
                color='#FF9800'
            )
            return
        
        print('✅ Campos preenchidos corretamente')
        
        # Mostra loading
        self.is_submitting = True
        self.inf_dialog.open()
        
        # Aguarda um pouco e envia
        Clock.schedule_once(lambda dt: self.step_two(), 0.3)
    
    def step_two(self):
        """Cria a denúncia e coloca no banco de dados"""
        url = f'{self.FIREBASE_URL}/reporteds_chat.json?auth={self.token_id}'
        date = datetime.now().strftime('%d/%m/%y')
        
        data = {
            'data_create': date,
            'denunciator_key': self.local_id,
            'description': self.ids.description_field.text,
            'motive': self.ids.motive_text.text,
            'reported_key': self.key_accused,
            'chat_id': self.chat_id,
            'status': 'pendente',
            'typedenunciator': str(self.perso).lower(),
            'typereported': str(self.type).lower()
        }
        
        UrlRequest(
            url,
            method='POST',
            on_success=self.step_three,
            req_body=json.dumps(data),
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )

    def step_three(self, req, result):
        """A requisição foi completada com sucesso"""
        self.signcontroller.close_all_dialogs()
        self.is_submitting = False
        
        print('='*50)
        print('✅ Denúncia criada:', result)
        print('='*50)
        
        self.show_message('✅ Denúncia criada com sucesso', color='#4CAF50')
        
        # Envia email em thread separada
        self.enviar_email_thread(
            self.name_sender, 
            self.email_sender, 
            self.ids.motive_text.text
        )
        
        # Limpa campos
        self.ids.description_field.text = ''
        self.ids.motive_text.text = 'Selecione o motivo'
        self.ids.motive_text.text_color = 'black'
        
        # Volta ao chat após 1 segundo
        Clock.schedule_once(lambda dt: self.back_chat(), 1)

    # ==================== NAVIGATION ====================
    def back_chat(self, *args):
        """Volta para o chat após carregar dados atualizados"""
        url = f'{self.FIREBASE_URL}/Chats/{self.chat_id}.json?auth={self.token_id}'
        
        UrlRequest(
            url,
            on_success=self.back_chat_two,
            on_error=lambda req, err: self.back_chat_fallback(),
            on_failure=lambda req, err: self.back_chat_fallback()
        )
    
    def back_chat_two(self, req, chat_data):
        """Processa dados do chat e navega de volta"""
        try:
            if not chat_data:
                print("⚠️ Chat não encontrado, voltando sem dados")
                self.back_chat_fallback()
                return
            
            # Extrai informações do chat
            contractor_id = chat_data.get('contractor', '')
            employee_id = chat_data.get('employee', '')
            
            historical_messages = chat_data.get('historical_messages', {})
            historical_contractor = ast.literal_eval(
                historical_messages.get('messages_contractor', '[]')
            )
            historical_employee = ast.literal_eval(
                historical_messages.get('messages_employee', '[]')
            )
            
            message_offline = chat_data.get('message_offline', {})
            msg_off_contractor = ast.literal_eval(
                message_offline.get('contractor', '[]')
            )
            msg_off_employee = ast.literal_eval(
                message_offline.get('employee', '[]')
            )
            
            participants = chat_data.get('participants', {})
            on_contractor = participants.get('contractor', 'offline') == 'online'
            on_employee = participants.get('employee', 'offline') == 'online'

            print(f'👤 Contractor está online? {on_contractor}')
            print(f'👤 Employee está online? {on_employee}')
            
            # Navega para o chat
            app = MDApp.get_running_app()
            screen_manager = app.root
            chat = screen_manager.get_screen('Chat')
            
            # IDs
            chat.chat_id = self.chat_id
            chat.contractor_id = contractor_id
            chat.employee_id = employee_id
            
            # Visual
            chat.perfil = self.avatar
            chat.name_user = self.username
            
            # Auth
            chat.local_id = self.local_id
            chat.refresh_token = self.refresh_token
            chat.api_key = self.api_key
            chat.token_id = self.token_id
            
            # Status online
            chat.on_contractor = on_contractor
            chat.on_employee = on_employee
            chat.perso = self.perso
            
            # Mensagens
            chat.messages_contractor_off = msg_off_contractor
            chat.messages_employee_off = msg_off_employee
            chat.historical_contractor = historical_contractor
            chat.historical_employee = historical_employee
            
            # Navega
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'Chat'
            
        except Exception as e:
            print(f'❌ Erro ao processar dados do chat: {e}')
            self.back_chat_fallback()
    
    def back_chat_fallback(self):
        """Volta ao chat mesmo sem carregar dados atualizados"""
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            chat = screen_manager.get_screen('Chat')
            
            # Passa apenas dados básicos
            chat.chat_id = self.chat_id
            chat.perfil = self.avatar
            chat.name_user = self.username
            chat.token_id = self.token_id
            chat.local_id = self.local_id
            chat.refresh_token = self.refresh_token
            chat.api_key = self.api_key
            chat.perso = self.perso
            
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'Chat'
            
        except Exception as e:
            print(f'❌ Erro crítico ao voltar ao chat: {e}')
            self.dialog_error_unknown.open()

    # ==================== NOTIFICATIONS ====================
    def show_message(self, message, color='#2196F3'):
        """Exibe uma mensagem no snackbar"""
        try:
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
                size_hint_x=0.9,
                theme_bg_color='Custom',
                background_color=get_color_from_hex(color),
                radius=[12, 12, 12, 12],
                duration=3,
            ).open()

        except Exception as e:
            print(f"❌ Erro ao exibir mensagem: {str(e)}")
            
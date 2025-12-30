from kivymd.uix.screen import MDScreen
from kivy.properties import get_color_from_hex, StringProperty, BooleanProperty
from kivy.clock import Clock
import smtplib
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.text import MIMEText
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition
import json
from threading import Thread
from configurations import (DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, 
                           firebase_url, SignController)


class ReportContractor(MDScreen):
    # ==================== PROPERTIES ====================
    FIREBASE_URL = firebase_url()
    
    # Auth & User
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    key_accused = StringProperty()
    perso = StringProperty()
    email_sender = StringProperty()
    name_sender = StringProperty()
    type = StringProperty()
    
    # State
    correct_data = BooleanProperty(False)
    active_minor = BooleanProperty(False)
    active_moderator = BooleanProperty(False)
    active_serious = BooleanProperty(False)
    
    # Internal counters (removido pois não eram usados)
    # cont_minor = 0
    # cont_moderator = 0
    # cont_serious = 0

    def on_kv_post(self, base_widget):
        self.menu_motive = None

    # ==================== LIFECYCLE METHODS ====================
    def on_enter(self):
        """Inicializa a tela quando entra"""
        
        # Inicializa os dialogs
        self._setup_dialogs()
        
        # Verifica token
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        
        # Carrega menu de motivos
        self.menu_motiver()
    
    def on_leave(self):
        """Limpa recursos ao sair da tela"""
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
        
        # Fecha menu se estiver aberto
        try:
            if self.menu_motive:
                self.menu_motive.dismiss()
        except:
            pass

    def _setup_dialogs(self):
        """Configura os dialogs de erro"""
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name='ReportContractor')
        
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

        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_token_success,
            on_failure=self.on_token_failure,
            on_error=self.on_token_failure,
            method="GET"
        )

    def on_token_success(self, req, result):
        """Token válido"""

    def on_token_failure(self, req, result):
        """Token inválido, tenta renovar"""
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

    def on_refresh_failure(self, req, result):
        """Falha ao renovar token"""
        self.show_snackbar('O token não foi renovado', bg_color=(1, 0, 0, 1))
        Clock.schedule_once(
            lambda dt: self.show_snackbar('Refaça login no aplicativo', bg_color=(1, 0, 0, 1)), 
            1
        )

    # ==================== MENU SETUP ====================
    def menu_motiver(self, *args):
        """Carrega o menu de motivos pela denúncia"""
        motives = [
            "Assédio moral ou sexual",
            "Discriminação (raça, gênero, idade, etc)",
            "Não cumprimento de pagamento",
            "Condições de trabalho inadequadas",
            "Exigências abusivas",
            "Comentários inadequados",
            "Outro motivo"
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

    # ==================== SEVERITY CARD TOGGLES ====================
    def trade_color_minor(self, *args):
        """Troca as cores para dar contraste de foco no card leve"""
        if self.active_minor:
            return
        
        # Desativa outros
        if self.active_moderator:
            self.active_moderator = False
            self.ids.moderator.line_color = 'black'
            self.ids.moderator.md_bg_color = 'white'
            self.ids.moderator_title.text_color = 'black'
        
        if self.active_serious:
            self.active_serious = False
            self.ids.serious.line_color = 'black'
            self.ids.serious.md_bg_color = 'white'
            self.ids.serious_title.text_color = 'black'
        
        # Ativa minor
        self.active_minor = True
        self.ids.minor.line_color = get_color_from_hex('#F0A202')
        self.ids.minor.md_bg_color = get_color_from_hex('#FFF9C4')
        self.ids.minor_title.text_color = get_color_from_hex('#F0A202')

    def trade_color_moderator(self, *args):
        """Troca as cores para dar contraste de foco no card moderado"""
        if self.active_moderator:
            return
        
        # Desativa outros
        if self.active_minor:
            self.active_minor = False
            self.ids.minor.line_color = 'black'
            self.ids.minor.md_bg_color = 'white'
            self.ids.minor_title.text_color = 'black'
        
        if self.active_serious:
            self.active_serious = False
            self.ids.serious.line_color = 'black'
            self.ids.serious.md_bg_color = 'white'
            self.ids.serious_title.text_color = 'black'
        
        # Ativa moderator
        self.active_moderator = True
        self.ids.moderator.line_color = get_color_from_hex('#F18805')
        self.ids.moderator.md_bg_color = get_color_from_hex('#FFE0B2')
        self.ids.moderator_title.text_color = get_color_from_hex('#F18805')

    def trade_color_serious(self, *args):
        """Troca as cores para dar contraste de foco no card grave"""
        if self.active_serious:
            return
        
        # Desativa outros
        if self.active_minor:
            self.active_minor = False
            self.ids.minor.line_color = 'black'
            self.ids.minor.md_bg_color = 'white'
            self.ids.minor_title.text_color = 'black'
        
        if self.active_moderator:
            self.active_moderator = False
            self.ids.moderator.line_color = 'black'
            self.ids.moderator.md_bg_color = 'white'
            self.ids.moderator_title.text_color = 'black'
        
        # Ativa serious
        self.active_serious = True
        self.ids.serious.line_color = get_color_from_hex('#FF1B1C')
        self.ids.serious.md_bg_color = get_color_from_hex('#FFCDD2')
        self.ids.serious_title.text_color = get_color_from_hex('#FF1B1C')

    def deactivate_all_cards(self):
        """Desativa todos os cards e redefine as cores padrão"""
        self.active_minor = False
        self.ids.minor.line_color = 'black'
        self.ids.minor.md_bg_color = 'white'
        self.ids.minor_title.text_color = 'black'

        self.active_moderator = False
        self.ids.moderator.line_color = 'black'
        self.ids.moderator.md_bg_color = 'white'
        self.ids.moderator_title.text_color = 'black'

        self.active_serious = False
        self.ids.serious.line_color = 'black'
        self.ids.serious.md_bg_color = 'white'
        self.ids.serious_title.text_color = 'black'

    # ==================== INPUT VALIDATION ====================
    def format_date(self, data, *args):
        """Coloca o texto da data no formato correto"""
        data = str(data).replace('/', '')
        num_caracteres = len(data)

        if num_caracteres == 8:
            day = data[0:2]
            month = data[2:4]
            year = data[4:]
            self.correct_data = True
            self.ids.date.text = f"{day}/{month}/{year}"
            Clock.schedule_once(
                lambda dt: setattr(self.ids.date, 'cursor', (len(self.ids.date.text), 0)), 
                0
            )
        else:
            self.correct_data = False

    def on_text_description(self, instance, value):
        """Limita caracteres e linhas no campo de descrição"""
        max_chars = 240
        max_lines = 6
        
        if len(value) > max_chars:
            instance.text = value[:max_chars]
            return
        
        lines = value.split('\n')
        
        if len(lines) > max_lines:
            instance.text = '\n'.join(lines[:max_lines])
            instance.cursor = (len(instance.text), 0)

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
                    <title>Document</title>
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
                            <h1>Denúncia Recebida com Sucesso</h1>
                            <p>Sua denúncia foi registrada em nosso sistema</p>
                        </div>
                        
                        <div class="email-body">
                            <h2>Olá, {name} 👋</h2>
                            <p>Recebemos sua denúncia e queremos agradecer por nos ajudar a manter nossa comunidade segura e respeitosa.</p>
                            
                            <div class="info-box">
                                <h3>📋 Detalhes da Denúncia</h3>
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
                msg["Subject"] = "Sua denúncia está em análise"
                msg["From"] = email_remetente
                msg["To"] = email_recipient
                msg.attach(MIMEText(html, "html"))

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(email_remetente, senha)
                    server.send_message(msg)
                
            except Exception as e:
                pass
        
        thread = Thread(target=send)
        thread.daemon = True
        thread.start()

    # ==================== REPORT SUBMISSION ====================
    def step_one(self, *args):
        """Verifica se os campos necessários para a denúncia não estão vazios"""
        text_motive = self.ids.motive_text.text
        text_description = self.ids.description_field.text

        # Validações
        if not self.active_minor and not self.active_moderator and not self.active_serious:
            self.show_snackbar(
                "⚠️ Selecione a gravidade da denúncia", 
                bg_color=(0.96, 0.49, 0.00, 1)
            )
            return
        
        if text_motive == 'Selecione o motivo':
            self.show_snackbar(
                "⚠️ Selecione o motivo da denúncia", 
                bg_color=(0.96, 0.49, 0.00, 1)
            )
            return
    
        if not self.correct_data:
            self.show_snackbar(
                "⚠️ Preencha a data corretamente (DD/MM/AAAA)", 
                bg_color=(0.96, 0.49, 0.00, 1)
            )
            return
        
        if not text_description:
            self.show_snackbar(
                "⚠️ Descreva o que aconteceu", 
                bg_color=(0.96, 0.49, 0.00, 1)
            )
            return
        
        # Mostra loading
        self.inf_dialog.open()
        
        # Aguarda um pouco e envia
        Clock.schedule_once(lambda dt: self.step_two(), 0.3)

    def step_two(self):
        """Cria a denúncia e coloca no banco de dados"""
        url = f'{self.FIREBASE_URL}/reports.json?auth={self.token_id}'
        date = datetime.now().strftime('%d/%m/%y')
        
        # Determina a gravidade
        severity = 'minor' if self.active_minor else 'moderator' if self.active_moderator else 'serious'
        
        data = {
            'data_create': date,
            'denunciator_key': self.local_id,
            'description': self.ids.description_field.text,
            'motive': self.ids.motive_text.text,
            'data_occurred': self.ids.date.text,
            'reported_key': self.key_accused,
            'status': 'pendente',
            'severity': severity,
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
        """Denúncia criada com sucesso, volta à tela inicial"""
        self.signcontroller.close_all_dialogs()
        
        # Envia email em thread separada
        self.enviar_email_thread(
            self.name_sender, 
            self.email_sender, 
            self.ids.motive_text.text
        )
        
        # Limpa os campos
        self.ids.description_field.text = ''
        self.deactivate_all_cards()
        self.ids.date.text = ''
        self.ids.motive_text.text = 'Selecione o motivo'
        self.ids.motive_text.text_color = 'black'
        self.correct_data = False
        
        # Fecha menu se estiver aberto
        try:
            if self.menu_motive:
                self.menu_motive.dismiss()
        except:
            pass
        
        # Navega para tela de confirmação
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            created = screenmanager.get_screen('ReportedCreated')
            
            created.token_id = self.token_id
            created.local_id = self.local_id
            created.refresh_token = self.refresh_token
            created.api_key = self.api_key
            created.perso = self.perso
            
            screenmanager.transition = SlideTransition(direction='right')
            screenmanager.current = 'ReportedCreated'
            
        except Exception as e:
            self.dialog_error_unknown.open()

    # ==================== NAVIGATION ====================
    def back_screen(self, *args):
        """Volta para a tela anterior"""
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            home = screenmanager.get_screen('IdentifyPerfil')
            
            home.token_id = self.token_id
            home.perso = self.perso
            home.local_id = self.local_id
            home.refresh_token = self.refresh_token
            home.api_key = self.api_key
            
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'IdentifyPerfil'
            
        except Exception as e:
            self.dialog_error_unknown.open()

    # ==================== NOTIFICATIONS ====================
    def show_snackbar(self, message, bg_color=(0.13, 0.59, 0.95, 1)):
        """Exibe snackbar com mensagem customizada"""
        snackbar = MDSnackbar(
            MDSnackbarText(
                text=message,
                theme_text_color='Custom',
                text_color='white',
                bold=True,
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            background_color=bg_color,
            radius=[12, 12, 12, 12],
            duration=3,
        )
        snackbar.open()
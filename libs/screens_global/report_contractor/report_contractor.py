from kivymd.uix.screen import MDScreen
from kivy.properties import get_color_from_hex
from kivy.clock import Clock
import smtplib
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.text import MIMEText
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer, MDDialogContentContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.divider import MDDivider
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition
import json
from kivy.core.clipboard import Clipboard
from threading import Thread


class ReportContractor(MDScreen):
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    key_accused = StringProperty()
    perso = StringProperty()
    email_sender = StringProperty()
    name_sender = StringProperty()
    type = StringProperty()
    cont_minor = 0
    cont_moderator = 0
    cont_serious = 0
    correct_data = False

    active_minor = False
    active_moderator = False
    active_serious = False

    def on_enter(self):
        """carrega os dados necessarios da tela"""
        self.menu_motiver()
    
    def show_snackbar(self, message, bg_color=(0.13, 0.59, 0.95, 1)):
        """Exibe snackbar com mensagem customizada"""
        snackbar = MDSnackbar(
            MDSnackbarText(text=message),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            background_color=bg_color,
        )
        snackbar.open()
    
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

    def copy_email(self):
        """Copia o email para a área de transferência"""
        Clipboard.copy("suporteobra@gmail.com")
        self.show_snackbar("Email copiado para a área de transferência!")

    def retry_connection(self):
        """Fecha o dialog e tenta novamente a requisição"""
        self.error_dialog.dismiss()
        self.step_one()

    def menu_motiver(self, *args):
        """Carregando o menu de motivos pela denuncia"""
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
            elevation=8,
            radius=[10, 10, 10, 10],
            pos_hint={'center_x': 0.5},
            border_margin=12,
            ver_growth="down",
        )

    def definir_largura(self, dt):
        self.menu_motive.width = Window.width * 0.8

    def open_menu(self, *args):
        self.menu_motive.open()
        Clock.schedule_once(self.definir_largura, 0.1)

    def replace_motive(self, text):
        self.ids.motive_text.text = text
        self.ids.motive_text.text_color = get_color_from_hex('#FF3F00')
        self.menu_motive.dismiss()

    def trade_color_minor(self, *args):
        """Troca as cores para dar contraste de foco no card leve"""
        if self.active_minor:
            return
        
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
        
        self.active_minor = True
        self.ids.minor.line_color = get_color_from_hex('#F0A202')
        self.ids.minor.md_bg_color = get_color_from_hex('#FFF9C4')
        self.ids.minor_title.text_color = get_color_from_hex('#F0A202')

    def trade_color_moderator(self, *args):
        """Troca as cores para dar contraste de foco no card moderado"""
        if self.active_moderator:
            return
        
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
        
        self.active_moderator = True
        self.ids.moderator.line_color = get_color_from_hex('#F18805')
        self.ids.moderator.md_bg_color = get_color_from_hex('#FFE0B2')
        self.ids.moderator_title.text_color = get_color_from_hex('#F18805')

    def trade_color_serious(self, *args):
        """Troca as cores para dar contraste de foco no card grave"""
        if self.active_serious:
            return
        
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

    def format_date(self, data, *args):
        """Colocando o texto da data no formato correto"""
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
                        .selector {{
                            max-width: 600px;
                            margin: 0 auto 30px;
                            background: white;
                            border-radius: 16px;
                            padding: 20px;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        }}
                        .selector h2 {{
                            margin: 0 0 15px;
                            color: #1F2937;
                            font-size: 18px;
                        }}
                        .btn-group {{
                            display: flex;
                            gap: 10px;
                            flex-wrap: wrap;
                        }}
                        .btn-select {{
                            flex: 1;
                            min-width: 150px;
                            padding: 12px 20px;
                            border: 2px solid #E5E7EB;
                            background: white;
                            border-radius: 12px;
                            cursor: pointer;
                            font-weight: 600;
                            transition: all 0.3s;
                            font-size: 14px;
                        }}
                        .btn-select:hover {{
                            transform: translateY(-2px);
                            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                        }}
                        .btn-select.active {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border-color: #667eea;
                        }}
                        .email-container {{
                            max-width: 600px;
                            margin: 0 auto;
                            background: #ffffff;
                            border-radius: 16px;
                            overflow: hidden;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        }}
                        .email-template {{
                            display: block;
                            background-color: white;
                        }}
                        .email-template.active {{
                            display: block;
                        }}
                        .email-header {{
                            padding: 40px 30px;
                            text-align: center;
                            color: white;
                        }}
                        .header-received {{
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
                        .icon-circle svg {{
                            width: 40px;
                            height: 40px;
                            stroke: white;
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
                        }}
                        .status-received {{
                            background: #DBEAFE;
                            color: #1E40AF;
                        }}
                        .divider {{
                            height: 1px;
                            background: linear-gradient(to right, transparent, #E5E7EB, transparent);
                            margin: 30px 0;
                        }}
                    </style>
                </head>
                <body>
                        <div class="email-container">
                        <div class="email-template active" id="email1">
                            <div class="email-header header-received">
                                <div class="icon-circle">
                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                                        <span class="info-value"> {datetime.today().day} de {meses[now.month - 1]}, {datetime.today().year} às {now.strftime('%H:%M')}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Motivo:</span>
                                        <span class="info-value"> {motive}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Status:</span>
                                        <span class="status-badge status-received">Recebida</span>
                                    </div>
                                </div>

                                <div class="divider"></div>

                                <h3 style="color: #1F2937; font-size: 18px;">📌 O que acontece agora?</h3>
                                
                                <div class="timeline">
                                    <div class="timeline-item">
                                        <div class="timeline-dot"></div>
                                        <div class="timeline-content">
                                            <h4>✅ Denúncia registrada</h4>
                                            <p>Sua denúncia foi recebida com sucesso</p>
                                        </div>
                                    </div>
                                    <div class="timeline-item">
                                        <div class="timeline-dot" style="background: #E5E7EB;"></div>
                                        <div class="timeline-content">
                                            <h4>🔍 Análise da equipe</h4>
                                            <p>Nossa equipe irá analisar cuidadosamente o caso</p>
                                        </div>
                                    </div>
                                    <div class="timeline-item">
                                        <div class="timeline-dot" style="background: #E5E7EB;"></div>
                                        <div class="timeline-content">
                                            <h4>⚖️ Decisão e ação</h4>
                                            <p>Tomaremos as medidas cabíveis e você será notificado</p>
                                        </div>
                                    </div>
                                </div>

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

                print("Email enviado com sucesso!")
                
            except Exception as e:
                print(f"Erro ao enviar email: {e}")
        
        thread = Thread(target=send)
        thread.daemon = True
        thread.start()

    def step_one(self, *args):
        """Verificar se os campos necessarios para a denuncia não estão vazios"""
        text_motive = self.ids.motive_text.text
        text_description = self.ids.description_field.text

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
        
        # Mostra snackbar de carregamento
        self.show_snackbar(
            "✨ Estamos processando sua denúncia...",
            bg_color=(0.29, 0.56, 0.89, 1)
        )
        
        self.step_two()

    def step_two(self):
        """Pegar o local id do usuario e cria a denuncia e coloca no banco de dados"""
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/reports.json?auth={self.token_id}'
        date = datetime.now().strftime('%d/%m/%y')
        data = {
            'data_create': date,
            'denunciator_key': self.local_id,
            'description': self.ids.description_field.text,
            'motive': self.ids.motive_text.text,
            'data_occurred': self.ids.date.text,
            'reported_key': self.key_accused,
            'status': 'pendente',
            'typedenunciator': str(self.perso).lower(),
            'typereported': str(self.type).lower()
        }
        UrlRequest(
            url,
            method='POST',
            on_success=self.step_three,
            req_body=json.dumps(data),
            on_error=self.error,
            on_failure=self.error
        )

    def step_three(self, req, result):
        """Denuncia criada com sucesso voltar a tela inicial"""
        print('='*50)
        print('Jason da denúncia criada: ', result)
        
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
        
        try:
            self.menu_motive.dismiss()
        except:
            pass
        
        # Navega para tela de confirmação
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
        print('='*50)
    
    def error(self, req, erro):
        """Exibe uma mensagem de erro na tela"""
        print('='*50)
        print('Ocorreu um erro inesperado: ', erro)
        self.show_error_dialog()
        print('='*50)
    
    def back_screen(self, *args):
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
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from threading import Thread
import smtplib
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.text import MIMEText
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer, MDDialogContentContainer
from kivymd.uix.label import MDLabel
import logging
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window
import ast
import smtplib
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.text import MIMEText
from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition
from kivy.utils import get_color_from_hex
import json
from kivy.properties import StringProperty


class ReportChat(MDScreen):
    avatar = StringProperty()
    username = StringProperty()
    name_sender = StringProperty()
    email_sender = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    api_key = StringProperty()
    refresh_token = StringProperty()
    chat_id = StringProperty()
    perso = StringProperty()
    type = StringProperty()
    key_accused = StringProperty()
    
    def on_enter(self):
        """carrega os dados necessarios da tela"""
        if self.perso == 'Employee':
            self.type = 'contractor'

        else:
            self.type = 'employee'

        print('='*50)
        print(f'{self.token_id}')
        print('='*50)
        self.menu_motive()

    def menu_motive(self, *args):
        """Carregando o menu de motivos pela denuncia"""
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

        menu_itens = []
        position = 0
        for state in motives:
            position += 1
            row = {'text': state, 'on_release': lambda x=state: self.replace_motive(x)}
            menu_itens.append(row)

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

    # manipulando dados -------------------------------------------------------------------

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
        """Verifica se os campos estão preenchidos """
        motive_text = self.ids.motive_text.text
        description = self.ids.description_field.text

        if motive_text == 'Selecione o motivo':
            return
        
        elif not description:
            return
        
        print('Seguinte meu nobre os campos estão preenchidos')
        self.step_two()
    
    def step_two(self):
        """ Pegar o local id do usuario e cria a denuncia e coloca no banco de dados"""
        import datetime
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/reporteds_chat.json?auth={self.token_id}'
        date = datetime.datetime.now().strftime('%d/%m/%y')
        data = {
            'data_create': f'{date}',
            'denunciator_key': f'{self.local_id}',
            'description': f'{self.ids.description_field.text}',
            'motive': f'{self.ids.motive_text.text}',
            'reported_key': f'{self.key_accused}',
            'status': 'pendente',
            'typedenunciator': f'{str(self.perso).lower()}',
            'typereported': f'{str(self.type).lower()}'
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
        """A requisição foi completada"""
        print('Requisição completa: ', result)
        self.show_message('Denúncia criada com sucesso')
        self.enviar_email_thread(
            self.name_sender, 
            self.email_sender, 
            self.ids.motive_text.text
        )
        self.back_chat()
    
    def error(self, req, error):
        """Quando a requisição dar um erro inesperado"""
        print('Deu o seguinte erro: ', error)
        self.show_error_dialog()

    def back_chat(self, *args):
        # só preciso carregar o historical_message o resto não precisa rsrsrs
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.back_chat_two
        )
    
    def back_chat_two(self, req, chat_data):
        historical = []
        msg_off_contractor = []
        msg_off_employee = []
        on_contractor = ''
        on_employee = ''
        contractor_id = ''
        employee_id = ''
        chat_id = ''
        info = chat_data
        contractor_id = info['contractor']
        employee_id = info['employee']
        historical_contractor = ast.literal_eval(info['historical_messages']['messages_contractor'])
        historical_employee = ast.literal_eval(info['historical_messages']['messages_employee'])
        msg_off_contractor = ast.literal_eval(info['message_offline']['contractor'])
        msg_off_employee = ast.literal_eval(info['message_offline']['employee'])
        on_contractor = info['participants']['contractor']
        on_employee = info['participants']['employee']

        print('Contractor está online? ', on_contractor)
        app = MDApp.get_running_app()
        screen_manager = app.root
        chat = screen_manager.get_screen('Chat')
        chat.chat_id = self.chat_id
        chat.contractor_id = contractor_id
        chat.employee_id = employee_id
        
        # parte visual ------------------
        chat.perfil = self.avatar
        chat.name_user = self.username
        
        # parte dos tokens --------------
        chat.local_id = self.local_id
        chat.refresh_token = self.refresh_token
        chat.api_key = self.api_key
        chat.token_id = self.token_id
        
        # Quem está online ou offline
        if on_contractor == 'online':
            on_contractor = True
        else:
            on_contractor = False
        
        if on_employee == 'online':
            on_employee = True
        else:
            on_employee = False

        chat.on_contractor = on_contractor
        chat.on_employee = on_employee
        chat.perso = self.perso
        
        # fluxo de mensagens
        chat.messages_contractor_off = msg_off_contractor
        chat.messages_employee_off = msg_off_employee
        
        chat.historical_contractor = historical_contractor
        chat.historical_employee = historical_employee
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'Chat'

    def show_message(self, message, color='#2196F3'):
        """
        Exibe uma mensagem no snackbar.

        Args:
            message (str): Mensagem a ser exibida.
            color (str, optional): Cor de fundo do snackbar. Padrão é '#2196F3'.
        """
        try:
            logging.info(f"Mensagem: {message}")

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

        except Exception as e:
            logging.error(f"Erro ao exibir mensagem: {str(e)}")
            print(f"Erro ao exibir mensagem: {str(e)}")

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
        """Fecha o dialog e tenta novamente a requisição"""
        self.error_dialog.dismiss()
        self.step_one()

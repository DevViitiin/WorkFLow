from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, get_color_from_hex, BooleanProperty, NumericProperty
from kivymd.uix.button import MDButton, MDButtonText
import logging
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
import ast
from kivy.network.urlrequest import UrlRequest


class PerfilEmployeeGlobal(MDScreen):
    # firebase ------------------------
    api_key = StringProperty()
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    chat_id = StringProperty()

    # tela ----------------------------
    avatar = StringProperty()
    city = StringProperty()
    state = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    FIREBASE_URL = 'https://obra-7ebd9-default-rtdb.firebaseio.com'
    
    def on_enter(self, *args):
        # Carregar habilidades
        self._load_skills()

    def _load_skills(self):
        """
        Método interno para carregar as habilidades do funcionário.

        Tenta converter a string de habilidades em uma lista e chama o método
        para adicionar as habilidades à UI.
        """
        try:
            skills = eval(self.skills) if self.skills else []
        except (SyntaxError, NameError, TypeError) as e:
            logging.warning(f"Erro ao interpretar habilidades: {str(e)}")
            skills = []

        try:
            if hasattr(self.ids, 'main_scroll'):
                self.ids.main_scroll.clear_widgets()
                self.skill_add = 0
                self.add_skills(skills)
            else:
                logging.error("Container de habilidades não encontrado")
        except Exception as e:
            logging.error(f"Erro ao adicionar habilidades: {str(e)}")

    def add_skills(self, skills):
        """
        Adiciona as habilidades do funcionário na tela.

        Args:
            skills (list): Lista de habilidades do funcionário.
        """
        try:
            if not hasattr(self.ids, 'main_scroll'):
                logging.error("Container de habilidades não encontrado")
                return

            self.ids.main_scroll.clear_widgets()

            if skills:
                for skill in skills:
                    try:
                        button = MDButton(
                            MDButtonText(
                                text=f'{skill}',
                                theme_text_color='Custom',
                                text_color='white',
                                bold=True
                            ),
                            theme_bg_color='Custom',
                            md_bg_color=get_color_from_hex('#0047AB')
                        )
                        self.ids.main_scroll.add_widget(button)
                    except Exception as e:
                        logging.error(f"Erro ao criar botão para habilidade '{skill}': {str(e)}")
            else:
                button = MDButton(
                    MDButtonText(
                        text='Nenhuma habilidade adicionada',
                        theme_text_color='Custom',
                        text_color='white',
                        bold=True
                    ),
                    theme_bg_color='Custom',
                    md_bg_color=get_color_from_hex('#0047AB')
                )
                self.ids.main_scroll.add_widget(button)
        except Exception as e:
            logging.error(f"Erro ao adicionar habilidades: {str(e)}")

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
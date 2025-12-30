from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.network.urlrequest import UrlRequest
import ast
from kivy.uix.screenmanager import SlideTransition 
from kivymd.app import MDApp
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController


class PerfilContractorGlobal(MDScreen):
    token_id = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    local_id = StringProperty()
    chat_id = StringProperty()
    username = StringProperty('Thorfin')
    avatar = StringProperty('https://res.cloudinary.com/dsmgwupky/image/upload/v1760446115/Thorfin.jpg')
    company = StringProperty('NoEnemies')
    city = StringProperty('Santana do Ipanema')
    state = StringProperty('Alagoas')
    telefone = StringProperty('(62) 99356-0986')
    email = StringProperty('thorfin@gmail.com')
    perso = StringProperty()
    function = StringProperty('Engenheiro Ambiental')

    def on_enter(self, *args):
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)
        
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível se conectar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.back_chat)
        )
        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')

    def back_chat(self, *args):
        # só preciso carregar o historical_message o resto não precisa rsrsrs
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Chats/{self.chat_id}.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.back_chat_two,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )
    
    def back_chat_two(self, req, chat_data):
        try:
            self.signcontroller.close_all_dialogs()
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
        except:
            self.dialog_error_unknown.open()

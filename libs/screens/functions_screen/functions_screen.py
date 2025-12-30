import json
from functools import partial
from kivy.clock import Clock
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.properties import StringProperty, BooleanProperty, get_color_from_hex
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItemTertiaryText, MDListItemSupportingText, MDListItemHeadlineText, \
    MDListItemLeadingIcon, MDListItem, MDListItemTrailingIcon, MDListItemTrailingCheckbox
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest


class FunctionsScreen(MDScreen):
    local_id = StringProperty()
    token_id = StringProperty()
    api_key = StringProperty()
    contractor = StringProperty()
    email = StringProperty()
    can_add = BooleanProperty()
    telephone = StringProperty()
    refresh_token = StringProperty()
    company = StringProperty()
    infor = False
    key_contractor = StringProperty()
    FIREBASE_URL = firebase_url()
    key = ''
    value = ''
    local = ''
    occupation = 'Pedreiro'
    oc = ''
    salary = ''

    def on_enter(self, *args):
        self.verific_token()
        # ====================== popups =============================
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)  
        self.dialog_not_net = DialogNoNet(
            subtitle='Não foi possível apagar a função. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.delete_function)
        )
        self.dialog_not_net_database = DialogNoNet(
            subtitle='Não foi carregar funções. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_handle(self.upload_functions)
        )
        self.dialog_error_unknown = DialogErrorUnknow(
            screen=f'{self.name}'
        )
        self.event_token = Clock.schedule_interval(self.verific_token, 300)
        def on_success(req, result):
            pass

        def on_error(req, error):
            pass

        def on_failure(req, result):
            pass

        self.verific_token()
        self.ids.main_scroll.clear_widgets()
        self.upload_functions()

    def upload_functions(self):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions.json'
        query_params = f"?orderBy=%22IdLocal%22&equalTo=%22{self.local_id}%22&auth={self.token_id}"
        UrlRequest(
            url + query_params,
            method='GET',
            on_success=self.functions,
            on_error=self.signcontroller.on_error,
            on_failure=self.signcontroller.on_failure
        )

    def on_leave(self, *args):
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
         
    def verific_token(self, *args):
        if not self.get_parent_window():
            return
        
        UrlRequest(
            f"{self.FIREBASE_URL}/Users/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_success,
            on_failure=self.on_failure,
            on_error=self.on_failure,
            method="GET"
        )

    def on_failure(self, req, result):
        self.refresh_id_token()  # chama atualização

    def on_success(self, req, result):
        pass


    # --- ATUALIZAÇÃO DO TOKEN ---
    def refresh_id_token(self):
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
        self.token_id = result["id_token"]
        self.refresh_token = result["refresh_token"]  # Firebase pode mandar de novo

    def on_refresh_failure(self, req, result):
        self.show_error('O token não foi renovado')
        #Clock.schedule_once(self.show_error('Refaça login no aplicativo'), 1.5)

    def show_message(self, message, color='#2196F3'):
        """
        Exibe uma mensagem na interface através de um snackbar.

        Args:
            message: A mensagem a ser exibida
            color: A cor de fundo do snackbar
        """
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
            size_hint_x=0.94,
            theme_bg_color='Custom',
            background_color=get_color_from_hex(color),
            duration=3  # Duração da exibição do snackbar em segundos
        ).open()

    def show_error(self, error_message):
        """
        Exibe uma mensagem de erro através de um snackbar vermelho.

        Args:
            error_message: A mensagem de erro a ser exibida
        """
        self.show_message(error_message, color='#FF0000')

    def functions(self, req, result):
        try:
            for x, y in result.items():
                for item, value in y.items():
                    if item == 'Contractor':
                        if y['IdLocal'] == self.local_id:
                            if 'label' in self.ids:
                                self.remove_widget(self.ids.label)
                            check = MDListItemTrailingCheckbox(
                                    )

                            self.ids[y['occupation']] = check
                            check.icon = 'trash-can-outline'
                            check.bind(on_release=partial(self.click, y['occupation'], x))
                            if y['Option Payment'] == 'Negociar':
                                list_item = MDListItem(
                                    MDListItemLeadingIcon(
                                        icon="account-tie"
                                    ),
                                    MDListItemHeadlineText(
                                        text=f"{y['occupation']}",
                                        bold=True,
                                        font_style='Headline',
                                        role='small'
                                    ),
                                    MDListItemSupportingText(
                                        text=f"{y['Option Payment']}"
                                    ),
                                    MDListItemTertiaryText(
                                        text=f"{y['State']}-{y['City']}"
                                    )
                                )
                                self.ids.main_scroll.add_widget(list_item)
                            else:
                                list_item = MDListItem(
                                    MDListItemLeadingIcon(
                                        icon="account-tie"
                                    ),
                                    MDListItemHeadlineText(
                                        text=f"{y['occupation']}",
                                        bold=True,
                                        font_style='Title',
                                        role='medium'
                                    ),
                                    MDListItemSupportingText(
                                        text=f"{y['Option Payment']}: R${y['Salary']}",
                                        font_style='Label',
                                        role='large',
                                        theme_text_color='Custom',
                                        text_color='black'
                                    ),
                                    MDListItemTertiaryText(
                                        text=f"{y['State']} - {y['City']}",
                                        font_style='Label',
                                        role='large',
                                        theme_text_color='Custom',
                                        text_color='black'
                                    ),
                                    check
                                )
                                self.ids.main_scroll.add_widget(list_item)

            if self.ids.main_scroll.children:
                pass
            else:
                self.show_no_requests_found()
        except:
            self.show_no_requests_found()
        
        finally:
            self.signcontroller.close_all_dialogs()


    def click(self, occupation, key, *args):
        self.ids[f'{occupation}'].icon = 'trash-can-outline'
        self.oc = self.ids[f'{occupation}']
        self.delete_function(key)

    def delete_function(self, key):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{key}/.json?auth={self.token_id}'
        def erro(req, result):
            pass

        UrlRequest(
            f'{url}',
            method='DELETE',
            on_success=self.final_delete,
            on_error=self.signcontroller.handle_signup_error,
            on_failure=self.signcontroller.handle_signup_failure
        )
    
    def final_delete(self, instance, result):
        self.ids.main_scroll.clear_widgets()
        self.upload_functions()

    def show_no_requests_found(self):
        """Common method to display the 'no requests found' message and image"""
        self.ids.main_scroll.clear_widgets()

        # Create a container for centered content
        container = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height="300dp",
            pos_hint={'center_x': 0.5}
        )

        # Add image
        image = AsyncImage(
            source='https://res.cloudinary.com/dsmgwupky/image/upload/v1746223701/aguiav2_pnq6bl.png',
            size_hint=(0.65, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        container.add_widget(image)
        self.ids.main_scroll.add_widget(container)

    def perfil(self, *args):
        try:
            app = MDApp.get_running_app()
            screen_manager = app.root
            functions = screen_manager.get_screen('Perfil')
            functions.token_id = self.token_id
            functions.local_id = self.local_id
            functions.refresh_token = self.refresh_token
            functions.api_key = self.api_key
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'Perfil'
        except:
            Clock.schedule_once(lambda dt: self.dialog_error_unknown.open(), 1.5)

    def page_functions(self, *args):
        try:
            self.manager.transition = SlideTransition(direction='left')
            step = self.manager.get_screen('Function')
            step.contractor = self.contractor
            step.email = self.email
            step.api_key = self.api_key
            step.can_add = self.can_add
            step.telephone = self.telephone
            step.company = self.company
            step.token_id = self.token_id
            step.local_id = self.local_id
            step.refresh_token = self.refresh_token
            step.key = self.key_contractor
            self.manager.current = 'Function'
        except:
            Clock.schedule_once(lambda dt: self.dialog_error_unknown.open(), 1.5)

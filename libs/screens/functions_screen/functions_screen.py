import json
from functools import partial

from kivy.properties import StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItemTertiaryText, MDListItemSupportingText, MDListItemHeadlineText, \
    MDListItemLeadingIcon, MDListItem, MDListItemTrailingIcon, MDListItemTrailingCheckbox
from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest


class FunctionsScreen(MDScreen):
    local_id = StringProperty()
    token_id = StringProperty()
    contractor = StringProperty()
    email = StringProperty()
    telephone = StringProperty()
    refresh_token = StringProperty()
    company = StringProperty()
    infor = False
    key_contractor = StringProperty()
    key = ''
    value = ''
    local = ''
    occupation = 'Pedreiro'
    oc = ''
    salary = ''

    def on_enter(self, *args):
        print('Token de refresh: ', self.refresh_token)
        def on_success(req, result):
            print("Dados filtrados:", result)

        def on_error(req, error):
            print("Erro:", error)

        def on_failure(req, result):
            print("Falha:", result)

        self.ids.main_scroll.clear_widgets()
        params = f'orderBy="IdLocal"&equalTo="{self.local_id}"'
        url = f"https://obra-7ebd9-default-rtdb.firebaseio.com/Functions.json?{params}"
        UrlRequest(url, self.functions, on_failure=on_failure, on_error=on_error)

    def functions(self, req, result):
        print('Resultados encontrados: ', result)
        try:
            for x, y in result.items():
                for item, value in y.items():
                    if item == 'Contractor':
                        if y['Contractor'] == self.contractor:
                            if 'label' in self.ids:
                                self.remove_widget(self.ids.label)
                            check = MDListItemTrailingCheckbox(
                                    )

                            print(x)
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
                print("O MDBoxLayout tem widgets dentro!")
            else:
                self.show_no_requests_found()
        except:
            self.show_no_requests_found()


    def click(self, occupation, key, *args):
        self.ids[f'{occupation}'].icon = 'trash-can-outline'
        self.oc = self.ids[f'{occupation}']
        self.delete_function(key)

    def delete_function(self, key):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Functions/{key}/.json?auth={self.token_id}'
        def erro(req, result):
            print(result)

        UrlRequest(
            f'{url}',
            method='DELETE',
            on_success=self.final_delete,
            on_error=erro,
            on_failure=erro
        )

    def final_delete(self, instance, result):
        self.ids.main_scroll.clear_widgets()
        self.on_enter()

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

    def perfil(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'Perfil'

    def page_functions(self):
        self.manager.transition = SlideTransition(direction='left')
        step = self.manager.get_screen('Function')
        step.contractor = self.contractor
        step.email = self.email
        step.telephone = self.telephone
        step.company = self.company
        step.token_id = self.token_id
        step.local_id = self.local_id
        step.refresh_token = self.refresh_token
        step.key = self.key_contractor
        self.manager.current = 'Function'

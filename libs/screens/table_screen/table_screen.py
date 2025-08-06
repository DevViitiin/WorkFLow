from kivy.properties import StringProperty, BooleanProperty, partial
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.list import MDListItem, MDListItemLeadingAvatar, MDListItemHeadlineText, MDListItemSupportingText, \
    MDListItemTertiaryText, MDListItemTrailingCheckbox

from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest


class TableScreen(MDScreen):
    cont = 0
    username = StringProperty()
    key = StringProperty()
    current_nav_state = StringProperty('table')
    adicionado = 0
    table = BooleanProperty()
    permission = True

    def on_enter(self):
        print(f'Nome passado {self.username} e a key passada {self.key}')
        url = 'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios'
        self.adicionado += 1
        if self.adicionado == 1:
            UrlRequest(
                f'{url}/.json',
                method='GET',
                on_success=self.load_employees
            )
        else:
            self.ids.main_scroll.clear_widgets()
            self.cont = 0
            UrlRequest(
                f'{url}/.json',
                method='GET',
                on_success=self.load_employees
            )

    def load_employees(self, req, result):
        # Definindo o mdlist -------------------------------

        for employees, info in result.items():
            if info['contractor'] == self.username:
                print(employees, info)
                self.cont += 1
                if 'label' in self.ids:
                    self.remove_widget(self.ids.label)

                # Capture o valor atual de employees em uma variável local para a função lambda
                employee_key = employees  # Criar uma variável local com o valor atual

                # Crie o checkbox com um evento de clique que impede a propagação
                check = MDListItemTrailingCheckbox()
                check.icon = 'trash-can-outline'
                self.ids[info['Name']] = check

                lista = MDListItem(
                    MDListItemLeadingAvatar(
                        source=info['avatar']
                    ),
                    MDListItemHeadlineText(
                        text=info['Name']
                    ),
                    MDListItemSupportingText(
                        text=info['function']
                    ),
                    MDListItemTertiaryText(
                        text=info['method_salary']
                    ),
                )

                inf = info
                # Use employee_key (variável local) em vez de employees (variável do loop)
                lista.bind(
                    on_release=lambda instance, info=inf, key=employee_key: self.show_employee_details(info, key))
                self.ids.main_scroll.add_widget(lista)
        self.ids.counter.text = f'{self.cont} funcionarios contratados'

    def handle_checkbox_click(self, instance, name, key, *args):
        # Impede a propagação do evento para o MDListItem
        instance.stop_propagation = True
        # Chama a função de exclusão
        self.click(name, key)

        return True

    def click(self, name, key, *args):
        self.ids[f'{name}'].icon = 'trash-can-outline'
        self.oc = self.ids[f'{name}']
        self.delete_function(key)
        self.permission = False


    def delete_function(self, key):
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{key}'  # Corrigido a URL
        UrlRequest(
            f'{url}/.json',
            method='DELETE',
            on_success=self.final_delete
        )

    def final_delete(self, instance, result):
        self.ids.main_scroll.clear_widgets()
        self.permission = True
        self.on_enter()

    def show_employee_details(self, info, key):
        # Obtendo o gerenciador de telas
        print('Informações do cara: ', info)
        if self.permission:
            detail_screen = self.manager.get_screen("Evaluation")
            detail_screen.employee_name = info['Name']
            detail_screen.employee_function = info['function']
            detail_screen.avatar = info['avatar']
            detail_screen.salary = info['salary']
            detail_screen.method_salary = info['method_salary']
            try:
                detail_screen.punctuality = info['punctuality']
            except:
                detail_screen.punctuality = '0'
            detail_screen.coexistence = info['coextistence']
            detail_screen.efficiency = info['effiency']
            detail_screen.days_work = info['days_work']
            detail_screen.scale = info['scale']
            detail_screen.contractor = info['contractor']
            detail_screen.confirm_payments = info['confirm_payments']
            detail_screen.request_payment = info['request_payment']
            detail_screen.work_days_week1 = info['work_days_week1']
            detail_screen.work_days_week2 = info['work_days_week2']
            detail_screen.work_days_week3 = info['work_days_week3']
            detail_screen.work_days_week4 = info['work_days_week4']
            detail_screen.week_1 = info['week_1']
            detail_screen.week_2 = info['week_2']
            detail_screen.week_3 = info['week_3']
            detail_screen.week_4 = info['week_4']
            detail_screen.day = info['day']
            detail_screen.ultimate = info['ultimate']
            detail_screen.valleys = info['valleys']
            detail_screen.tot = info['tot']
            detail_screen.key = key
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = "Evaluation"

    # chama a tela de cadastrar funcionarios
    def add_screen(self):
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        perfil = screen_manager.get_screen('Add')
        perfil.contractor = self.username
        self.manager.current = 'Add'

    def search(self):
        app = MDApp.get_running_app()
        print('Passando essa key pra tela de search:', self.key)
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('VacancyContractor')
        bricklayer.key_contractor = self.key
        bricklayer.username = self.username
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = True
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'search'
        screen_manager.current = 'VacancyContractor'

    def request(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        screen_manager.transition = SlideTransition(direction='right')
        bricklayer = screen_manager.get_screen('RequestContractor')
        bricklayer.key = self.key
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = False
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = True
        bricklayer.current_nav_state = 'request'
        bricklayer.name_contractor = self.username
        screen_manager.current = 'RequestContractor'

    def passo(self):
        app = MDApp.get_running_app()
        screen_manager = app.root
        bricklayer = screen_manager.get_screen('Perfil')
        bricklayer.username = self.username
        bricklayer.key = self.key
        bricklayer.ids.table.active = False
        bricklayer.ids.perfil.active = True
        bricklayer.ids.search.active = False
        bricklayer.ids.request.active = False
        bricklayer.current_nav_state = 'perfil'
        screen_manager.transition = SlideTransition(direction='left')
        screen_manager.current = 'Perfil'
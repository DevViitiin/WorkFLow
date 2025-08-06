from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


class RequestSent(MDScreen):
    # Propriedades que serão transferidas entre telas
    current_nav_state = StringProperty('payment')
    request = BooleanProperty()
    avatar = StringProperty()
    employee_name = StringProperty()
    employee_function = StringProperty()
    employee_mail = StringProperty()
    employee_telephone = StringProperty()
    key = StringProperty()
    employee_summary = StringProperty()
    skills = StringProperty()
    contractor = StringProperty()

    def on_enter(self, *args):
        """
        Evento acionado quando a tela é exibida.
        Garante que o valor de 'request' seja um booleano real.
        """
        self.request = bool(self.request)
        print(self.request)

    def _next_screen(self):
        """
        Navega para a tela 'RequestsVacancy' com os dados do funcionário.
        Ativa o ícone de notificações como estado de navegação.
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        perfil = screenmanager.get_screen('RequestsVacancy')

        # Transfere dados do funcionário
        perfil.key = self.key
        perfil.employee_name = self.employee_name
        perfil.employee_function = self.employee_function
        perfil.employee_mail = self.employee_mail
        perfil.employee_telephone = self.employee_telephone
        perfil.avatar = self.avatar
        perfil.employee_summary = self.employee_summary
        perfil.skills = self.skills
        perfil.tab_nav_state = 'received'
        perfil.request = self.request

        # Estado de navegação
        perfil.current_nav_state = 'perfil'
        perfil.ids.vacancy.active = False
        perfil.ids.perfil.active = False
        perfil.ids.payment.active = False
        perfil.ids.notification.active = True

        # Transição de tela
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'RequestsVacancy'

    def perfil(self):
        """
        Navega para a tela de perfil do funcionário ('PrincipalScreenEmployee'),
        transfere todos os dados necessários e atualiza a navegação.
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        perfil = screenmanager.get_screen('PrincipalScreenEmployee')

        # Transfere dados
        perfil.key = self.key
        perfil.employee_name = self.employee_name
        perfil.employee_function = self.employee_function
        perfil.employee_mail = self.employee_mail
        perfil.employee_telephone = self.employee_telephone
        perfil.avatar = self.avatar
        perfil.employee_summary = self.employee_summary
        perfil.skills = self.skills
        perfil.request = self.request

        # Estado de navegação
        perfil.ids.payment.active = False
        perfil.ids.vacancy.active = False
        perfil.ids.notification.active = False
        perfil.ids.perfil.active = True
        perfil.current_nav_state = 'perfil'

        self.tot_salary = 0  # Inicializa salário total

        # Transição de tela
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'PrincipalScreenEmployee'

    def vacancy(self):
        """
        Navega para a tela de banco de vagas ('VacancyBank'),
        passa todos os dados do funcionário e marca a aba de vagas como ativa.
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        vac = screenmanager.get_screen('VacancyBank')

        # Transfere dados
        vac.key = self.key
        print(self.key)
        vac.employee_name = self.employee_name
        vac.employee_function = self.employee_function
        vac.employee_mail = self.employee_mail
        vac.employee_telephone = self.employee_telephone
        vac.avatar = self.avatar
        vac.employee_summary = self.employee_summary
        vac.skills = self.skills
        vac.contractor = self.contractor
        vac.request = True

        # Estado de navegação
        self.current_nav_state = 'vacancy'
        vac.ids.vacancy.active = True
        vac.ids.perfil.active = False
        vac.ids.notification.active = False
        vac.ids.payment.active = False

        # Transição de tela
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'VacancyBank'

    def req(self):
        """
        Navega para a tela 'RequestsVacancy', focando na aba de requisições.
        Transfere os dados do funcionário e configura o estado de navegação.
        """
        app = MDApp.get_running_app()
        screenmanager = app.root

        vac = screenmanager.get_screen('RequestsVacancy')

        # Transfere dados
        vac.key = self.key
        vac.tab_nav_state = 'request'
        vac.current_nav_state = 'notification'
        vac.employee_name = self.employee_name
        vac.employee_function = self.employee_function
        vac.employee_mail = self.employee_mail
        vac.employee_telephone = self.employee_telephone
        vac.avatar = self.avatar
        vac.employee_summary = self.employee_summary
        vac.skills = self.skills
        vac.request = self.request
        vac.contractor = self.contractor

        # Estado de navegação
        vac.ids.vacancy.active = False
        vac.ids.perfil.active = False
        vac.ids.payment.active = False
        vac.ids.notification.active = True

        # Transição de tela
        screenmanager.transition = SlideTransition(direction='right')
        screenmanager.current = 'RequestsVacancy'

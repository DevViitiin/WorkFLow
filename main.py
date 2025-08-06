from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.uix.screenmanager import MDScreenManager
#from android.permissions import request_permissions, check_permission, Permission
from kivy.utils import platform
from libs.screens.add_employee_password.add_employee_password import AddEmployeePassword
from libs.screens.confirm_payment.confirm_payment import ConfirmPayment
from libs.screens.edit_profile.edit_profile import EditProfile
from libs.screens.edit_profile_employee.edit_profile_employee import EditProfileEmployee
from libs.screens.edit_profile_two.edit_profile_two import EditProfileTwo
from libs.screens.fourth_week.fourth_week import FourthWeek
from libs.screens.hiring_profile.hiring_profile import HiringProfile
from libs.screens.perfil_employee.perfil_employee import PerfilEmployee
from libs.screens.principal_screen.principal_screen import PerfilScreen
from libs.screens.report_bricklayer.report_bricklayer import ReportBricklayer
from libs.screens.request_contractor.request_contractor import RequestContractor
from libs.screens.table_screen.table_screen import TableScreen
from libs.screens.add_employee.add_employee import AddEmployee
from libs.screens.add_employee_avatar.add_employee_avatar import EmployeeAvatar
from libs.screens.function_screen.function_screen import FunctionScreen
from libs.screens.evaluation_screen.evaluation_screen import EvaluationScreen
from libs.screens.asses_punctuality.asses_punctuality import AssesPunctuality
from libs.screens.asses_effiency.asses_effiency import AssesEffiency
from libs.screens.asses_coexistence.asses_coexistence import AssesCoexistence
from libs.screens.third_week.third_week import ThirdWeek
from libs.screens.vacancy_contractor.vacancy_contractor import VacancyContractor
from libs.screens.working_bricklayer.working_bricklayer import WorkingBricklayer
from libs.screens.working_days.working_days import WorkingDays
from libs.screens.working_month.working_month import WorkingMonth
from libs.screens.first_week.first_week import FirstWeek
from libs.screens.second_week.second_week import SecondWeek
from kivy.core.window import Window
from libs.screens_employee.confirm_payment.confirm_payment import ConfirmPaymentEmployee
from libs.screens_employee.edit_profile_employee.edit_profile_employee import EditEmployee
from libs.screens_employee.edit_profile_employee_two.edit_profile_employe_two import EditEmployeeTwo
from libs.screens_employee.notification_page.notification_page import NotificationPage
from libs.screens_employee.principal_screen_employee.principal_screen_employee import PrincipalScreenEmployee
from libs.screens_employee.request_accept.request_accept import RequestAccept
from libs.screens_employee.request_sent.request_sent import RequestSent
from libs.screens_employee.requests_vacancy.requests_vacancy import RequestsVacancy
from libs.screens_employee.review_screen.review_screen import ReviewScreen
from libs.screens_employee.vacancy_bank.vacancy_bank import VacancyBank
from libs.screens_employee.view_payment_completed.view_payment_completed import ViewPaymentCompleted
from libs.screens_employee.without_contractor.without_contractor import WithoutContractor
from libs.screens_login.choice_account.choice_account import ChoiceAccount
from libs.screens_login.init_screen.init_screen import InitScreen
from libs.screens.functions_screen.functions_screen import FunctionsScreen
from libs.screens_login.register_contractor.register_contractor import RegisterContractor
from libs.screens_login.register_funcionario.register_funcionario import RegisterFuncionario


class MainApp(MDApp):

    def build(self):
        self.load_all_kv_files()
        self.screenmanager = MDScreenManager()

        # Parte do cadastro ou login inicial
        self.screenmanager.add_widget(InitScreen(name='Init'))
        self.screenmanager.add_widget(AddEmployeePassword(name='AddEmployeePassword'))
        self.screenmanager.add_widget(ConfirmPaymentEmployee(name='ConfirmPaymentEmployee'))
        self.screenmanager.add_widget(NotificationPage(name='NotificationPage'))
        self.screenmanager.add_widget(ViewPaymentCompleted(name='ViewPaymentCompleted'))
        self.screenmanager.add_widget(ReviewScreen(name='ReviewScreen'))
        self.screenmanager.add_widget(EvaluationScreen(name='Evaluation'))
        self.screenmanager.add_widget(RegisterFuncionario(name='RegisterFuncionario'))
        self.screenmanager.add_widget(RegisterContractor(name='RegisterContractor'))
        self.screenmanager.add_widget(ChoiceAccount(name='ChoiceAccount'))

        # Parte do aplicativo principal (Funcionario)
        self.screenmanager.add_widget(EditEmployeeTwo(name='EditEmployeeTwo'))
        self.screenmanager.add_widget(RequestSent(name='RequestSent'))
        self.screenmanager.add_widget(RequestAccept(name='RequestAccept'))
        self.screenmanager.add_widget(RequestsVacancy(name='RequestsVacancy'))
        self.screenmanager.add_widget(WithoutContractor(name='WithoutContractor'))
        self.screenmanager.add_widget(PrincipalScreenEmployee(name='PrincipalScreenEmployee'))
        self.screenmanager.add_widget(VacancyBank(name='VacancyBank'))
        self.screenmanager.add_widget(EditEmployee(name='EditEmployee'))

        # parte do aplicativo principal (Contratante)
        self.screenmanager.add_widget(ConfirmPayment(name='ConfirmPayment'))
        self.screenmanager.add_widget(RequestContractor(name='RequestContractor'))
        self.screenmanager.add_widget(HiringProfile(name='HiringProfile'))
        self.screenmanager.add_widget(VacancyContractor(name='VacancyContractor'))
        self.screenmanager.add_widget(PerfilEmployee(name='PerfilEmployee'))
        self.screenmanager.add_widget(PerfilScreen(name='Perfil'))
        self.screenmanager.add_widget(FunctionScreen(name='Function'))
        self.screenmanager.add_widget(FunctionsScreen(name='FunctionsScreen'))
        self.screenmanager.add_widget(WorkingMonth(name='WorkingMonth'))
        self.screenmanager.add_widget(EditProfileTwo(name='EditProfileTwo'))
        self.screenmanager.add_widget(EditProfile(name='EditProfile'))
        self.screenmanager.add_widget(EmployeeAvatar(name='EmployeeAvatar'))

        self.screenmanager.add_widget(AddEmployee(name='Add'))
        self.screenmanager.add_widget(ReportBricklayer(name='ReportBricklayer'))
        self.screenmanager.add_widget(WorkingBricklayer(name='WorkingBricklayer'))
        self.screenmanager.add_widget(EditProfileEmployee(name='EditProfileEmployee'))
        self.screenmanager.add_widget(WorkingDays(name='WorkingDays'))
        self.screenmanager.add_widget(AssesEffiency(name='AssesEfficiency'))
        self.screenmanager.add_widget(FourthWeek(name='FourthWeek'))
        self.screenmanager.add_widget(ThirdWeek(name='ThirdWeek'))
        self.screenmanager.add_widget(SecondWeek(name='SecondWeek'))
        self.screenmanager.add_widget(FirstWeek(name='FirstWeek'))
        self.screenmanager.add_widget(AssesCoexistence(name='AssesCoexistence'))
        self.screenmanager.add_widget(AssesPunctuality(name='AssesPunctuality'))
        self.screenmanager.add_widget(TableScreen(name='Table'))
        Clock.schedule_once(lambda dt: self.solicitar_permissoes(), 0.5)

        return self.screenmanager

    def solicitar_permissoes(self):
        #if platform == 'android':
            #if not check_permission(Permission.READ_EXTERNAL_STORAGE):
                #request_permissions([Permission.READ_EXTERNAL_STORAGE])
        pass

    def load_all_kv_files(self):
        Builder.load_file('libs/screens/edit_profile/edit_profile.kv')
        Builder.load_file('libs/screens/principal_screen/principal_screen.kv')
        Builder.load_file('libs/screens/edit_profile_two/edit_profile_two.kv')
        Builder.load_file('libs/screens/table_screen/table_screen.kv')
        Builder.load_file('libs/screens/add_employee/add_employee.kv')
        Builder.load_file('libs/screens/add_employee_avatar/add_employee_avatar.kv')
        Builder.load_file('libs/screens/function_screen/function_screen.kv')
        Builder.load_file('libs/screens/functions_screen/functions_screen.kv')
        Builder.load_file('libs/screens/evaluation_screen/evaluation_screen.kv')
        Builder.load_file('libs/screens/asses_punctuality/asses_punctuality.kv')
        Builder.load_file('libs/screens/asses_effiency/asses_effiency.kv')
        Builder.load_file('libs/screens/asses_coexistence/asses_coexistence.kv')
        Builder.load_file('libs/screens/working_days/working_days.kv')
        Builder.load_file('libs/screens/working_month/working_month.kv')
        Builder.load_file('libs/screens/first_week/first_week.kv')
        Builder.load_file('libs/screens/second_week/second_week.kv')
        Builder.load_file('libs/screens/third_week/third_week.kv')
        Builder.load_file('libs/screens/fourth_week/fourth_week.kv')
        Builder.load_file('libs/screens/edit_profile_employee/edit_profile_employee.kv')
        Builder.load_file('libs/screens/working_bricklayer/working_bricklayer.kv')
        Builder.load_file('libs/screens/report_bricklayer/report_bricklayer.kv')
        Builder.load_file('libs/screens/vacancy_contractor/vacancy_contractor.kv')
        Builder.load_file('libs/screens/perfil_employee/perfil_employee.kv')
        Builder.load_file('libs/screens/request_contractor/request_contractor.kv')
        Builder.load_file('libs/screens/hiring_profile/hiring_profile.kv')
        Builder.load_file('libs/screens/confirm_payment/confirm_payment.kv')

        # telas do funcionario -------------
        Builder.load_file('libs/screens_employee/request_sent/request_sent.kv')
        Builder.load_file('libs/screens_employee/without_contractor/without_contractor.kv')
        Builder.load_file('libs/screens_employee/principal_screen_employee/principal_screen_employe.kv')
        Builder.load_file('libs/screens_employee/vacancy_bank/vacancy_bank.kv')
        Builder.load_file('libs/screens_employee/edit_profile_employee/edit_profile_employee.kv')
        Builder.load_file('libs/screens_employee/edit_profile_employee_two/edit_profile_employee_two.kv')
        Builder.load_file('libs/screens_employee/requests_vacancy/requests_vacancy.kv')
        Builder.load_file('libs/screens_employee/review_screen/review_screen.kv')
        Builder.load_file('libs/screens/add_employee_password/add_employee_password.kv')
        Builder.load_file('libs/screens_employee/request_accept/request_accept.kv')
        Builder.load_file('libs/screens_employee/notification_page/notification_page.kv')
        Builder.load_file('libs/screens_employee/view_payment_completed/view_payment_completed.kv')
        Builder.load_file('libs/screens_employee/confirm_payment/confirm_payment.kv')

        # Telas de inicio (login e cadastro)
        Builder.load_file('libs/screens_login/choice_account/choice_account.kv')
        Builder.load_file('libs/screens_login/init_screen/init_screen.kv')
        Builder.load_file('libs/screens_login/register_contractor/register_contractor.kv')
        Builder.load_file('libs/screens_login/register_funcionario/register_funcionario.kv')


MainApp().run()

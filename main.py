from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.uix.screenmanager import MDScreenManager
from android.permissions import request_permissions, check_permission, Permission
from kivy.utils import platform
from libs.screens.edit_profile.edit_profile import EditProfile
from libs.screens.edit_profile_employee.edit_profile_employee import EditProfileEmployee
from libs.screens.edit_profile_two.edit_profile_two import EditProfileTwo
from libs.screens.hiring_profile.hiring_profile import HiringProfile
from libs.screens.perfil_employee.perfil_employee import PerfilEmployee
from libs.screens.principal_screen.principal_screen import PerfilScreen
from libs.screens.request_contractor.request_contractor import RequestContractor
from libs.screens.add_employee_avatar.add_employee_avatar import EmployeeAvatar
from libs.screens.function_screen.function_screen import FunctionScreen
from libs.screens.vacancy_contractor.vacancy_contractor import VacancyContractor
from kivy.core.window import Window
from libs.screens_employee.edit_profile_employee.edit_profile_employee import EditEmployee
from libs.screens_employee.edit_profile_employee_two.edit_profile_employe_two import EditEmployeeTwo
from libs.screens_employee.principal_screen_employee.principal_screen_employee import PrincipalScreenEmployee
from libs.screens_employee.request_accept.request_accept import RequestAccept
from libs.screens_employee.request_sent.request_sent import RequestSent
from libs.screens_employee.requests_vacancy.requests_vacancy import RequestsVacancy
from libs.screens_employee.review_screen.review_screen import ReviewScreen
from libs.screens_employee.vacancy_bank.vacancy_bank import VacancyBank
from libs.screens_employee.without_contractor.without_contractor import WithoutContractor
from libs.screens_login.choice_account.choice_account import ChoiceAccount
from libs.screens_login.init_screen.init_screen import InitScreen
from libs.screens.functions_screen.functions_screen import FunctionsScreen
from libs.screens_login.register_contractor.register_contractor import RegisterContractor
from libs.screens_login.register_funcionario.register_funcionario import RegisterFuncionario
from libs.screens_login.splash_screen.splash_screen import SplashScreen
from libs.screens_employee.confirm_payment_bricklayer.confirm_payment_bricklayer import ConfirmPaymentBricklayer
from libs.screens_employee.view_payment_bricklayer.view_payment_bricklayer import ViewPaymentBricklayer
from libs.screens_global.suspension_screen.suspension_screen import SuspensionScreen
from libs.screens_global.warning_screen.warning_screen import WarningScreen
from libs.screens_global.ban_screen.ban_screen import BanScreen
from libs.screens_global.report_screen.report_screen import ReportScreen
from libs.screens_global.list_chat.list_chat import ListChat
from libs.screens_global.chat.chat import Chat
from libs.screens_global.perfil_employee.perfil_employee import PerfilEmployeeGlobal
from libs.screens_global.perfil_contractor.perfil_contractor import PerfilContractorGlobal
from libs.screens_global.list_chat_contractor.list_chat_contractor import ListChatContractor
from libs.screens_global.report_contractor.report_contractor import ReportContractor
from libs.screens_global.identify_contractor.identify_contractor import IdentifyContractor
from libs.screens_global.identify_perfil.identify_perfil import IdentifyPerfil
from libs.screens_global.reported_created.reported_created import ReportedCreated
from libs.screens_global.report_chat.report_chat import ReportChat



class MainApp(MDApp):

    def build(self):
        Window.size = (350, 650)
        self.screenmanager = MDScreenManager()
        self.load_all_kv_files()
        # Parte do cadastro ou login iniciald
        self.screenmanager.add_widget(InitScreen(name='Init'))
        self.screenmanager.add_widget(ReportChat(name='ReportChat'))
        self.screenmanager.add_widget(ListChatContractor(name='ListChatContractor'))
        self.screenmanager.add_widget(ReviewScreen(name='ReviewScreen'))
        self.screenmanager.add_widget(ViewPaymentBricklayer(name='ViewPaymentBricklayer'))
        self.screenmanager.add_widget(ConfirmPaymentBricklayer(name='ConfirmPaymentBricklayer'))
        self.screenmanager.add_widget(SplashScreen(name='SplashScreen'))
        self.screenmanager.add_widget(ListChat(name='ListChat'))
        self.screenmanager.add_widget(Chat(name='Chat'))
        self.screenmanager.add_widget(PerfilEmployeeGlobal(name='PerfilEmployeeGlobal'))
        self.screenmanager.add_widget(PerfilContractorGlobal(name='PerfilContractorGlobal')) 
        
        # screens globais 
        self.screenmanager.add_widget(ReportedCreated(name='ReportedCreated'))
        self.screenmanager.add_widget(IdentifyContractor(name='IdentifyContractor'))
        self.screenmanager.add_widget(IdentifyPerfil(name='IdentifyPerfil'))
        self.screenmanager.add_widget(ReportScreen(name='ReportScreen'))
        self.screenmanager.add_widget(ReportContractor(name='ReportContractor'))
        self.screenmanager.add_widget(BanScreen(name='BanScreen'))
        self.screenmanager.add_widget(WarningScreen(name='WarningScreen'))
        self.screenmanager.add_widget(SuspensionScreen(name='SuspensionScreen'))
        self.screenmanager.add_widget(RegisterFuncionario(name='RegisterFuncionario'))
        self.screenmanager.add_widget(RegisterContractor(name='RegisterContractor'))
        self.screenmanager.add_widget(ChoiceAccount(name='ChoiceAccount'))

        # Parte do aplicativo principal (Funciomnario)
        self.screenmanager.add_widget(EditEmployeeTwo(name='EditEmployeeTwo'))
        self.screenmanager.add_widget(RequestSent(name='RequestSent'))
        self.screenmanager.add_widget(RequestAccept(name='RequestAccept'))
        self.screenmanager.add_widget(RequestsVacancy(name='RequestsVacancy'))
        self.screenmanager.add_widget(WithoutContractor(name='WithoutContractor'))
        self.screenmanager.add_widget(PrincipalScreenEmployee(name='PrincipalScreenEmployee'))
        self.screenmanager.add_widget(VacancyBank(name='VacancyBank'))
        self.screenmanager.add_widget(EditEmployee(name='EditEmployee'))

        # parte do aplicativo principal (Contratante)
        self.screenmanager.add_widget(RequestContractor(name='RequestContractor'))
        self.screenmanager.add_widget(HiringProfile(name='HiringProfile'))
        self.screenmanager.add_widget(VacancyContractor(name='VacancyContractor'))
        self.screenmanager.add_widget(PerfilEmployee(name='PerfilEmployee'))
        self.screenmanager.add_widget(PerfilScreen(name='Perfil'))
        self.screenmanager.add_widget(FunctionScreen(name='Function'))
        self.screenmanager.add_widget(FunctionsScreen(name='FunctionsScreen'))
        self.screenmanager.add_widget(EditProfileTwo(name='EditProfileTwo'))
        self.screenmanager.add_widget(EditProfile(name='EditProfile'))
        self.screenmanager.add_widget(EmployeeAvatar(name='EmployeeAvatar'))

        self.screenmanager.add_widget(EditProfileEmployee(name='EditProfileEmployee'))
        Clock.schedule_once(lambda dt: self.solicitar_permissoes(), 0.5)
        return self.screenmanager

    def solicitar_permissoes(self):
        if platform == 'android':
       
            if not check_permission(Permission.READ_EXTERNAL_STORAGE):
                request_permissions([Permission.READ_EXTERNAL_STORAGE])
        pass 

    def on_stop(self):
        '''Executado quando o app fecha'''
        print('🛑 App fechando - marcando todos como offline')
        
        # Tenta marcar o usuário atual como offline
        try:
            # Acessa a tela de chat se estiver disponível
            if hasattr(self.root, 'get_screen'):
                try:
                    chat_screen = self.root.get_screen('Chat')
                    if chat_screen and hasattr(chat_screen, 'mark_user_offline'):
                        chat_screen.stop_heartbeat()
                        chat_screen.mark_user_offline()
                        print('✓ Usuário marcado como offline no on_stop')
                except:
                    pass
        except Exception as e:
            print(f'Erro ao marcar offline no on_stop: {e}')
        
        return True
    
    def load_all_kv_files(self):
        Builder.load_file('libs/screens_global/report_chat/report_chat.kv')
        Builder.load_file('libs/screens_global/reported_created/reported_created.kv')
        Builder.load_file('libs/screens_global/identify_contractor/identify_contractor.kv')
        Builder.load_file('libs/screens_global/report_contractor/report_contractor.kv')
        Builder.load_file('libs/screens_global/list_chat_contractor/list_chat_contractor.kv')
        Builder.load_file('libs/screens_global/perfil_contractor/perfil_contractor.kv')
        Builder.load_file('libs/screens_global/perfil_employee/perfil_employee.kv')
        Builder.load_file('libs/screens_global/chat/chat.kv')
        Builder.load_file('libs/screens_global/list_chat/list_chat.kv')
        Builder.load_file('libs/screens_global/report_screen/report_screen.kv')
        Builder.load_file('libs/screens_global/ban_screen/ban_screen.kv')
        Builder.load_file('libs/screens_global/warning_screen/warning_screen.kv')
        Builder.load_file('libs/screens_global/suspension_screen/suspension_screen.kv')
        Builder.load_file('libs/screens/edit_profile/edit_profile.kv')
        Builder.load_file('libs/screens/principal_screen/principal_screen.kv')
        Builder.load_file('libs/screens/edit_profile_two/edit_profile_two.kv')
        Builder.load_file('libs/screens/add_employee_avatar/add_employee_avatar.kv')
        Builder.load_file('libs/screens/function_screen/function_screen.kv')
        Builder.load_file('libs/screens/functions_screen/functions_screen.kv')
        Builder.load_file('libs/screens/edit_profile_employee/edit_profile_employee.kv')
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
        Builder.load_file('libs/screens_employee/request_accept/request_accept.kv')
        Builder.load_file('libs/screens_employee/confirm_payment/confirm_payment.kv')

        # Telas de inicio (login e cadastro)
        Builder.load_file('libs/screens_login/choice_account/choice_account.kv')
        Builder.load_file('libs/screens_login/init_screen/init_screen.kv')
        Builder.load_file('libs/screens_login/splash_screen/splash_screen.kv')
        Builder.load_file('libs/screens_login/register_contractor/register_contractor.kv')
        Builder.load_file('libs/screens_login/register_funcionario/register_funcionario.kv')

MainApp().run()

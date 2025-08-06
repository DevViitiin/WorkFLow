from kivy.properties import StringProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
import bcrypt


class AddEmployeePassword(MDScreen):
    employee_name = StringProperty()
    function = StringProperty()
    password = StringProperty()
    contractor = StringProperty()
    method_salary = StringProperty()
    salary = StringProperty()
    scale = StringProperty()

    def hashed_password(self):
        password = self.ids.password.text
        print(password)
        if len(password) >= 8:
            hashed_password = self.ids.password.text.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password=hashed_password, salt=salt).decode('utf-8')

            # Exibir a senha criptografada
            print('A senha criptgrafada é: ', hashed_password)
            self.next_page(hashed_password)
        else:
            print('A senha está desaprovada')

    def next_page(self, passsword):
        self.manager.transition = SlideTransition(direction='left')
        app = MDApp.get_running_app()
        screen_manager = app.root
        employee_avatar = screen_manager.get_screen('EmployeeAvatar')
        employee_avatar.employee_name = self.employee_name
        employee_avatar.function = self.function
        employee_avatar.salary = self.salary
        employee_avatar.contractor = self.contractor
        employee_avatar.method_salary = self.method_salary
        employee_avatar.scale = self.scale
        employee_avatar.password = f"{passsword}"
        self.ids.password.text = ''
        screen_manager.current = 'EmployeeAvatar'
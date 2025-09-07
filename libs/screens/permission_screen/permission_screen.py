from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.screen import MDScreen
from android.permissions import request_permissions, check_permission, Permission


class PermissionScreen(MDScreen):

    def request_permission(self):
        """
        Verifica e solicita permissões, se necessário.
        """
        request_permissions(
            permissions=[
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ],
            callback=self.permission_callback
        )
        print("Solicitando permissões...")

    def permission_callback(self, permissions, results):
        """
        Callback chamado após o usuário permitir ou negar permissões.
        :param permissions: Lista de permissões solicitadas.
        :param results: Lista de resultados (True para permitido, False para negado).
        """
        for permission, result in zip(permissions, results):
            if result:
                print(f"Permissão concedida: {permission}")
                self.on_permissions_granted()
            else:
                print(f"Permissão negada: {permission}")
                self.on_permissions_denied()

    def on_permissions_granted(self):
        """
        Ações a serem executadas se as permissões forem concedidas.
        """
        print("Permissões concedidas, execute a funcionalidade necessária.")
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'EditProfile'

    def on_permissions_denied(self):
        """
        Ações a serem executadas se as permissões forem negadas.
        """
        print("Permissões negadas, mostre uma mensagem ou desative a funcionalidade.")
        self.manager.transition = SlideTransition(direction='right')


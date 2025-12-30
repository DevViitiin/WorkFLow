import ast
import json
from datetime import datetime

from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from configurations import DialogNoNet, DialogInfinityUpload, DialogErrorUnknow, firebase_url, check_error, SignController
import uuid
from kivy.clock import Clock


class RequestAccept(MDScreen):
    """
    Tela para gerenciar aceitação ou recusa de solicitações de contratação.

    Esta classe permite que um contratante adicione um funcionário à sua equipe
    ou dispense o funcionário, removendo-o da lista de solicitações pendentes.
    Gerencia toda a comunicação com o banco de dados Firebase para manter
    os registros atualizados.
    """
    # Propriedades que serão compartilhadas entre telas ou com o backend
    key_contractor = StringProperty()
    username = StringProperty()
    company = StringProperty()
    city = StringProperty()
    state = StringProperty()
    function = StringProperty()
    avatar = StringProperty()
    token_id = StringProperty()
    api_key = StringProperty()
    local_id = StringProperty()
    refresh_token = StringProperty()
    email = StringProperty()
    telefone = StringProperty()
    data_contractor = StringProperty()
    contractor = StringProperty()
    required_function = StringProperty()
    key = StringProperty()
    FIREBASE_URL = firebase_url()

    def on_enter(self):
        """Inicializa dialogs ao entrar na tela"""
        print('A key do contratante é: ', self.key_contractor)
        print('Key da requisição: ', self.key)
        print('Token id: ', self.token_id)
        
        # ====================== Inicializa popups =============================
        self.inf_dialog = DialogInfinityUpload()
        self.signcontroller = SignController(screen=self, name=self.name)
        
        # Dialog para erro de conexão na contratação
        self.dialog_not_net_hire = DialogNoNet(
            subtitle='Não foi possível contratar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.hire_employee)
        )
        
        # Dialog para erro de conexão na recusa
        self.dialog_not_net_reject = DialogNoNet(
            subtitle='Não foi possível recusar. Verifique sua internet e tente novamente',
            callback=lambda: self.signcontroller.retry_signup(self.reject_candidate)
        )
        
        # Dialog para erros desconhecidos
        self.dialog_error_unknown = DialogErrorUnknow(screen=f'{self.name}')
        
        # Verifica token
        self.verific_token()
        self.event_token = Clock.schedule_interval(self.verific_token, 300)

    def on_leave(self, *args):
        """Cancela verificações ao sair da tela"""
        if hasattr(self, 'event_token'):
            self.event_token.cancel()
            print("⏱️ Clock do token cancelado ao sair da tela")

    def verific_token(self, *args):
        """Verifica se o token ainda é válido"""
        if not self.get_parent_window():
            return
        
        print('🔎 verificando token...')
        UrlRequest(
            f"{self.FIREBASE_URL}/Funcionarios/{self.local_id}.json?auth={self.token_id}",
            on_success=self.on_token_success,
            on_failure=self.on_token_failure,
            on_error=self.on_token_failure,
            method="GET"
        )

    def on_token_failure(self, req, result):
        """Token inválido, tenta atualizar"""
        print('❌ Token inválido, tentando atualizar...', result)
        self.refresh_id_token()

    def on_token_success(self, req, result):
        """Token válido"""
        print('✅ Token válido, usuário encontrado')

    def refresh_id_token(self):
        """Atualiza o token de autenticação"""
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
        """Token renovado com sucesso"""
        self.token_id = result["id_token"]
        self.refresh_token = result["refresh_token"]
        print("🔄 Token renovado com sucesso")

    def on_refresh_failure(self, req, result):
        """Erro ao renovar token"""
        print("❌ Erro ao renovar token:", result)
        self._show_snackbar('O token não foi renovado', 'red')
        Clock.schedule_once(lambda dt: self._show_snackbar('Refaça login no aplicativo', 'red'), 1)

    def _show_snackbar(self, text, bg_color='green'):
        """
        Exibe uma mensagem temporária na parte inferior da tela.

        Args:
            text (str): Texto a ser exibido na mensagem.
            bg_color (str): Cor de fundo da mensagem.
        """
        MDSnackbar(
            MDSnackbarText(
                text=text,
                theme_text_color='Custom',
                text_color='white',
                bold=True
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            halign='center',
            size_hint_x=0.9,
            theme_bg_color='Custom',
            background_color=bg_color
        ).open()

    def hire_employee(self):
        """
        Adiciona o contratante e o funcionário na base de chat do Firebase.
        """
        try:
            # Mostra loading
            self.inf_dialog.open()
            
            # Obtém a data atual
            data_atual = datetime.now()
            chat_id = str(uuid.uuid4())
            timestamp = data_atual.strftime('%d/%m/%Y')

            data = {
                'contractor': f'{self.key_contractor}',
                'employee': f'{self.local_id}',
                
                "participants": {
                    'contractor': 'offline',
                    'employee': 'offline'
                },
                "metadata": {
                    "created_at": timestamp,
                    "last_message": "",
                    "last_sender": "",
                    "last_timestamp": timestamp
                },
                "historical_messages": {
                    'messages_contractor': '[]',
                    'messages_employee': '[]'
                },
                'message_offline': {
                    'contractor': '[]',
                    'employee': '[]'
                }
            }

            UrlRequest(
                f"{self.FIREBASE_URL}/Chats/{chat_id}.json?auth={self.token_id}",
                req_body=json.dumps(data),
                method='PUT',
                on_success=self.process_after_hiring,
                on_error=self.handle_hire_error,
                on_failure=self.handle_hire_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao recrutar funcionário: {str(e)}")
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()

    def handle_hire_error(self, req, result):
        """Trata erros na requisição de contratação"""
        print(f"Erro na contratação: {result}")
        
        error_type = check_error(result)
        
        if error_type == 'no_internet':
            self.dialog_not_net_hire.dismiss()
            Clock.schedule_once(lambda dt: self.open_hire_no_internet_dialog(), 1.5)
        else:
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()

    def handle_hire_failure(self, req, result):
        """Trata falhas de conexão na contratação"""
        print('Falha na conexão durante contratação: ', result)
        Clock.schedule_once(lambda dt: self.open_hire_no_internet_dialog(), 1.5)

    def open_hire_no_internet_dialog(self):
        """Abre dialog de sem internet para contratação"""
        self.inf_dialog.dismiss()
        self.dialog_not_net_hire.open()

    def process_after_hiring(self, req, result):
        """
        Após criar o chat, inicia a remoção da requisição
        """
        try:
            print("✅ Chat criado com sucesso")
            
            url = (
                f'{firebase_url()}/requets.json'
                f'?auth={self.token_id}&orderBy="key"&equalTo="{self.local_id}"'
            )
            
            UrlRequest(
                url,
                on_success=self.handle_successful_deletion,
                on_error=self.handle_hire_error,
                on_failure=self.handle_hire_failure,
                timeout=10
            )
            
        except Exception as e:
            print(f"Erro ao processar recrutamento: {str(e)}")
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()
        finally:
            self.signcontroller.close_all_dialogs()

    def handle_successful_deletion(self, req, result):
        """
        Remove a key do contratante das requisições do funcionário
        """
        print('Resultado da busca de requisições: ', result)
        
        try:
            id_ = ''
            key_send = []
            
            for key, dic in result.items():
                id_ = str(key)
                key_send = ast.literal_eval(dic['requests'])
            
            if self.key_contractor in key_send:
                key_send.remove(self.key_contractor)
            
            id_ = id_.replace('-', '')
            data = {
                'requests': f'{key_send}'
            }
            
            url = f'{firebase_url()}/requets/{id_}.json?auth={self.token_id}'
            print('Os dados sem a key do contratante são: ', key_send)
            
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.skyfall,
                on_error=self.handle_hire_error,
                on_failure=self.handle_hire_failure
            )
        except Exception as e:
            print(f"Erro ao processar exclusão: {str(e)}")
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()
        finally:
            self.signcontroller.close_all_dialogs()
    
    def skyfall(self, req, result):
        """Busca dados do funcionário para atualizar receiveds"""
        print('✅ Requisição removida com sucesso')
        url = f'{firebase_url()}/Funcionarios/{self.local_id}.json?auth={self.token_id}'
        
        UrlRequest(
            url,
            on_success=self.skyfall2,
            on_error=self.handle_hire_error,
            on_failure=self.handle_hire_failure
        )

    def skyfall2(self, req, result):
        """Remove a key do contratante da lista 'receiveds' do funcionário"""
        print('Skyfall2 - Dados recebidos: ', result)
        
        try:
            receiveds_str = result.get('receiveds', '[]')
            key_send = ast.literal_eval(receiveds_str) if isinstance(receiveds_str, str) else receiveds_str
            
            # Remove a key do contratante se existir
            if self.key_contractor in key_send:
                key_send.remove(self.key_contractor)
                print(f'✅ Removido {self.key_contractor} de receiveds')
            else:
                print(f'⚠️ {self.key_contractor} não estava em receiveds')
            
            data = {
                'receiveds': f'{key_send}'
            }
            
            url = f'{firebase_url()}/Funcionarios/{self.local_id}.json?auth={self.token_id}'
            print('📤 Atualizando receiveds finais: ', key_send)
            
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.finalize_hiring,
                on_error=self.handle_hire_error,
                on_failure=self.handle_hire_failure
            )
        except Exception as e:
            print(f'❌ Erro no skyfall2: {e}')
            self.signcontroller.close_all_dialogs()
            self._show_snackbar(f"Erro ao finalizar: {str(e)}", "red")
            # Mesmo com erro, navega de volta
            self._navigate_back_with_reload()
        finally:
            self.signcontroller.close_all_dialogs()

    def finalize_hiring(self, req, result):
        """Finaliza o processo de contratação com sucesso"""
        print('✅ Processo de contratação finalizado completamente!')
        self.signcontroller.close_all_dialogs()
        self._show_snackbar("Chat aceito com sucesso!", "green")
        
        # Navega de volta COM reload dos dados
        self.signcontroller.close_all_dialogs()
        Clock.schedule_once(lambda dt: self._navigate_back_with_reload(), 0.5)

    def reject_candidate(self):
        """
        Desvincula o funcionário do contratante atual sem aceitá-lo na equipe.
        """
        try:
            # Mostra loading
            self.inf_dialog.open()
            
            url = f'{firebase_url()}/Funcionarios/{self.local_id}/.json?auth={self.token_id}'

            UrlRequest(
                url,
                on_success=self.update_employee_data_after_rejection,
                on_error=self.handle_reject_error,
                on_failure=self.handle_reject_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao dispensar funcionário: {str(e)}")
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()

    def handle_reject_error(self, req, result):
        """Trata erros na requisição de recusa"""
        print(f"Erro na recusa: {result}")
        
        error_type = check_error(result)
        
        if error_type == 'no_internet':
            self.dialog_not_net_reject.dismiss()
            Clock.schedule_once(lambda dt: self.open_reject_no_internet_dialog(), 1.5)
        else:
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()

    def handle_reject_failure(self, req, result):
        """Trata falhas de conexão na recusa"""
        print('Falha na conexão durante recusa: ', result)
        Clock.schedule_once(lambda dt: self.open_reject_no_internet_dialog(), 1.5)

    def open_reject_no_internet_dialog(self):
        """Abre dialog de sem internet para recusa"""
        self.inf_dialog.dismiss()
        self.dialog_not_net_reject.open()

    def update_employee_data_after_rejection(self, req, result):
        """Após obter os dados do funcionário, remove o contratante da lista de recebidos."""
        try:
            print('Dados do funcionário: ', result)

            if not result or 'receiveds' not in result:
                print("Dados do funcionário inválidos ou incompletos")
                self.signcontroller.close_all_dialogs()
                self._show_snackbar("Erro: dados do funcionário não encontrados", "red")
                return

            try:
                rk = ast.literal_eval(result['receiveds'])

                # Remove o contratante da lista
                if self.key_contractor in rk:
                    rk.remove(self.key_contractor)

                data = {
                    'contractor': '',
                    'receiveds': f"{rk}"
                }

                UrlRequest(
                    f'{firebase_url()}/Funcionarios/{self.local_id}/.json?auth={self.token_id}',
                    req_body=json.dumps(data),
                    method='PATCH',
                    on_success=self.fetch_requests_after_rejection,
                    on_error=self.handle_reject_error,
                    on_failure=self.handle_reject_failure,
                    timeout=10
                )
            except (SyntaxError, ValueError) as e:
                print(f"Erro ao processar lista 'receiveds': {str(e)}")
                self.signcontroller.close_all_dialogs()
                self.dialog_error_unknown.open()

        except Exception as e:
            print(f"Erro ao processar próxima etapa: {str(e)}")
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()

    def fetch_requests_after_rejection(self, req, result):
        """
        Após atualizar os dados do funcionário, busca as requisições para ajustar a lista de recusa.
        """
        try:
            url = (
                f'{firebase_url()}/requets.json'
                f'?auth={self.token_id}&orderBy="key"&equalTo="{self.local_id}"'
            )

            UrlRequest(
                url,
                on_success=self.process_candidate_rejection,
                on_error=self.handle_reject_error,
                on_failure=self.handle_reject_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao buscar requisições: {str(e)}")
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()

    def process_candidate_rejection(self, req, result):
        """
        Remove a key do contratante das requisições após recusa
        """
        print('Processando recusa - resultado:', result)
        
        try:
            id_ = ''
            key_send = []
            
            for key, dic in result.items():
                id_ = str(key)
                key_send = ast.literal_eval(dic.get('requests', '[]'))
            
            if self.key_contractor in key_send:
                key_send.remove(self.key_contractor)
            
            id_ = id_.replace('-', '')
            data = {
                'requests': f'{key_send}'
            }
            
            url = f'{firebase_url()}/requets/{id_}.json?auth={self.token_id}'
            
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.handle_successful_rejection,
                on_error=self.handle_reject_error,
                on_failure=self.handle_reject_failure
            )
        except Exception as e:
            print(f"Erro ao processar recusa: {str(e)}")
            self.signcontroller.close_all_dialogs()
            self.dialog_error_unknown.open()

    def handle_successful_rejection(self, req, result):
        """
        Conclui a recusa do contratante com sucesso
        """
        print('✅ Recusa finalizada com sucesso')
        self.signcontroller.close_all_dialogs()
        self._show_snackbar("Contratante dispensado com sucesso", "green")
        
        # Navega de volta COM reload
        Clock.schedule_once(lambda dt: self._navigate_back_with_reload(), 0.5)

    def _navigate_back_with_reload(self):
        """
        Navega de volta e FORÇA o reload dos dados do Firebase
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            request_screen = screenmanager.get_screen('RequestsVacancy')

            # Atualiza os dados de autenticação
            request_screen.key = self.key
            request_screen.data_contractor = self.data_contractor
            request_screen.contractor = self.contractor
            request_screen.api_key = self.api_key
            request_screen.local_id = self.local_id
            request_screen.refresh_token = self.refresh_token
            request_screen.token_id = self.token_id

            # Limpa a tela ANTES de navegar
            request_screen.ids.main_scroll.clear_widgets()
            request_screen._request_count = 0

            # Navega para a tela
            screenmanager.transition = SlideTransition(direction='left')
            screenmanager.current = 'RequestsVacancy'
            
            # Agenda o reload para DEPOIS da navegação
            def reload_data(dt):
                if request_screen.tab_nav_state == 'received':
                    print('🔄 Recarregando receiveds...')
                    request_screen.receiveds()
                else:
                    print('🔄 Recarregando requests...')
                    request_screen.upload_requests()
            
            Clock.schedule_once(reload_data, 0.3)
            
        except Exception as e:
            print(f"❌ Erro ao navegar: {e}")
            self.dialog_error_unknown.open()

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
import uuid
import time


class RequestAccept(MDScreen):
    """
    Tela para gerenciar aceitação ou recusa de solicitações de contratação.

    Esta classe permite que um contratante adicione um funcionário à sua equipe
    ou dispense o funcionário, removendo-o da lista de solicitações pendentes.
    Gerencia toda a comunicação com o banco de dados Firebase para manter
    os registros atualizados.

    Attributes:
        key_contractor (StringProperty): Chave única do contratante no banco de dados.
        username (StringProperty): Nome de usuário do contratante.
        company (StringProperty): Nome da empresa do contratante.
        city (StringProperty): Cidade do contratante ou funcionário.
        state (StringProperty): Estado do contratante ou funcionário.
        function (StringProperty): Função/cargo atual ou desejada.
        avatar (StringProperty): Caminho para a imagem de avatar.
        email (StringProperty): Email de contato.
        telefone (StringProperty): Número de telefone de contato.
        contractor (StringProperty): Nome do contratante atual (se houver).
        required_function (StringProperty): Função requerida para a vaga.
        key (StringProperty): Chave única do funcionário no banco de dados.
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
    FIREBASE_URL = "https://obra-7ebd9-default-rtdb.firebaseio.com/"
    CHAT_PATH = f"{FIREBASE_URL}/Chats.json?auth={token_id}"

    def on_enter(self):
        print('A key do contratante é: ', self.key_contractor)
        print('Key da requisição: ', self.key)
        print('Token id: ', self.token_id)

    def _show_snackbar(self, text, bg_color='green'):
        """
        Exibe uma mensagem temporária na parte inferior da tela.

        Args:
            text (str): Texto a ser exibido na mensagem.
            bg_color (str, optional): Cor de fundo da mensagem. Padrão é 'green'.
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
        Adiciona o contratante e o funcionario na base de chat do Firebase.

        """
        try:
            month = datetime.today().month
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

            self._show_snackbar("Aceitando chat do contratante...", "blue")

            UrlRequest(
                f"{self.FIREBASE_URL}/Chats/{chat_id}.json?auth={self.token_id}",
                req_body=json.dumps(data),
                method='PUT',
                on_success=self.process_after_hiring,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao recrutar funcionário: {str(e)}")
            self._show_snackbar(f"Erro ao recrutar: {str(e)}", "red")

    def on_error(self, request, error):
        """
        Callback para tratamento de erros de requisição.

        Args:
            request: Objeto de requisição que gerou o erro.
            error: Informações sobre o erro ocorrido.
        """
        print(f"Erro na requisição: {error}")
        self._show_snackbar(f"Erro na operação: {error}", "red")

    def on_failure(self, req, result):
        """
        Callback para tratamento de falhas de conexão.

        Args:
            request: Objeto de requisição que falhou.
            result: Informações sobre a falha.
        """
        print('error nessa porra: ', result)
        self._show_snackbar("Falha na conexão. Verifique sua internet.", "red")

    def process_after_hiring(self, req, result):
        """
        Após o recrutamento, redireciona para a tela 'RequestsVacancy' e inicia a exclusão da requisição.

        Args:
            req: Objeto da requisição HTTP.
            result: Dados retornados pela requisição.
        """
        try:
            app = MDApp.get_running_app()
            screenmanager = app.root
            request = screenmanager.get_screen('RequestsVacancy')

            # Transfere os dados necessários para a próxima tela
            request.key = self.key
            if 'contractor' in result:
                request.contractor = result['contractor']
            else:
                request.contractor = self.username

            self._show_snackbar("Finalizando processo de contratação...", "blue")

            url = (
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets.json'
            f'?auth={self.token_id}&orderBy="key"&equalTo="{self.local_id}"'
            )
            
            UrlRequest(
                url,
                on_success=self.handle_successful_deletion,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )
            
        except Exception as e:
            print(f"Erro ao processar recrutamento: {str(e)}")
            self._show_snackbar(f"Erro no processo: {str(e)}", "red")


    def handle_successful_deletion(self, req, result):
        """
        Callback de sucesso para a exclusão da requisição.

        Confirma que o processo de contratação foi finalizado com sucesso.

        Args:
            req: Objeto da requisição HTTP.
            result: Resultado da exclusão (geralmente vazio para DELETE).
        """
        print('Resultado da exclusão: ', result)
        id_ = ''
        key_send = []
        for key, dic in result.items():
            id_ = str(key)
            key_send = ast.literal_eval(dic['requests'])
        
        key_send.remove(self.key_contractor)
        id_.replace('-', '')
        data = {
            'requests': f'{key_send}'
        }
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets/{id_}.json?auth={self.token_id}'
        print('Os dados sem a key do usuario são: ', key_send)
        UrlRequest(
            url,
            method='PATCH',
            req_body=json.dumps(data),
            on_success=self.skyfall
        )
    
    def skyfall(self, req, result):
        """Busca dados do funcionário para atualizar receiveds"""
        print('✅ Requisição removida com sucesso')
        url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}.json?auth={self.token_id}'
        UrlRequest(
            url,
            on_success=self.skyfall2,
            on_error=self.on_error,
            on_failure=self.on_failure
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
            
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}.json?auth={self.token_id}'
            print('📤 Atualizando receiveds finais: ', key_send)
            
            UrlRequest(
                url,
                method='PATCH',
                req_body=json.dumps(data),
                on_success=self.finalize_hiring,  # ✅ Nova função - NÃO chama skyfall de novo!
                on_error=self.on_error,
                on_failure=self.on_failure
            )
        except Exception as e:
            print(f'❌ Erro no skyfall2: {e}')
            self._show_snackbar(f"Erro ao finalizar: {str(e)}", "red")
            # Mesmo com erro, navega de volta
            self._navigate_back_with_reload()

    def finalize_hiring(self, req, result):
        """Finaliza o processo de contratação com sucesso"""
        print('✅ Processo de contratação finalizado completamente!')
        self._show_snackbar("Contratação concluída com sucesso!", "green")
        
        # Agora sim, navega de volta COM reload dos dados
        self._navigate_back_with_reload()

    def reject_candidate(self):
        """
        Desvincula o funcionário do contratante atual sem aceitá-lo na equipe.

        Inicia o processo de recusa da solicitação de contratação,
        mantendo o funcionário disponível para outros contratantes.
        """
        try:
            url = f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}/.json?auth={self.token_id}'

            self._show_snackbar("Processando recusa...", "blue")

            UrlRequest(
                url,
                on_success=self.update_employee_data_after_rejection,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao dispensar funcionário: {str(e)}")
            self._show_snackbar(f"Erro ao recusar: {str(e)}", "red")

    def update_employee_data_after_rejection(self, req, result):
        """ Após obter os dados do funcionário, remove o contratante da lista de recebidos. """
        try:
            print('Dados do funcionário: ', result)

            # Se não há dados ou campo 'receiveds' não existe
            if not result or 'receiveds' not in result:
                print("Dados do funcionário inválidos ou incompletos")
                self._show_snackbar("Erro: dados do funcionário não encontrados", "red")
                return

            # Converte a string de lista para lista Python
            try:
                rk = ast.literal_eval(result['receiveds'])

                # Remove o contratante da lista
                if self.key_contractor in rk:
                    rk.remove(self.key_contractor)

                data = {
                    'contractor': '',
                    'receiveds': f"{rk}"
                }

                # Atualiza os dados do funcionário
                UrlRequest(
                    f'https://obra-7ebd9-default-rtdb.firebaseio.com/Funcionarios/{self.local_id}/.json?auth={self.token_id}',
                    req_body=json.dumps(data),
                    method='PATCH',
                    on_success=self.fetch_requests_after_rejection,
                    on_error=self.on_error,
                    on_failure=self.on_failure,
                    timeout=10
                )
            except (SyntaxError, ValueError) as e:
                print(f"Erro ao processar lista 'receiveds': {str(e)}")
                self._show_snackbar("Erro ao processar dados", "red")

        except Exception as e:
            print(f"Erro ao processar próxima etapa: {str(e)}")
            self._show_snackbar(f"Erro no processamento: {str(e)}", "red")

    def fetch_requests_after_rejection(self, req, result):
        """
        Após atualizar os dados do funcionário, busca as requisições para ajustar a lista de recusa.

        Args:
            req: Objeto da requisição HTTP.
            result: Resultado da atualização (geralmente os dados atualizados).
        """

        try:
            url = (
            f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets.json'
            f'?auth={self.token_id}&orderBy="key"&equalTo="{self.local_id}"'
            )

            UrlRequest(
                url,
                on_success=self.process_candidate_rejection,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )
        except Exception as e:
            print(f"Erro ao buscar requisições: {str(e)}")
            self._show_snackbar(f"Erro ao finalizar recusa: {str(e)}", "red")

    def process_after_hiring(self, req, result):
        """
        Após criar o chat, inicia a remoção da requisição
        NÃO navega ainda - só no final!
        """
        try:
            self._show_snackbar("Finalizando processo de contratação...", "blue")

            url = (
                f'https://obra-7ebd9-default-rtdb.firebaseio.com/requets.json'
                f'?auth={self.token_id}&orderBy="key"&equalTo="{self.local_id}"'
            )
            
            UrlRequest(
                url,
                on_success=self.handle_successful_deletion,
                on_error=self.on_error,
                on_failure=self.on_failure,
                timeout=10
            )
            
            # ❌ REMOVIDO: Não navega mais aqui!
            # A navegação só acontece no finalize_hiring()
                
        except Exception as e:
            print(f"Erro ao processar recrutamento: {str(e)}")
            self._show_snackbar(f"Erro no processo: {str(e)}", "red")

  
    def _navigate_back(self):
        """
        Método auxiliar para navegar de volta à tela de requisições,
        garantindo que a requisição processada seja removida da lista.
        """
        app = MDApp.get_running_app()
        screenmanager = app.root
        request_screen = screenmanager.get_screen('RequestsVacancy')

        # Atualiza os dados do request_screen
        request_screen.key = self.key
        request_screen.data_contractor = self.data_contractor
        request_screen.contractor = ''
        request_screen.api_key = self.api_key
        request_screen.local_id = self.local_id
        request_screen.refresh_token = self.refresh_token
        request_screen.token_id = self.token_id

        # ✅ SOLUÇÃO: Força reload completo dos dados
        request_screen.ids.main_scroll.clear_widgets()
        request_screen._request_count = 0
        
        # Navega primeiro
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'RequestsVacancy'
        
        # ✅ Recarrega os dados após a navegação
        if request_screen.tab_nav_state == 'received':
            request_screen.receiveds()
        else:
            request_screen.upload_requests()


    def _navigate_back_with_reload(self):
        """
        Navega de volta e FORÇA o reload dos dados do Firebase
        """
        try:
            from kivy.clock import Clock
            
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

            # ✅ SOLUÇÃO: Limpa a tela ANTES de navegar
            request_screen.ids.main_scroll.clear_widgets()
            request_screen._request_count = 0

            # Navega para a tela
            screenmanager.transition = SlideTransition(direction='left')
            screenmanager.current = 'RequestsVacancy'
            
            # ✅ CRITICAL: Agenda o reload para DEPOIS da navegação
            # Isso garante que a tela está visível quando recarregar
            def reload_data(dt):
                if request_screen.tab_nav_state == 'received':
                    print('🔄 Recarregando receiveds...')
                    request_screen.receiveds()
                else:
                    print('🔄 Recarregando requests...')
                    request_screen.upload_requests()
            
            Clock.schedule_once(reload_data, 0.3)  # Aguarda 0.3s para garantir
            
        except Exception as e:
            print(f"❌ Erro ao navegar: {e}")
            self._show_snackbar(f"Erro na navegação: {str(e)}", "red")
        
    def _navigate_back_two(self, *args):
        """
        Mesmo que _navigate_back, mas preserva o nome do contratante selecionado.
        """
        app = MDApp.get_running_app()
        screenmanager = app.root
        request_screen = screenmanager.get_screen('RequestsVacancy')

        request_screen.key = self.key
        request_screen.data_contractor = self.data_contractor
        request_screen.contractor = self.contractor
        request_screen.api_key = self.api_key
        request_screen.local_id = self.local_id
        request_screen.refresh_token = self.refresh_token
        request_screen.token_id = self.token_id

        # ✅ SOLUÇÃO: Força reload completo dos dados
        request_screen.ids.main_scroll.clear_widgets()
        request_screen._request_count = 0

        # Navega primeiro
        screenmanager.transition = SlideTransition(direction='left')
        screenmanager.current = 'RequestsVacancy'
        
        # ✅ Recarrega os dados após a navegação
        if request_screen.tab_nav_state == 'received':
            request_screen.receiveds()
        else:
            request_screen.upload_requests()


    def handle_successful_rejection(self, req, result):
        """
        Conclui a recusa do contratante com sucesso
        """
        print('✅ Recusa finalizada com sucesso')
        self._show_snackbar("Contratante dispensado com sucesso", "green")
        
        # Navega de volta COM reload
        self._navigate_back_with_reload()


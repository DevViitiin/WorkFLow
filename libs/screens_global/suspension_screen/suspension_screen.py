from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from datetime import datetime 
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.widget import Widget
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.divider import MDDivider
from kivymd.uix.list import (
    MDListItem,
    MDListItemLeadingIcon,
    MDListItemSupportingText,
)


class SuspensionScreen(MDScreen):
    motive = StringProperty()
    init = StringProperty()
    end = StringProperty()
    days = StringProperty()
    
    def __init__(self, dados=None, **kwargs):
        super().__init__(**kwargs)
        if dados:
            self.motive = dados.get('motive', '')
            self.init = dados.get('init', '')
            self.end = dados.get('end', '')

    
    def on_enter(self):
        """Vou carregar os dados dessas variaveis na tela de suspensão"""
        self.ids.motive.text = f"{self.motive}"
        self.ids.init.text = f"{self.init}"
        self.ids.end.text = f"{self.end}"
        days = self.days()
        self.ids.days.text = f'Faltam {days} dias para o término'
    
    def days(self):
        """Calcular quantos dias faltam para o fim do prazo"""
        # Converter string para objeto datetime
        formato = "%d/%m/%Y"  # dia/mês/ano
        data_init = datetime.strptime(self.init, formato)
        data_end = datetime.strptime(self.end, formato)

        # Pegar a data atual
        hoje = datetime.today()

        # Calcular diferença
        dias_faltando = (data_end - hoje).days + 1

        # Evitar negativo (pra quando já passou do prazo)
        if dias_faltando < 0:
            dias_faltando = 0

        print(f"Faltam {dias_faltando} dias para o fim do prazo.")
        return dias_faltando

    def dialog_email(self):
        """Cria e abre um dialog com o email de contato do suporte"""
        MDDialog(
            # -----------------------Headline text-------------------------
            MDDialogHeadlineText(
                text="Formas de contato",
                halign='left',
                pos_hint={'center_x': 0.5}
            ),
            # -----------------------Supporting text-----------------------
            MDDialogSupportingText(
                text="Precisa de ajuda? Nossa equipe de suporte está disponível para você. Entre em contato pelos canais abaixo:"
            ),
            # -----------------------Custom content------------------------
            MDDialogContentContainer(   
                MDDivider(),
                MDListItem(
                    MDListItemLeadingIcon(
                        icon="gmail",
                    ),
                    MDListItemSupportingText(
                        text="suportemaodeobra@gmail.com",
                    ),
                    theme_bg_color="Custom",
                    md_bg_color=self.theme_cls.transparentColor,
                ),
                MDListItem(
                    MDListItemLeadingIcon(
                        icon="phone",
                    ),
                    MDListItemSupportingText(
                        text="(62) 9299-7127",
                    ),
                    theme_bg_color="Custom",
                    md_bg_color=self.theme_cls.transparentColor,
                ),
                MDDivider(),
                orientation="vertical",
            ),
        ).open()
    
    def back_screen(self, *args):
        self.manager.current = 'Init'   
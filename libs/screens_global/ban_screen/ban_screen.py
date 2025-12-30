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
from kivymd.app import MDApp

class BanScreen(MDScreen):
    motive = StringProperty()
    description = StringProperty()
    
    def on_enter(self, *args):
        """Colocando os dados na tela rsrsrsrsrsrsrsr"""
        self.ids.motive.text = self.motive
        self.ids.description.text = self.description
        
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
        
    def out_app(self, *args):
        app = MDApp.get_running_app()
        app.stop()
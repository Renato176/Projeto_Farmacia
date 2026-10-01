import reflex as rx
import httpx

# URL base da API do Xano
XANO_API_URL: str = "https://x8ki-letl-twmt.n7.xano.io/api:VzEWcgd6"

# Cores do tema da aplicação (Padrão Farmácia Saúde+)
COLOR_BG_DARK = "#0b0f17"
COLOR_CARD_BG = "rgba(20, 26, 38, 0.85)"
COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_INPUT_BG = "rgba(255, 255, 255, 0.05)"
COLOR_TEXT_PRIMARY = "#f5f7fa"
COLOR_TEXT_SECONDARY = "#9aa3b2"
COLOR_ACCENT = "#22d3ee"
COLOR_ACCENT_2 = "#3b82f6"


class ForgotPasswordState(rx.State):
    email: str = ""
    message: str = ""
    is_success: bool = False
    is_loading: bool = False

    def set_email(self, value: str):
        self.email = value

    async def handle_recover(self):
        self.is_loading = True
        self.message = ""
        self.is_success = False

        if not self.email:
            self.message = "Por favor, insira o seu e-mail."
            self.is_loading = False
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{XANO_API_URL}/authqpassword-reset",
                    json={"email": self.email},
                    timeout=10.0
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    self.is_success = True
                    self.message = data.get("message", "Instruções enviadas com sucesso.")
                    
                    # Aguarda um breve momento para o utilizador ver a mensagem e redireciona para a tela de redefinição
                    return rx.redirect("/redefinir-senha")
                else:
                    data = response.json()
                    self.message = data.get("message", "Não foi possível processar o pedido.")
        except httpx.RequestError:
            self.message = "Erro de conexão com o servidor."
        except Exception:
            self.message = "Ocorreu um erro interno."
        finally:
            self.is_loading = False


def forgot_password_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text("Recuperar Palavra-passe", color=COLOR_TEXT_PRIMARY, font_size="1.2em", font_weight="700"),
            rx.text("Insira o seu e-mail para receber as instruções de recuperação.", color=COLOR_TEXT_SECONDARY, font_size="0.85em"),
            align_items="start",
            spacing="1",
            width="100%",
            margin_bottom="1.5em",
        ),
        rx.cond(
            ForgotPasswordState.message != "",
            rx.text(
                ForgotPasswordState.message,
                color=rx.cond(ForgotPasswordState.is_success, "#22c55e", "#ef4444"),
                font_size="0.85em",
                margin_bottom="0.5em"
            )
        ),
        rx.hstack(
            rx.icon("mail", size=18, color=COLOR_TEXT_SECONDARY),
            rx.input(
                placeholder="exemplo@email.com",
                on_change=ForgotPasswordState.set_email,
                width="100%",
                border="none",
                background="transparent",
            ),
            width="100%",
            padding="0.5em 1em",
            background=COLOR_INPUT_BG,
            border="1px solid",
            border_color=COLOR_BORDER,
            border_radius="12px",
            spacing="3",
            align_items="center",
        ),
        rx.button(
            "Enviar Instruções",
            on_click=ForgotPasswordState.handle_recover,
            loading=ForgotPasswordState.is_loading,
            width="100%",
            padding="1.2em 0",
            border_radius="12px",
            background=f"linear-gradient(90deg, {COLOR_ACCENT_2}, {COLOR_ACCENT})",
            color="white",
            cursor="pointer",
        ),
        rx.link("Voltar para o Login", href="/", color=COLOR_ACCENT, font_size="0.85em", text_align="center"),
        width="100%",
        spacing="4",
        padding="2em",
        background=COLOR_CARD_BG,
        border="1px solid",
        border_color=COLOR_BORDER,
        border_radius="20px",
        box_shadow="0 20px 60px rgba(0, 0, 0, 0.4)",
    )


def forgot_password_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                forgot_password_form(),
                width="100%",
                max_width="380px",
                align_items="center",
            ),
            width="100%",
            min_height="100vh",
            padding="2em 1.2em",
        ),
        width="100%",
        min_height="100vh",
        background=f"radial-gradient(circle at 50% 0%, #1a2233 0%, {COLOR_BG_DARK} 60%)",
    )
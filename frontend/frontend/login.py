import reflex as rx
import httpx

XANO_API_URL: str = "https://x8ki-letl-twmt.n7.xano.io/api:Nq0yy-QT"

COLOR_BG_DARK = "#0b0f17"
COLOR_CARD_BG = "rgba(20, 26, 38, 0.85)"
COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_INPUT_BG = "rgba(255, 255, 255, 0.05)"
COLOR_TEXT_PRIMARY = "#f5f7fa"
COLOR_TEXT_SECONDARY = "#9aa3b2"
COLOR_ACCENT = "#22d3ee"
COLOR_ACCENT_2 = "#3b82f6"


class LoginState(rx.State):
    email: str = ""
    password: str = ""
    show_password: bool = False
    remember_me: bool = True
    error_message: str = ""
    is_loading: bool = False

    def toggle_show_password(self):
        self.show_password = not self.show_password

    def set_email(self, value: str):
        self.email = value

    def set_password(self, value: str):
        self.password = value

    async def handle_login(self):
        self.is_loading = True
        self.error_message = ""

        if not self.email or not self.password:
            self.error_message = "Por favor, preencha todos os campos."
            self.is_loading = False
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{XANO_API_URL}/anonimo/auth/login",
                    json={
                        "email": self.email,
                        "password": self.password
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    return rx.redirect("/dashboard")
                elif response.status_code == 401:
                    self.error_message = "E-mail ou senha incorretos."
                else:
                    self.error_message = "Erro ao conectar com o servidor. Tente novamente."

        except httpx.RequestError:
            self.error_message = "Não foi possível alcançar o servidor de autenticação."
        except Exception as e:
            print(f"Erro inesperado: {e}")
            self.error_message = "Ocorreu um erro interno."
        finally:
            self.is_loading = False


def logo() -> rx.Component:
    return rx.box(
        rx.icon("plus", size=30, color="white", stroke_width=2.5),
        position="relative",
        display="flex",
        align_items="center",
        justify_content="center",
        width="72px",
        height="72px",
        border="2px solid",
        border_color=COLOR_ACCENT,
        border_radius="20px",
        background="rgba(34, 211, 238, 0.08)",
        margin_bottom="1em",
    )


def header() -> rx.Component:
    return rx.vstack(
        logo(),
        rx.hstack(
            rx.text("Farmácia", color=COLOR_TEXT_PRIMARY, font_size="1.6em", font_weight="700"),
            rx.text("Saúde+", color=COLOR_ACCENT, font_size="1.6em", font_weight="700"),
            spacing="2",
        ),
        rx.text(
            "Mais saúde para o seu dia a dia",
            color=COLOR_TEXT_SECONDARY,
            font_size="0.9em",
        ),
        align_items="center",
        spacing="1",
        margin_bottom="2em",
    )


def login_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Acesse sua conta",
                color=COLOR_TEXT_PRIMARY,
                font_size="1.2em",
                font_weight="700",
            ),
            rx.text(
                "Bem-vindo de volta! Entre com seu e-mail para continuar.",
                color=COLOR_TEXT_SECONDARY,
                font_size="0.85em",
                text_align="left",
            ),
            align_items="start",
            spacing="1",
            width="100%",
            margin_bottom="1.5em",
        ),
        rx.cond(
            LoginState.error_message != "",
            rx.text(LoginState.error_message, color="#ef4444", font_size="0.85em", margin_bottom="0.5em")
        ),
        rx.hstack(
            rx.icon("user", size=18, color=COLOR_TEXT_SECONDARY),
            rx.input(
                placeholder="exemplo@email.com",
                on_change=LoginState.set_email,
                width="100%",
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
        rx.hstack(
            rx.icon("lock", size=18, color=COLOR_TEXT_SECONDARY),
            rx.input(
                placeholder="••••••••",
                on_change=LoginState.set_password,
                type="password",
                width="100%",
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
            "Entrar",
            on_click=LoginState.handle_login,
            loading=LoginState.is_loading,
            width="100%",
            padding="1.2em 0",
            border_radius="12px",
            background=f"linear-gradient(90deg, {COLOR_ACCENT_2}, {COLOR_ACCENT})",
            color="white",
            cursor="pointer",
        ),
        width="100%",
        spacing="4",
        padding="2em",
        background=COLOR_CARD_BG,
        border="1px solid",
        border_color=COLOR_BORDER,
        border_radius="20px",
        box_shadow="0 20px 60px rgba(0, 0, 0, 0.4)",
    )


def login_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                header(),
                login_form(),
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
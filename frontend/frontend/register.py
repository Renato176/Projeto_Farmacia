import reflex as rx
import httpx

XANO_API_URL: str = "https://x8ki-letl-twmt.n7.xano.io/api:VzEWcgd6"

COLOR_BG_DARK = "#0b0f17"
COLOR_CARD_BG = "rgba(20, 26, 38, 0.85)"
COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_INPUT_BG = "rgba(255, 255, 255, 0.05)"
COLOR_TEXT_PRIMARY = "#f5f7fa"
COLOR_TEXT_SECONDARY = "#9aa3b2"
COLOR_ACCENT = "#22d3ee"
COLOR_ACCENT_2 = "#3b82f6"


class RegisterState(rx.State):
    name: str = ""
    email: str = ""
    password: str = ""
    show_password: bool = False
    error_message: str = ""
    is_loading: bool = False

    def toggle_show_password(self):
        self.show_password = not self.show_password

    def set_name(self, value: str):
        self.name = value

    def set_email(self, value: str):
        self.email = value

    def set_password(self, value: str):
        self.password = value

    async def handle_register(self):
        self.is_loading = True
        self.error_message = ""

        if not self.name or not self.email or not self.password:
            self.error_message = "Por favor, preencha todos os campos."
            self.is_loading = False
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{XANO_API_URL}/auth/login",
                    json={
                        "name": self.name,
                        "email": self.email,
                        "password": self.password
                    },
                    timeout=10.0
                )

                if response.status_code in [200, 201]:
                    return rx.redirect("/")
                else:
                    data = response.json()
                    self.error_message = data.get("message", "Erro ao criar conta. Tente novamente.")

        except httpx.RequestError:
            self.error_message = "Não foi possível conectar ao servidor."
        except Exception as e:
            print(f"Erro inesperado: {e}")
            self.error_message = "Ocorreu um erro interno."
        finally:
            self.is_loading = False


def register_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text("Criar Nova Conta", color=COLOR_TEXT_PRIMARY, font_size="1.2em", font_weight="700"),
            rx.text("Preencha os dados abaixo para começar.", color=COLOR_TEXT_SECONDARY, font_size="0.85em"),
            align_items="start",
            spacing="1",
            width="100%",
            margin_bottom="1.5em",
        ),
        rx.cond(
            RegisterState.error_message != "",
            rx.text(RegisterState.error_message, color="#ef4444", font_size="0.85em", margin_bottom="0.5em")
        ),
        rx.hstack(
            rx.icon("user", size=18, color=COLOR_TEXT_SECONDARY),
            rx.input(
                placeholder="Nome completo",
                on_change=RegisterState.set_name,
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
        rx.hstack(
            rx.icon("mail", size=18, color=COLOR_TEXT_SECONDARY),
            rx.input(
                placeholder="exemplo@email.com",
                on_change=RegisterState.set_email,
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
        rx.hstack(
            rx.icon("lock", size=18, color=COLOR_TEXT_SECONDARY),
            rx.input(
                placeholder="••••••••",
                on_change=RegisterState.set_password,
                type=rx.cond(RegisterState.show_password, "text", "password"),
                width="100%",
                border="none",
                background="transparent",
            ),
            rx.icon(
                tag=rx.cond(RegisterState.show_password, "eye-off", "eye"),
                size=18,
                color=COLOR_TEXT_SECONDARY,
                cursor="pointer",
                on_click=RegisterState.toggle_show_password,
                _hover={"color": COLOR_ACCENT},
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
            "Cadastrar",
            on_click=RegisterState.handle_register,
            loading=RegisterState.is_loading,
            width="100%",
            padding="1.2em 0",
            border_radius="12px",
            background=f"linear-gradient(90deg, {COLOR_ACCENT_2}, {COLOR_ACCENT})",
            color="white",
            cursor="pointer",
        ),
        rx.link("Já tem uma conta? Faça login", href="/", color=COLOR_ACCENT, font_size="0.85em", text_align="center"),
        width="100%",
        spacing="4",
        padding="2em",
        background=COLOR_CARD_BG,
        border="1px solid",
        border_color=COLOR_BORDER,
        border_radius="20px",
        box_shadow="0 20px 60px rgba(0, 0, 0, 0.4)",
    )


def register_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                register_form(),
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
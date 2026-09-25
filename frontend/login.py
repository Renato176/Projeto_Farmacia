import reflex as rx
import httpx  # Utilizado para chamadas assíncronas ao Xano

class LoginState(rx.State):
    """Estado responsável pela lógica da tela de login."""
    
    email: str = ""
    password: str = ""
    error_message: str = ""
    is_loading: bool = False
    
    # URL base do Xano
    XANO_API_URL: str = "https://x8ki-letl-twmt.n7.xano.io/api:Nq0yy-QT"

    # Métodos explícitos para atualizar os campos de input
    def set_email(self, value: str):
        self.email = value

    def set_password(self, value: str):
        self.password = value

    async def handle_login(self):
        """
        Envia as credenciais para o back-end (Xano) e trata a resposta.
        """
        self.is_loading = True
        self.error_message = ""

        # Validação básica de front-end
        if not self.email or not self.password:
            self.error_message = "Por favor, preencha todos os campos."
            self.is_loading = False
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.XANO_API_URL}/auth/login",
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

    def clear_error(self):
        self.error_message = ""


def login_card() -> rx.Component:
    """Componente visual do card de login."""
    return rx.vstack(
        rx.heading("Farmácia Anônima", size="8", margin_bottom="0.5em"),
        rx.text("Faça login para acessar o sistema", color_scheme="gray"),
        
        rx.vstack(
            rx.text("E-mail", font_weight="bold", size="2"),
            rx.input(
                placeholder="exemplo@email.com",
                on_blur=LoginState.set_email,
                size="3",
                width="100%",
            ),
            align_items="start",
            width="100%",
        ),
        
        rx.vstack(
            rx.text("Senha", font_weight="bold", size="2"),
            rx.input(
                placeholder="••••••••",
                type="password",
                on_blur=LoginState.set_password,
                size="3",
                width="100%",
            ),
            align_items="start",
            width="100%",
        ),

        # Exibição de erro condicional
        rx.cond(
            LoginState.error_message != "",
            rx.callout(
                LoginState.error_message,
                icon="info",
                color_scheme="red",
                variant="soft",
                width="100%",
            ),
        ),

        rx.button(
            "Entrar",
            on_click=LoginState.handle_login,
            loading=LoginState.is_loading,
            width="100%",
            size="3",
            color_scheme="blue",
            margin_top="1em",
        ),
        
        spacing="4",
        padding="2em",
        width="100%",
        max_width="400px",
        border="1px solid #EAEAEA",
        border_radius="lg",
        box_shadow="lg",
        background_color="white",
    )


def login_page() -> rx.Component:
    """Página principal de login."""
    return rx.center(
        rx.vstack(
            login_card(),
            spacing="4",
        ),
        width="100vw",
        height="100vh",
        background_color="#F4F4F5",
    )
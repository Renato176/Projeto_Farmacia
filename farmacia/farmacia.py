"""DROGA-NONIMO pharmacy application."""

import asyncio
import logging
from typing import Any

import httpx
import reflex as rx

from farmacia import xano

COLOR_BG_DARK = "#0b0f17"
COLOR_CARD_BG = "rgba(20, 26, 38, 0.92)"
COLOR_BORDER = "rgba(255, 255, 255, 0.10)"
COLOR_INPUT_BG = "rgba(255, 255, 255, 0.05)"
COLOR_TEXT_PRIMARY = "#f5f7fa"
COLOR_TEXT_SECONDARY = "#9aa3b2"
COLOR_ACCENT = "#22d3ee"
COLOR_ACCENT_2 = "#3b82f6"

logger = logging.getLogger(__name__)


class LoginState(rx.State):
    email: str = ""
    _password: str = ""
    _auth_token: str = ""
    register_name: str = ""
    register_email: str = ""
    _register_password: str = ""
    show_password: bool = False
    remember_me: bool = True
    error_message: str = ""
    register_error_message: str = ""
    is_loading: bool = False
    is_registering: bool = False
    products: list[dict[str, Any]] = []
    customers: list[dict[str, Any]] = []
    sales: list[dict[str, Any]] = []
    cart: list[dict[str, Any]] = []
    product_search: str = ""
    low_stock_only: bool = False
    product_name: str = ""
    product_barcode: str = ""
    product_price: str = ""
    product_stock: str = ""
    editing_product_id: int = 0
    stock_error: str = ""
    stock_notice: str = ""
    is_loading_products: bool = False
    is_saving_product: bool = False
    sales_error: str = ""
    is_loading_sales: bool = False
    payment_method: str = "pix"
    selected_customer: str = ""

    @rx.event
    def toggle_show_password(self):
        self.show_password = not self.show_password

    @rx.event
    def set_email(self, value: str):
        self.email = value

    @rx.event
    def set_password(self, value: str):
        self._password = value

    @rx.event
    def set_remember_me(self, value: bool):
        self.remember_me = value

    @rx.event
    def set_register_name(self, value: str):
        self.register_name = value

    @rx.event
    def set_register_email(self, value: str):
        self.register_email = value

    @rx.event
    def set_register_password(self, value: str):
        self._register_password = value

    @rx.event
    def clear_login_message(self):
        self.error_message = ""
        self.is_loading = False
        self._password = ""

    @rx.event
    def clear_register_message(self):
        self.register_error_message = ""
        self.is_registering = False

    @rx.event
    async def handle_login(self):
        self.is_loading = True
        self.error_message = ""

        if not self.email.strip() or not self._password:
            self.error_message = "Por favor, preencha seu e-mail e sua senha."
            self.is_loading = False
            return

        try:
            response = await xano.request(
                "POST",
                "/auth/login",
                payload={
                    "email": self.email.strip(),
                    "password": self._password,
                },
            )

            if response.status_code == 200:
                response_data = xano.response_data(response)
                token = xano.auth_token(response_data)
                if not token:
                    self.error_message = xano.response_message(
                        response_data,
                        "O servidor não retornou um token de acesso válido.",
                    )
                    return

                self._auth_token = token
                return rx.redirect("/splash")

            response_data = xano.response_data(response)
            fallback = (
                "E-mail ou senha incorretos."
                if response.status_code == 401
                else "Não foi possível entrar. Tente novamente em instantes."
            )
            self.error_message = xano.response_message(
                response_data,
                fallback,
            )
        except httpx.RequestError:
            logger.warning("A requisicao de login para o Xano falhou.")
            self.error_message = (
                "Não foi possível alcançar o servidor de autenticação."
            )
        finally:
            self.is_loading = False

    @rx.event
    async def handle_register(self):
        self.is_registering = True
        self.register_error_message = ""

        name = self.register_name.strip()
        email = self.register_email.strip()
        if not name or not email or not self._register_password:
            self.register_error_message = "Por favor, preencha todos os campos."
            self.is_registering = False
            return

        try:
            response = await xano.request(
                "POST",
                "/auth/signup",
                payload={
                    "name": name,
                    "email": email,
                    "password": self._register_password,
                },
            )
            response_data = xano.response_data(response)
            if response.status_code not in (200, 201):
                self.register_error_message = xano.response_message(
                    response_data,
                    "Não foi possível criar a conta. Confira os dados e tente novamente.",
                )
                return

            token = xano.auth_token(response_data)
            if not token:
                self.register_error_message = xano.response_message(
                    response_data,
                    "A conta foi criada, mas o Xano não retornou um token de acesso.",
                )
                return

            self._auth_token = token
            self.email = email
            self._register_password = ""
            return rx.redirect("/splash")
        except httpx.RequestError:
            logger.warning("A requisicao de cadastro para o Xano falhou.")
            self.register_error_message = (
                "Não foi possível conectar ao servidor. Tente novamente mais tarde."
            )
        finally:
            self.is_registering = False

    @rx.event
    def require_login(self):
        if not self._auth_token:
            return rx.redirect("/")

    @rx.event
    def logout(self):
        self._auth_token = ""
        self.email = ""
        self._password = ""
        self._register_password = ""
        self.products = []
        self.customers = []
        self.sales = []
        self.cart = []
        return rx.redirect("/")

    @rx.var
    def filtered_products(self) -> list[dict[str, Any]]:
        query = self.product_search.strip().casefold()
        return [
            product
            for product in self.products
            if (
                not query
                or query in str(product.get("nome", "")).casefold()
                or query in str(product.get("codigo_barras", "")).casefold()
            )
            and (
                not self.low_stock_only
                or self._stock_quantity(product) <= 5
            )
        ]

    @rx.var
    def low_stock_count(self) -> int:
        return sum(self._stock_quantity(product) <= 5 for product in self.products)

    @rx.var
    def cart_total(self) -> float:
        return sum(
            float(item["preco"]) * int(item["quantidade"])
            for item in self.cart
        )

    @rx.var
    def cart_item_count(self) -> int:
        return sum(int(item["quantidade"]) for item in self.cart)

    @rx.var
    def customer_names(self) -> list[str]:
        return [
            str(customer.get("nome", ""))
            for customer in self.customers
            if customer.get("nome")
        ]

    @staticmethod
    def _stock_quantity(product: dict[str, Any]) -> int:
        try:
            return int(product.get("estoque_quantidade", 0))
        except (TypeError, ValueError):
            return 0

    async def _load_products(self) -> bool:
        response = await xano.request(
            "GET",
            "/produto",
            auth_token=self._auth_token,
            base_url=xano.XANO_PHARMACY_API_URL,
        )
        if response.status_code != 200:
            self.stock_error = xano.response_message(
                xano.response_data(response),
                f"Não foi possível carregar os produtos (HTTP {response.status_code}).",
            )
            return False
        try:
            self.products = xano.response_records(
                xano.response_data(response),
                "produtos",
            )
        except ValueError:
            logger.error("O endpoint /produto retornou dados fora do formato esperado.")
            self.stock_error = "O Xano retornou uma lista de produtos inválida."
            return False
        return True

    @rx.event
    async def load_stock(self):
        if not self._auth_token:
            return rx.redirect("/")

        self.is_loading_products = True
        self.stock_error = ""
        try:
            await self._load_products()
        except httpx.RequestError:
            logger.warning("A consulta de produtos no Xano falhou.")
            self.stock_error = "Não foi possível conectar ao estoque no Xano."
        finally:
            self.is_loading_products = False

    @rx.event
    def set_product_search(self, value: str):
        self.product_search = value

    @rx.event
    def toggle_low_stock_filter(self):
        self.low_stock_only = not self.low_stock_only

    @rx.event
    def set_product_name(self, value: str):
        self.product_name = value

    @rx.event
    def set_product_barcode(self, value: str):
        self.product_barcode = value

    @rx.event
    def set_product_price(self, value: str):
        self.product_price = value

    @rx.event
    def set_product_stock(self, value: str):
        self.product_stock = value

    @rx.event
    def start_product_edit(
        self,
        product_id: int,
        name: str,
        barcode: str,
        price: float,
        stock: int,
    ):
        self.editing_product_id = product_id
        self.product_name = name
        self.product_barcode = barcode
        self.product_price = str(price)
        self.product_stock = str(stock)
        self.stock_notice = ""
        self.stock_error = ""

    @rx.event
    def cancel_product_edit(self):
        self.editing_product_id = 0
        self.product_name = ""
        self.product_barcode = ""
        self.product_price = ""
        self.product_stock = ""
        self.stock_notice = ""

    @rx.event
    async def save_product(self):
        if not self._auth_token:
            return rx.redirect("/")

        name = self.product_name.strip()
        barcode = self.product_barcode.strip()
        if not name or not barcode:
            self.stock_error = "Informe o nome e o código de barras do produto."
            return

        try:
            price = float(self.product_price.replace(",", "."))
            stock = int(self.product_stock)
        except ValueError:
            self.stock_error = "Preço e quantidade devem ser números válidos."
            return
        if price < 0 or stock < 0:
            self.stock_error = "Preço e quantidade não podem ser negativos."
            return

        payload: dict[str, Any] = {
            "nome": name,
            "codigo_barras": barcode,
            "preco": price,
            "estoque_quantidade": stock,
        }
        endpoint = (
            f"/produto/{self.editing_product_id}"
            if self.editing_product_id
            else "/produto"
        )
        method = "PUT" if self.editing_product_id else "POST"

        self.is_saving_product = True
        self.stock_error = ""
        self.stock_notice = ""
        try:
            response = await xano.request(
                method,
                endpoint,
                payload=payload,
                auth_token=self._auth_token,
                base_url=xano.XANO_PHARMACY_API_URL,
            )
            if response.status_code not in (200, 201):
                self.stock_error = xano.response_message(
                    xano.response_data(response),
                    f"Não foi possível salvar o produto (HTTP {response.status_code}).",
                )
                return
            self.cancel_product_edit()
            self.stock_notice = "Produto salvo com sucesso."
            await self._load_products()
        except httpx.RequestError:
            logger.warning("A gravação de produto no Xano falhou.")
            self.stock_error = "Não foi possível conectar ao Xano para salvar."
        finally:
            self.is_saving_product = False

    @rx.event
    async def delete_product(self, product_id: int):
        if not self._auth_token:
            return rx.redirect("/")

        self.stock_error = ""
        self.stock_notice = ""
        try:
            response = await xano.request(
                "DELETE",
                f"/produto/{product_id}",
                auth_token=self._auth_token,
                base_url=xano.XANO_PHARMACY_API_URL,
            )
            if response.status_code not in (200, 204):
                self.stock_error = xano.response_message(
                    xano.response_data(response),
                    f"Não foi possível excluir o produto (HTTP {response.status_code}).",
                )
                return
            self.stock_notice = "Produto excluído."
            await self._load_products()
        except httpx.RequestError:
            logger.warning("A exclusão de produto no Xano falhou.")
            self.stock_error = "Não foi possível conectar ao Xano para excluir."

    @rx.event
    async def load_sales(self):
        if not self._auth_token:
            return rx.redirect("/")

        self.is_loading_sales = True
        self.sales_error = ""
        try:
            sales_response, products_response, customers_response = await asyncio.gather(
                xano.request(
                    "GET",
                    "/venda",
                    auth_token=self._auth_token,
                    base_url=xano.XANO_PHARMACY_API_URL,
                ),
                xano.request(
                    "GET",
                    "/produto",
                    auth_token=self._auth_token,
                    base_url=xano.XANO_PHARMACY_API_URL,
                ),
                xano.request(
                    "GET",
                    "/cliente",
                    auth_token=self._auth_token,
                    base_url=xano.XANO_PHARMACY_API_URL,
                ),
            )
            if sales_response.status_code != 200:
                self.sales_error = xano.response_message(
                    xano.response_data(sales_response),
                    f"Não foi possível carregar as vendas (HTTP {sales_response.status_code}).",
                )
                return
            if products_response.status_code != 200:
                self.sales_error = xano.response_message(
                    xano.response_data(products_response),
                    f"Não foi possível carregar o catálogo (HTTP {products_response.status_code}).",
                )
                return
            if customers_response.status_code != 200:
                self.sales_error = xano.response_message(
                    xano.response_data(customers_response),
                    f"Não foi possível carregar os clientes (HTTP {customers_response.status_code}).",
                )
                return

            self.sales = xano.response_records(
                xano.response_data(sales_response),
                "vendas",
            )
            self.products = xano.response_records(
                xano.response_data(products_response),
                "produtos",
            )
            self.customers = xano.response_records(
                xano.response_data(customers_response),
                "clientes",
            )
        except httpx.RequestError:
            logger.warning("A carga da tela de vendas no Xano falhou.")
            self.sales_error = "Não foi possível conectar às APIs de vendas do Xano."
        except ValueError:
            logger.error("Uma API de vendas retornou dados fora do formato esperado.")
            self.sales_error = "O Xano retornou dados inválidos para vendas."
        finally:
            self.is_loading_sales = False

    @rx.event
    def add_to_cart(self, product_id: int):
        product = next(
            (item for item in self.products if int(item.get("id", 0)) == product_id),
            None,
        )
        if product is None:
            self.sales_error = "Produto não encontrado no catálogo carregado."
            return

        stock = self._stock_quantity(product)
        existing = next(
            (item for item in self.cart if int(item["produto_id"]) == product_id),
            None,
        )
        if existing and int(existing["quantidade"]) >= stock:
            self.sales_error = "A quantidade no carrinho já atingiu o estoque disponível."
            return
        if not existing and stock < 1:
            self.sales_error = "Este produto está sem estoque."
            return

        self.sales_error = ""
        if existing:
            existing["quantidade"] = int(existing["quantidade"]) + 1
            self.cart = list(self.cart)
            return

        self.cart.append(
            {
                "produto_id": product_id,
                "nome": str(product.get("nome", "")),
                "preco": float(product.get("preco", 0)),
                "quantidade": 1,
                "estoque_quantidade": stock,
            }
        )

    @rx.event
    def change_cart_quantity(self, product_id: int, delta: int):
        for item in self.cart:
            if int(item["produto_id"]) != product_id:
                continue
            quantity = int(item["quantidade"]) + delta
            if quantity < 1:
                self.cart.remove(item)
            elif quantity <= int(item["estoque_quantidade"]):
                item["quantidade"] = quantity
            else:
                self.sales_error = "A quantidade solicitada supera o estoque disponível."
                return
            self.cart = list(self.cart)
            self.sales_error = ""
            return

    @rx.event
    def clear_cart(self):
        self.cart = []
        self.sales_error = ""

    @rx.event
    def set_payment_method(self, value: str):
        self.payment_method = value

    @rx.event
    def set_selected_customer(self, value: str):
        self.selected_customer = value


class SplashState(rx.State):
    @rx.event
    async def go_dashboard(self):
        await asyncio.sleep(1.5)
        return rx.redirect("/dashboard")


class ForgotPasswordState(rx.State):
    email: str = ""
    message: str = ""
    is_loading: bool = False

    @rx.event
    def set_email(self, value: str):
        self.email = value

    @rx.event
    def clear_message(self):
        self.message = ""
        self.is_loading = False

    @rx.event
    async def handle_recover(self):
        self.is_loading = True
        self.message = ""

        email = self.email.strip()
        if not email:
            self.message = "Por favor, insira o seu e-mail."
            self.is_loading = False
            return

        try:
            await xano.request(
                "GET",
                "/reset/request-reset-link",
                params={"email": email},
            )
        except httpx.RequestError:
            logger.warning("A solicitacao de link de redefinicao para o Xano falhou.")

        self.is_loading = False
        return rx.redirect(f"/redefinir-senha?email={email}")


class ResetPasswordState(rx.State):
    _reset_auth_token: str = ""
    _password: str = ""
    _confirm_password: str = ""
    show_password: bool = False
    message: str = ""
    is_success: bool = False
    is_link_verified: bool = False
    is_loading: bool = False

    @rx.event
    def set_password(self, value: str):
        self._password = value

    @rx.event
    def set_confirm_password(self, value: str):
        self._confirm_password = value

    @rx.event
    def toggle_show_password(self):
        self.show_password = not self.show_password

    @rx.event
    async def prepare_reset(self):
        if self._reset_auth_token:
            return

        self.message = ""
        self.is_success = False
        query = self.router.url.query_parameters
        magic_token = query.get("magic_token", "").strip()
        email = query.get("email", "").strip()

        if not email:
            self.message = "Informe um e-mail válido para redefinir a senha."
            return

        if magic_token:
            self.is_loading = True
            try:
                response = await xano.request(
                    "POST",
                    "/reset/magic-link-login",
                    payload={"magic_token": magic_token, "email": email},
                )
                response_data = xano.response_data(response)
                token = xano.auth_token(response_data)
                if response.status_code != 200 or not token:
                    self.message = xano.response_message(
                        response_data,
                        "Este link de redefinição é inválido ou expirou. Solicite um novo.",
                    )
                    return

                self._reset_auth_token = token
                self.is_link_verified = True
                self.message = ""
                return
            except httpx.RequestError:
                logger.warning("A validacao do link de redefinicao no Xano falhou.")
                self.message = (
                    "Não foi possível validar o link agora. Tente novamente."
                )
            finally:
                self.is_loading = False

        self.is_link_verified = True
        self.message = ""

    @rx.event
    async def handle_reset(self):
        self.message = ""
        self.is_success = False

        if not self._reset_auth_token:
            self.message = (
                "O link de redefinição não foi validado. Solicite um novo pelo e-mail."
            )
            return
        if not self._password or not self._confirm_password:
            self.message = "Por favor, preencha os dois campos de senha."
            return
        if self._password != self._confirm_password:
            self.message = "As senhas não coincidem."
            return

        self.is_loading = True
        try:
            response = await xano.request(
                "POST",
                "/reset/update_password",
                payload={
                    "password": self._password,
                    "confirm_password": self._confirm_password,
                },
                auth_token=self._reset_auth_token,
            )
            response_data = xano.response_data(response)
            if response.status_code in (200, 201):
                self.is_success = True
                self.message = xano.response_message(
                    response_data,
                    "Senha alterada com sucesso. Você já pode entrar com a nova senha.",
                )
                self._reset_auth_token = ""
                self.is_link_verified = False
                self._password = ""
                self._confirm_password = ""
                return

            self.message = xano.response_message(
                response_data,
                "Não foi possível alterar a senha. Solicite um novo link e tente novamente.",
            )
        except httpx.RequestError:
            logger.warning("A redefinicao de senha no Xano falhou.")
            self.message = (
                "Não foi possível conectar ao servidor para redefinir a senha."
            )
        finally:
            self.is_loading = False


def logo(size: str = "180px") -> rx.Component:
    return rx.image(
        src=rx.asset("droga-nonimo-logo.png"),
        alt="Logo da DROGA-NONIMO: cruz farmacêutica azul com símbolo de farmácia",
        width=size,
        height=size,
        object_fit="contain",
    )


def header() -> rx.Component:
    return rx.vstack(
        logo("200px"),
        rx.hstack(
            rx.text(
                "DROGA-",
                color=COLOR_TEXT_PRIMARY,
                font_size="1.45em",
                font_weight="800",
                letter_spacing="0.02em",
            ),
            rx.text(
                "NONIMO",
                color=COLOR_ACCENT,
                font_size="1.45em",
                font_weight="800",
                letter_spacing="0.02em",
            ),
            spacing="0",
            align_items="center",
        ),
        rx.text(
            "Cuidado e confiança em cada atendimento",
            color=COLOR_TEXT_SECONDARY,
            font_size="0.9em",
            text_align="center",
        ),
        align_items="center",
        spacing="1",
        margin_bottom="2em",
    )


def text_field(
    icon_name: str,
    placeholder: str,
    value: rx.Var,
    on_change,
    *,
    input_type: str = "text",
) -> rx.Component:
    return rx.hstack(
        rx.icon(icon_name, size=18, color=COLOR_TEXT_SECONDARY),
        rx.input(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            type=input_type,
            width="100%",
            border="none",
            outline="none",
            background="transparent",
            color=COLOR_TEXT_PRIMARY,
            _placeholder={"color": COLOR_TEXT_SECONDARY},
            aria_label=placeholder,
        ),
        width="100%",
        padding="0.65em 1em",
        background=COLOR_INPUT_BG,
        border=f"1px solid {COLOR_BORDER}",
        border_radius="12px",
        spacing="3",
        align_items="center",
    )


def password_field() -> rx.Component:
    return rx.hstack(
        rx.icon("lock-keyhole", size=18, color=COLOR_TEXT_SECONDARY),
        rx.input(
            placeholder="Sua senha",
            on_change=LoginState.set_password,
            type=rx.cond(LoginState.show_password, "text", "password"),
            width="100%",
            border="none",
            outline="none",
            background="transparent",
            color=COLOR_TEXT_PRIMARY,
            _placeholder={"color": COLOR_TEXT_SECONDARY},
            aria_label="Sua senha",
        ),
        rx.icon(
            tag=rx.cond(LoginState.show_password, "eye-off", "eye"),
            size=18,
            color=COLOR_TEXT_SECONDARY,
            cursor="pointer",
            on_click=LoginState.toggle_show_password,
            _hover={"color": COLOR_ACCENT},
        ),
        width="100%",
        padding="0.65em 1em",
        background=COLOR_INPUT_BG,
        border=f"1px solid {COLOR_BORDER}",
        border_radius="12px",
        spacing="3",
        align_items="center",
    )


def password_input(
    placeholder: str,
    on_change,
    show_password: rx.Var,
    on_toggle,
) -> rx.Component:
    return rx.hstack(
        rx.icon("lock-keyhole", size=18, color=COLOR_TEXT_SECONDARY),
        rx.input(
            placeholder=placeholder,
            on_change=on_change,
            type=rx.cond(show_password, "text", "password"),
            width="100%",
            border="none",
            outline="none",
            background="transparent",
            color=COLOR_TEXT_PRIMARY,
            _placeholder={"color": COLOR_TEXT_SECONDARY},
            aria_label=placeholder,
        ),
        rx.icon(
            tag=rx.cond(show_password, "eye-off", "eye"),
            size=18,
            color=COLOR_TEXT_SECONDARY,
            cursor="pointer",
            on_click=on_toggle,
            _hover={"color": COLOR_ACCENT},
        ),
        width="100%",
        padding="0.65em 1em",
        background=COLOR_INPUT_BG,
        border=f"1px solid {COLOR_BORDER}",
        border_radius="12px",
        spacing="3",
        align_items="center",
    )


def form_message(message: rx.Var, success: rx.Var | None = None) -> rx.Component:
    color = (
        rx.cond(success, "#22c55e", "#f87171")
        if success is not None
        else "#f87171"
    )
    return rx.cond(
        message != "",
        rx.text(
            message,
            color=color,
            font_size="0.85em",
            role="alert",
            width="100%",
        ),
        rx.fragment(),
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
                "Entre com seu e-mail para continuar.",
                color=COLOR_TEXT_SECONDARY,
                font_size="0.85em",
                text_align="left",
            ),
            align_items="start",
            spacing="1",
            width="100%",
            margin_bottom="1em",
        ),
        rx.cond(
            LoginState.error_message != "",
            rx.text(
                LoginState.error_message,
                color="#f87171",
                font_size="0.85em",
                role="alert",
                width="100%",
            ),
            rx.fragment(),
        ),
        text_field(
            "mail",
            "exemplo@email.com",
            LoginState.email,
            LoginState.set_email,
            input_type="email",
        ),
        password_field(),
        rx.hstack(
            rx.hstack(
                rx.checkbox(
                    checked=LoginState.remember_me,
                    on_change=LoginState.set_remember_me,
                    color_scheme="cyan",
                ),
                rx.text(
                    "Lembrar de mim",
                    color=COLOR_TEXT_SECONDARY,
                    font_size="0.85em",
                ),
                spacing="2",
                align_items="center",
            ),
            rx.spacer(),
            rx.link(
                "Esqueci minha senha",
                href="/recuperar-senha",
                color=COLOR_ACCENT,
                font_size="0.85em",
                _hover={
                    "color": COLOR_ACCENT_2,
                    "text_decoration": "underline",
                },
            ),
            width="100%",
            margin_top="0.25em",
            margin_bottom="0.5em",
            flex_wrap="wrap",
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
            font_weight="700",
            cursor="pointer",
            _hover={"filter": "brightness(1.08)"},
        ),
        rx.hstack(
            rx.text(
                "Ainda não tem uma conta?",
                color=COLOR_TEXT_SECONDARY,
                font_size="0.85em",
            ),
            rx.link(
                "Cadastre-se",
                href="/register",
                color=COLOR_ACCENT,
                font_size="0.85em",
                _hover={
                    "color": COLOR_ACCENT_2,
                    "text_decoration": "underline",
                },
            ),
            justify="center",
            width="100%",
            margin_top="0.5em",
            flex_wrap="wrap",
        ),
        width="100%",
        spacing="4",
        padding="2em",
        background=COLOR_CARD_BG,
        border=f"1px solid {COLOR_BORDER}",
        border_radius="20px",
        box_shadow="0 20px 60px rgba(0, 0, 0, 0.4)",
    )


def register_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Criar nova conta",
                color=COLOR_TEXT_PRIMARY,
                font_size="1.2em",
                font_weight="700",
            ),
            rx.text(
                "Preencha os dados para criar seu acesso.",
                color=COLOR_TEXT_SECONDARY,
                font_size="0.85em",
            ),
            align_items="start",
            spacing="1",
            width="100%",
            margin_bottom="1em",
        ),
        form_message(LoginState.register_error_message),
        text_field(
            "user",
            "Nome completo",
            LoginState.register_name,
            LoginState.set_register_name,
        ),
        text_field(
            "mail",
            "exemplo@email.com",
            LoginState.register_email,
            LoginState.set_register_email,
            input_type="email",
        ),
        password_input(
            "Crie uma senha",
            LoginState.set_register_password,
            LoginState.show_password,
            LoginState.toggle_show_password,
        ),
        rx.button(
            "Cadastrar",
            on_click=LoginState.handle_register,
            loading=LoginState.is_registering,
            width="100%",
            padding="1.2em 0",
            border_radius="12px",
            background=f"linear-gradient(90deg, {COLOR_ACCENT_2}, {COLOR_ACCENT})",
            color="white",
            font_weight="700",
            cursor="pointer",
        ),
        rx.hstack(
            rx.text(
                "Já tem uma conta?",
                color=COLOR_TEXT_SECONDARY,
                font_size="0.85em",
            ),
            rx.link(
                "Faça login",
                href="/",
                color=COLOR_ACCENT,
                font_size="0.85em",
            ),
            justify="center",
            width="100%",
            flex_wrap="wrap",
        ),
        width="100%",
        spacing="4",
        padding="2em",
        background=COLOR_CARD_BG,
        border=f"1px solid {COLOR_BORDER}",
        border_radius="20px",
        box_shadow="0 20px 60px rgba(0, 0, 0, 0.4)",
    )


def forgot_password_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Recuperar acesso",
                color=COLOR_TEXT_PRIMARY,
                font_size="1.2em",
                font_weight="700",
            ),
            rx.text(
                "Informe seu e-mail para receber um link seguro de redefinição.",
                color=COLOR_TEXT_SECONDARY,
                font_size="0.85em",
            ),
            align_items="start",
            spacing="1",
            width="100%",
            margin_bottom="1em",
        ),
        rx.cond(
            ForgotPasswordState.message != "",
            rx.text(
                ForgotPasswordState.message,
                color=COLOR_TEXT_SECONDARY,
                font_size="0.85em",
                role="status",
                width="100%",
            ),
            rx.fragment(),
        ),
        text_field(
            "mail",
            "exemplo@email.com",
            ForgotPasswordState.email,
            ForgotPasswordState.set_email,
            input_type="email",
        ),
        rx.button(
            "Enviar link de recuperação",
            on_click=ForgotPasswordState.handle_recover,
            loading=ForgotPasswordState.is_loading,
            width="100%",
            padding="1.2em 0",
            border_radius="12px",
            background=f"linear-gradient(90deg, {COLOR_ACCENT_2}, {COLOR_ACCENT})",
            color="white",
            font_weight="700",
            cursor="pointer",
        ),
        rx.link(
            "Voltar para o login",
            href="/",
            color=COLOR_ACCENT,
            font_size="0.85em",
            text_align="center",
        ),
        width="100%",
        spacing="4",
        padding="2em",
        background=COLOR_CARD_BG,
        border=f"1px solid {COLOR_BORDER}",
        border_radius="20px",
        box_shadow="0 20px 60px rgba(0, 0, 0, 0.4)",
    )


def reset_password_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Criar nova senha",
                color=COLOR_TEXT_PRIMARY,
                font_size="1.2em",
                font_weight="700",
            ),
            rx.text(
                "Defina e confirme sua nova senha para concluir a recuperação.",
                color=COLOR_TEXT_SECONDARY,
                font_size="0.85em",
            ),
            align_items="start",
            spacing="1",
            width="100%",
            margin_bottom="1em",
        ),
        form_message(
            ResetPasswordState.message,
            ResetPasswordState.is_success,
        ),
        rx.cond(
            ResetPasswordState.is_success,
            rx.fragment(),
            rx.vstack(
                password_input(
                    "Nova senha",
                    ResetPasswordState.set_password,
                    ResetPasswordState.show_password,
                    ResetPasswordState.toggle_show_password,
                ),
                password_input(
                    "Confirme a nova senha",
                    ResetPasswordState.set_confirm_password,
                    ResetPasswordState.show_password,
                    ResetPasswordState.toggle_show_password,
                ),
                rx.button(
                    "Redefinir senha",
                    on_click=ResetPasswordState.handle_reset,
                    loading=ResetPasswordState.is_loading,
                    width="100%",
                    padding="1.2em 0",
                    border_radius="12px",
                    background=f"linear-gradient(90deg, {COLOR_ACCENT_2}, {COLOR_ACCENT})",
                    color="white",
                    font_weight="700",
                    cursor="pointer",
                ),
                width="100%",
                spacing="4",
            ),
        ),
        rx.link(
            "Voltar para o login",
            href="/",
            color=COLOR_ACCENT,
            font_size="0.85em",
            text_align="center",
        ),
        width="100%",
        spacing="4",
        padding="2em",
        background=COLOR_CARD_BG,
        border=f"1px solid {COLOR_BORDER}",
        border_radius="20px",
        box_shadow="0 20px 60px rgba(0, 0, 0, 0.4)",
    )


def auth_page_shell(content: rx.Component) -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                header(),
                content,
                rx.text(
                    "© 2026 DROGA-NONIMO · Sistema de gestão farmacêutica",
                    color=COLOR_TEXT_SECONDARY,
                    font_size="0.75em",
                    text_align="center",
                    margin_top="1em",
                ),
                width="100%",
                max_width="400px",
                align_items="center",
            ),
            width="100%",
            min_height="100vh",
            padding="2em 1.2em",
        ),
        width="100%",
        min_height="100vh",
        background=(
            f"radial-gradient(circle at 50% 0%, #1a2233 0%, "
            f"{COLOR_BG_DARK} 60%)"
        ),
    )


def login_page() -> rx.Component:
    return auth_page_shell(login_form())


def register_page() -> rx.Component:
    return auth_page_shell(register_form())


def forgot_password_page() -> rx.Component:
    return auth_page_shell(forgot_password_form())


def reset_password_page() -> rx.Component:
    return auth_page_shell(
        rx.cond(
            ResetPasswordState.is_link_verified,
            reset_password_form(),
            rx.vstack(
                rx.text(
                    "Validando o link de recuperação...",
                    color=COLOR_TEXT_SECONDARY,
                    text_align="center",
                ),
                form_message(ResetPasswordState.message),
                rx.link(
                    "Solicitar um novo link",
                    href="/recuperar-senha",
                    color=COLOR_ACCENT,
                ),
                width="100%",
                align_items="center",
                spacing="4",
                padding="2em",
                background=COLOR_CARD_BG,
                border=f"1px solid {COLOR_BORDER}",
                border_radius="20px",
            ),
        )
    )


def splash_page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                logo("240px"),
                align_items="center",
                spacing="2",
            ),
            width="100%",
            min_height="100vh",
        ),
        width="100%",
        min_height="100vh",
        background="radial-gradient(circle at 50% 0%, rgba(29,47,70,0.9), rgba(3,8,18,0.97) 60%)",
    )


def management_sidebar(active: str) -> rx.Component:
    def item(label: str, icon_name: str, route: str, key: str) -> rx.Component:
        row = rx.hstack(
            rx.icon(
                icon_name,
                size=18,
                color="white" if active == key else "#d6f7ee",
            ),
            rx.text(
                label,
                color="white" if active == key else "#dfe7ec",
                font_size="1rem",
                font_weight="600",
            ),
            width="100%",
            padding="0.8rem 0.9rem",
            border_radius="12px",
            background=(
                "linear-gradient(90deg, rgba(34,197,94,0.25), rgba(34,197,94,0.06))"
                if active == key
                else "transparent"
            ),
            border=(
                "1px solid rgba(34,197,94,0.6)"
                if active == key
                else "1px solid rgba(255,255,255,0.06)"
            ),
            align_items="center",
            spacing="2",
            _hover={"background": "rgba(255,255,255,0.05)"},
        )
        return rx.link(
            row,
            href=route,
            width="100%",
            text_decoration="none",
        )

    return rx.box(
        rx.vstack(
            rx.link(
                logo("140px"),
                href="/dashboard",
                width="100%",
                display="flex",
                align_items="center",
                justify_content="center",
                margin_bottom="1rem",
            ),
            item("Visão Geral", "house", "/dashboard", "overview"),
            item("Gestão de Estoque", "boxes", "/estoque", "stock"),
            item("Vendas", "shopping-cart", "/vendas", "sales"),
            sidebar_item_disabled("Categorias", "tag"),
            sidebar_item_disabled("Funcionários", "users"),
            sidebar_item_disabled("Configurações", "settings"),
            rx.spacer(),
            rx.hstack(
                rx.avatar(
                    fallback="U",
                    size="4",
                    background="rgba(255,255,255,0.25)",
                    color="white",
                    border="1px solid rgba(255,255,255,0.2)",
                ),
                rx.button(
                    "Sair",
                    on_click=LoginState.logout,
                    background="rgba(255,255,255,0.1)",
                    color="white",
                    border="1px solid rgba(255,255,255,0.2)",
                    border_radius="10px",
                    padding="0.45rem 0.7rem",
                    width="74px",
                    min_width="74px",
                    height="38px",
                    _hover={"background": "rgba(255,255,255,0.18)"},
                ),
                width="100%",
                spacing="2",
                align_items="center",
            ),
            width="100%",
            min_height="100vh",
            padding="1.2rem 0.9rem",
            spacing="2",
        ),
        width="280px",
        min_width="280px",
        min_height="100vh",
        background="linear-gradient(180deg, rgba(10,20,36,1), rgba(18,38,58,1))",
        border_right="1px solid rgba(255,255,255,0.08)",
    )


def sidebar_item_disabled(label: str, icon_name: str) -> rx.Component:
    return rx.hstack(
        rx.icon(icon_name, size=18, color="#d6f7ee"),
        rx.text(label, color="#dfe7ec", font_size="1rem", font_weight="600"),
        width="100%",
        padding="0.8rem 0.9rem",
        border_radius="12px",
        border="1px solid rgba(255,255,255,0.06)",
        align_items="center",
        spacing="2",
        opacity="0.65",
    )


def management_page_shell(
    active: str,
    title: str,
    content: rx.Component,
) -> rx.Component:
    return rx.box(
        rx.hstack(
            management_sidebar(active),
            rx.box(
                rx.vstack(
                    rx.heading(
                        title,
                        color="#1f2c39",
                        font_size="2rem",
                        font_weight="700",
                        align_self="flex-start",
                    ),
                    content,
                    width="100%",
                    padding="2rem",
                    spacing="5",
                    align_items="stretch",
                ),
                width="100%",
                min_height="100vh",
                background="#f3f4f6",
                overflow_x="auto",
            ),
            width="100%",
            min_height="100vh",
            align_items="stretch",
        ),
        width="100%",
        min_height="100vh",
        background="#f3f4f6",
    )


def stock_page() -> rx.Component:
    def product_row(product: rx.Var) -> rx.Component:
        quantity = product["estoque_quantidade"].to(int)
        return rx.hstack(
            rx.vstack(
                rx.text(
                    product["nome"],
                    color="#1f2c39",
                    font_weight="700",
                ),
                rx.text(
                    "Código: ",
                    product["codigo_barras"],
                    color="#64748b",
                    font_size="0.82rem",
                ),
                align_items="flex-start",
                spacing="1",
                width="32%",
            ),
            rx.text(
                "R$ ",
                product["preco"],
                color="#34485b",
                font_weight="600",
                width="20%",
            ),
            rx.vstack(
                rx.text(
                    quantity,
                    color="#1f2c39",
                    font_weight="700",
                ),
                rx.cond(
                    quantity <= 5,
                    rx.text("Estoque baixo", color="#dc2626", font_size="0.78rem"),
                    rx.text("Disponível", color="#16a34a", font_size="0.78rem"),
                ),
                align_items="flex-start",
                spacing="1",
                width="20%",
            ),
            rx.button(
                "Editar",
                on_click=LoginState.start_product_edit(
                    product["id"],
                    product["nome"],
                    product["codigo_barras"],
                    product["preco"],
                    quantity,
                ),
                variant="outline",
                color="#1d4ed8",
                size="2",
            ),
            rx.button(
                "Excluir",
                on_click=LoginState.delete_product(product["id"]),
                variant="outline",
                color="#dc2626",
                size="2",
            ),
            width="100%",
            padding="0.9rem 1rem",
            border_bottom="1px solid #e5e7eb",
            align_items="center",
            spacing="3",
            flex_wrap="wrap",
        )

    content = rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Produtos cadastrados", color="#64748b", font_size="0.9rem"),
                rx.text(LoginState.products.length(), color="#1f2c39", font_size="1.6rem", font_weight="700"),
                padding="1rem 1.25rem",
                background="white",
                border="1px solid #e5e7eb",
                border_radius="14px",
                width="100%",
            ),
            rx.vstack(
                rx.text("Estoque baixo (até 5)", color="#64748b", font_size="0.9rem"),
                rx.text(LoginState.low_stock_count, color="#dc2626", font_size="1.6rem", font_weight="700"),
                padding="1rem 1.25rem",
                background="white",
                border="1px solid #e5e7eb",
                border_radius="14px",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        rx.hstack(
            rx.input(
                placeholder="Buscar por nome ou código de barras",
                value=LoginState.product_search,
                on_change=LoginState.set_product_search,
                width="100%",
                max_width="520px",
                background="white",
            ),
            rx.button(
                rx.cond(LoginState.low_stock_only, "Mostrar todos", "Estoque baixo"),
                on_click=LoginState.toggle_low_stock_filter,
                variant="outline",
            ),
            rx.spacer(),
            rx.button(
                "Novo produto",
                on_click=LoginState.cancel_product_edit,
                background="#16a34a",
                color="white",
            ),
            width="100%",
            align_items="center",
            flex_wrap="wrap",
        ),
        rx.cond(
            LoginState.stock_error != "",
            rx.text(LoginState.stock_error, color="#dc2626", role="alert"),
            rx.fragment(),
        ),
        rx.cond(
            LoginState.stock_notice != "",
            rx.text(LoginState.stock_notice, color="#16a34a", role="status"),
            rx.fragment(),
        ),
        rx.vstack(
            rx.heading(
                rx.cond(
                    LoginState.editing_product_id > 0,
                    "Editar produto",
                    "Cadastrar produto",
                ),
                color="#1f2c39",
                size="4",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Nome do produto",
                    value=LoginState.product_name,
                    on_change=LoginState.set_product_name,
                    width="100%",
                    background="white",
                ),
                rx.input(
                    placeholder="Código de barras",
                    value=LoginState.product_barcode,
                    on_change=LoginState.set_product_barcode,
                    width="100%",
                    background="white",
                ),
                width="100%",
                flex_wrap="wrap",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Preço (ex.: 12,50)",
                    value=LoginState.product_price,
                    on_change=LoginState.set_product_price,
                    type="number",
                    width="100%",
                    background="white",
                ),
                rx.input(
                    placeholder="Quantidade em estoque",
                    value=LoginState.product_stock,
                    on_change=LoginState.set_product_stock,
                    type="number",
                    width="100%",
                    background="white",
                ),
                rx.button(
                    rx.cond(
                        LoginState.is_saving_product,
                        "Salvando...",
                        "Salvar produto",
                    ),
                    on_click=LoginState.save_product,
                    loading=LoginState.is_saving_product,
                    background="#16a34a",
                    color="white",
                ),
                rx.button(
                    "Cancelar",
                    on_click=LoginState.cancel_product_edit,
                    variant="outline",
                ),
                width="100%",
                flex_wrap="wrap",
            ),
            width="100%",
            padding="1.25rem",
            background="white",
            border="1px solid #e5e7eb",
            border_radius="16px",
            spacing="3",
            align_items="stretch",
        ),
        rx.vstack(
            rx.hstack(
                rx.text("Produto", width="32%", font_weight="700", color="#475569"),
                rx.text("Preço", width="20%", font_weight="700", color="#475569"),
                rx.text("Quantidade", width="20%", font_weight="700", color="#475569"),
                rx.text("Ações", font_weight="700", color="#475569"),
                width="100%",
                padding="0.9rem 1rem",
                border_bottom="1px solid #e5e7eb",
                flex_wrap="wrap",
            ),
            rx.cond(
                LoginState.is_loading_products,
                rx.text("Carregando produtos do Xano...", color="#64748b", padding="1rem"),
                rx.fragment(),
            ),
            rx.foreach(LoginState.filtered_products, product_row),
            rx.cond(
                (LoginState.products.length() == 0)
                & (LoginState.is_loading_products == False),
                rx.text(
                    "Ainda não há produtos cadastrados no Xano.",
                    color="#64748b",
                    padding="1rem",
                ),
                rx.fragment(),
            ),
            width="100%",
            background="white",
            border="1px solid #e5e7eb",
            border_radius="16px",
            overflow="hidden",
            align_items="stretch",
            spacing="0",
        ),
        width="100%",
        spacing="4",
        align_items="stretch",
    )
    return management_page_shell("stock", "Gestão de Estoque", content)


def sales_page() -> rx.Component:
    def catalog_row(product: rx.Var) -> rx.Component:
        return rx.hstack(
            rx.vstack(
                rx.text(product["nome"], color="#1f2c39", font_weight="700"),
                rx.text(
                    "R$ ",
                    product["preco"],
                    " · Estoque: ",
                    product["estoque_quantidade"],
                    color="#64748b",
                    font_size="0.85rem",
                ),
                align_items="flex-start",
                spacing="1",
                width="100%",
            ),
            rx.button(
                "Adicionar",
                on_click=LoginState.add_to_cart(product["id"]),
                size="2",
                background="#16a34a",
                color="white",
            ),
            width="100%",
            padding="0.85rem 1rem",
            border_bottom="1px solid #e5e7eb",
            align_items="center",
            spacing="3",
        )

    def cart_row(item: rx.Var) -> rx.Component:
        return rx.hstack(
            rx.vstack(
                rx.text(item["nome"], color="#1f2c39", font_weight="600"),
                rx.text(
                    "R$ ",
                    item["preco"],
                    " cada",
                    color="#64748b",
                    font_size="0.82rem",
                ),
                align_items="flex-start",
                spacing="1",
                width="100%",
            ),
            rx.button(
                "−",
                on_click=LoginState.change_cart_quantity(item["produto_id"], -1),
                variant="outline",
                size="1",
            ),
            rx.text(item["quantidade"], color="#1f2c39", font_weight="700"),
            rx.button(
                "+",
                on_click=LoginState.change_cart_quantity(item["produto_id"], 1),
                variant="outline",
                size="1",
            ),
            width="100%",
            padding="0.7rem 0",
            align_items="center",
            spacing="2",
        )

    def sale_row(sale: rx.Var) -> rx.Component:
        return rx.hstack(
            rx.text("#", sale["id"], color="#1f2c39", font_weight="700", width="16%"),
            rx.text(
                "Cliente: ",
                sale["cliente_id"],
                color="#64748b",
                width="24%",
            ),
            rx.text("R$ ", sale["valor_total"], color="#1f2c39", width="24%"),
            rx.text(sale["forma_pagamento"], color="#475569", width="20%"),
            rx.text(sale["criado_em"], color="#64748b", font_size="0.82rem", width="16%"),
            width="100%",
            padding="0.85rem 1rem",
            border_bottom="1px solid #e5e7eb",
            align_items="center",
            flex_wrap="wrap",
        )

    content = rx.vstack(
        rx.cond(
            LoginState.sales_error != "",
            rx.text(LoginState.sales_error, color="#dc2626", role="alert"),
            rx.fragment(),
        ),
        rx.hstack(
            rx.vstack(
                rx.heading("Catálogo", color="#1f2c39", size="4"),
                rx.input(
                    placeholder="Buscar produtos no estoque",
                    value=LoginState.product_search,
                    on_change=LoginState.set_product_search,
                    width="100%",
                    background="white",
                ),
                rx.vstack(
                    rx.foreach(LoginState.filtered_products, catalog_row),
                    width="100%",
                    max_height="420px",
                    overflow_y="auto",
                    background="white",
                    border="1px solid #e5e7eb",
                    border_radius="14px",
                    align_items="stretch",
                    spacing="0",
                ),
                width="100%",
                padding="1.2rem",
                background="white",
                border="1px solid #e5e7eb",
                border_radius="16px",
                spacing="3",
                align_items="stretch",
            ),
            rx.vstack(
                rx.heading("Carrinho", color="#1f2c39", size="4"),
                rx.text(
                    "Itens: ",
                    LoginState.cart_item_count,
                    color="#64748b",
                ),
                rx.vstack(
                    rx.foreach(LoginState.cart, cart_row),
                    width="100%",
                    align_items="stretch",
                    spacing="1",
                ),
                rx.input(
                    placeholder="Cliente (opcional)",
                    value=LoginState.selected_customer,
                    on_change=LoginState.set_selected_customer,
                    width="100%",
                    background="white",
                ),
                rx.text("Forma de pagamento", color="#475569", font_weight="600"),
                rx.select(
                    ["Dinheiro", "PIX", "Crédito", "Débito"],
                    value=LoginState.payment_method,
                    on_change=LoginState.set_payment_method,
                    width="100%",
                ),
                rx.hstack(
                    rx.text("Total", color="#475569", font_weight="700"),
                    rx.spacer(),
                    rx.text("R$ ", LoginState.cart_total, color="#1f2c39", font_size="1.35rem", font_weight="800"),
                    width="100%",
                    padding_top="0.8rem",
                    border_top="1px solid #e5e7eb",
                ),
                rx.text(
                    "Carrinho demonstrativo: o checkout e a baixa de estoque serão conectados após a criação do endpoint transacional no Xano.",
                    color="#a16207",
                    font_size="0.82rem",
                    role="status",
                ),
                rx.hstack(
                    rx.button(
                        "Limpar carrinho",
                        on_click=LoginState.clear_cart,
                        variant="outline",
                        width="100%",
                    ),
                    rx.button(
                        "Finalização pendente",
                        disabled=True,
                        width="100%",
                        background="#94a3b8",
                        color="white",
                    ),
                    width="100%",
                    flex_wrap="wrap",
                ),
                width="100%",
                padding="1.2rem",
                background="white",
                border="1px solid #e5e7eb",
                border_radius="16px",
                spacing="3",
                align_items="stretch",
            ),
            width="100%",
            align_items="flex-start",
            spacing="4",
            flex_wrap="wrap",
        ),
        rx.vstack(
            rx.hstack(
                rx.heading("Histórico de vendas", color="#1f2c39", size="4"),
                rx.spacer(),
                rx.button(
                    "Atualizar",
                    on_click=LoginState.load_sales,
                    loading=LoginState.is_loading_sales,
                    variant="outline",
                ),
                width="100%",
                align_items="center",
            ),
            rx.hstack(
                rx.text("Venda", width="16%", font_weight="700", color="#475569"),
                rx.text("Cliente", width="24%", font_weight="700", color="#475569"),
                rx.text("Total", width="24%", font_weight="700", color="#475569"),
                rx.text("Pagamento", width="20%", font_weight="700", color="#475569"),
                rx.text("Data", width="16%", font_weight="700", color="#475569"),
                width="100%",
                padding="0.9rem 1rem",
                border_bottom="1px solid #e5e7eb",
                flex_wrap="wrap",
            ),
            rx.foreach(LoginState.sales, sale_row),
            rx.cond(
                LoginState.is_loading_sales,
                rx.text("Carregando histórico do Xano...", color="#64748b", padding="1rem"),
                rx.fragment(),
            ),
            rx.cond(
                (LoginState.sales.length() == 0)
                & (LoginState.is_loading_sales == False),
                rx.text(
                    "Nenhuma venda registrada ainda.",
                    color="#64748b",
                    padding="1rem",
                ),
                rx.fragment(),
            ),
            width="100%",
            padding="1.2rem",
            background="white",
            border="1px solid #e5e7eb",
            border_radius="16px",
            spacing="2",
            align_items="stretch",
            overflow_x="auto",
        ),
        width="100%",
        spacing="4",
        align_items="stretch",
    )
    return management_page_shell("sales", "Vendas", content)


def dashboard_page() -> rx.Component:
    def sidebar_item(label: str, icon_name: str, active: bool = False) -> rx.Component:
        return rx.hstack(
            rx.icon(
                icon_name,
                size=18,
                color="white" if active else "#d6f7ee",
            ),
            rx.text(
                label,
                color="white" if active else "#dfe7ec",
                font_size="1.05rem",
                font_weight="600",
            ),
            width="100%",
            padding="0.9rem 1rem",
            border_radius="12px",
            background="linear-gradient(90deg, rgba(34,197,94,0.25), rgba(34,197,94,0.06))" if active else "transparent",
            border=f"1px solid {'rgba(34,197,94,0.6)' if active else 'rgba(255,255,255,0.06)'}",
            align_items="center",
            spacing="2",
            cursor="pointer",
            _hover={"background": "rgba(255,255,255,0.05)"},
        )

    def stat_card(title: str, value: str, subtitle: str, highlight: bool = False) -> rx.Component:
        return rx.vstack(
            rx.text(
                title,
                color="#1d2736",
                font_size="1.05rem",
                font_weight="700",
                margin_bottom="0.2rem",
            ),
            rx.text(
                value,
                color="#101828",
                font_size="2.1rem",
                font_weight="800",
            ),
            rx.text(
                subtitle,
                color="#5f6f7b",
                font_size="0.92rem",
            ),
            width="100%",
            min_height="180px",
            padding="1.2rem 1.4rem",
            background="rgba(255,255,255,0.85)",
            border=f"1px solid {'#6dd5ff' if highlight else '#e5e7eb'}",
            border_radius="18px",
            box_shadow="0 12px 28px rgba(15, 23, 42, 0.05)",
            justify="center",
            align_items="flex-start",
            spacing="2",
        )

    def category_row(label: str, amount: str, color: str, percent: int) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.text(label, color="#34485b", font_size="0.95rem", font_weight="600"),
                rx.spacer(),
                rx.text(amount, color="#34485b", font_size="0.95rem", font_weight="700"),
                width="100%",
            ),
            rx.box(
                rx.box(
                    width=f"{percent}%",
                    height="100%",
                    background=color,
                    border_radius="999px",
                ),
                width="100%",
                height="18px",
                border_radius="999px",
                background="rgba(148, 163, 184, 0.18)",
                overflow="hidden",
                margin_top="0.15rem",
            ),
            width="100%",
            spacing="2",
            margin_bottom="0.7rem",
        )

    def action_card(title: str, subtitle: str, icon_name: str, bg: str) -> rx.Component:
        return rx.vstack(
            rx.box(
                rx.icon(icon_name, size=26, color="#1d2736"),
                width="44px",
                height="44px",
                display="flex",
                align_items="center",
                justify_content="center",
                border_radius="12px",
                background="rgba(255,255,255,0.4)",
            ),
            rx.text(title, color="#1d2736", font_size="1.05rem", font_weight="600", text_align="center"),
            rx.text(subtitle, color="#526272", font_size="0.82rem", text_align="center"),
            width="100%",
            min_height="150px",
            padding="1rem 0.7rem",
            background=bg,
            border="1px solid rgba(148, 163, 184, 0.22)",
            border_radius="16px",
            justify="center",
            align_items="center",
            spacing="2",
        )

    return rx.box(
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.box(
                        logo("138px"),
                        width="100%",
                        min_height="150px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        margin_bottom="0.5rem",
                    ),
                    rx.link(
                        sidebar_item("Visão Geral", "house", True),
                        href="/dashboard",
                        width="100%",
                        text_decoration="none",
                    ),
                    rx.link(
                        sidebar_item("Gestão de Estoque", "boxes"),
                        href="/estoque",
                        width="100%",
                        text_decoration="none",
                    ),
                    rx.link(
                        sidebar_item("Vendas", "shopping-cart"),
                        href="/vendas",
                        width="100%",
                        text_decoration="none",
                    ),
                    sidebar_item("Categorias", "tag"),
                    sidebar_item("Funcionários", "users"),
                    sidebar_item("Configurações", "settings"),
                    rx.spacer(),
                    rx.hstack(
                        rx.avatar(
                            fallback="U",
                            size="4",
                            background="rgba(255,255,255,0.25)",
                            color="white",
                            border="1px solid rgba(255,255,255,0.2)",
                        ),
                        rx.button(
                            "Sair",
                            on_click=LoginState.logout,
                            background="rgba(255,255,255,0.1)",
                            color="white",
                            border="1px solid rgba(255,255,255,0.2)",
                            border_radius="12px",
                            padding="0.5rem 0.7rem",
                            width="74px",
                            min_width="74px",
                            height="38px",
                            _hover={"background": "rgba(255,255,255,0.18)"},
                        ),
                        width="100%",
                        spacing="2",
                        align_items="center",
                    ),
                    width="100%",
                    min_height="100%",
                    padding="2rem 1rem 1.25rem",
                    spacing="2",
                ),
                width="280px",
                min_width="280px",
                min_height="100vh",
                background="linear-gradient(180deg, rgba(10,20,36,1), rgba(18,38,58,1))",
                border_right="1px solid rgba(255,255,255,0.08)",
            ),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            "Visão Geral",
                            color="#1f2c39",
                            font_size="2.3rem",
                            font_weight="700",
                            margin_left="0.5rem",
                        ),
                        rx.spacer(),
                        rx.link(
                            rx.button(
                                rx.icon("plus", size=16, color="white"),
                                rx.text("Nova Venda", color="white", font_weight="700"),
                                background="linear-gradient(90deg, #17b26a, #16a34a)",
                                border_radius="12px",
                                padding="0.9rem 1.3rem",
                                border="none",
                                box_shadow="0 10px 22px rgba(22,163,74,0.28)",
                                _hover={"filter": "brightness(1.05)"},
                            ),
                            href="/vendas",
                            text_decoration="none",
                        ),
                        width="100%",
                        align_items="center",
                        margin_bottom="1.5rem",
                    ),
                    rx.hstack(
                        stat_card("Vendas Hoje", "R$ 0,00", "0 Vendas Realizadas", True),
                        stat_card("Esta Semana", "R$ 0,00", "Acumulado dos 7 dias"),
                        width="100%",
                        spacing="2",
                    ),
                    rx.hstack(
                        stat_card("Este Mês", "R$ 0,00", "Meta mensal atingida em 0%"),
                        stat_card("Itens Estoque", "0", "0 produtos cadastrados"),
                        width="100%",
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Vendas por Categorias", color="#1f2c39", font_size="1.2rem", font_weight="700"),
                            category_row("Medicamentos", "R$ 0,00", "#22c55e", 0),
                            category_row("Antibióticos", "R$ 0,00", "#ef4444", 0),
                            category_row("Proteínas e Suplementos", "R$ 0,00", "#3b82f6", 0),
                            category_row("Primeiros Socorros", "R$ 0,00", "#f59e0b", 0),
                            width="100%",
                            padding="1.3rem 1.4rem",
                            background="rgba(255,255,255,0.84)",
                            border="1px solid rgba(148,163,184,0.18)",
                            border_radius="18px",
                            box_shadow="0 12px 28px rgba(15, 23, 42, 0.05)",
                        ),
                        rx.vstack(
                            rx.text("Modificações Rápidas", color="#1f2c39", font_size="1.2rem", font_weight="700"),
                            rx.grid(
                                action_card("Promoções", "Ajustar promoções", "tag", "rgba(239,246,255,0.9)"),
                                action_card("Alterar Horário", "Ajustar expediente de hoje", "clock", "rgba(244,240,229,0.9)"),
                                action_card("Avisos", "Enviar aviso aos clientes", "bell", "rgba(250,245,235,0.9)"),
                                action_card("Pausar Loja", "Interromper vendas", "pause", "rgba(254,242,242,0.9)"),
                                columns="2",
                                gap="2",
                                width="100%",
                            ),
                            width="100%",
                            padding="1.3rem 1.4rem",
                            background="rgba(255,255,255,0.72)",
                            border="1px solid rgba(148,163,184,0.18)",
                            border_radius="18px",
                            box_shadow="0 12px 28px rgba(15, 23, 42, 0.05)",
                            spacing="2",
                        ),
                        width="100%",
                        spacing="2",
                    ),
                    width="100%",
                    padding="2.2rem 2rem 2.5rem",
                    spacing="2",
                ),
                width="100%",
                min_height="100vh",
                background="#f3f4f6",
            ),
            width="100%",
            min_height="100vh",
            align_items="stretch",
        ),
        width="100%",
        min_height="100vh",
        background="#f3f4f6",
    )


app = rx.App()
app.add_page(
    login_page,
    route="/",
    title="Entrar · DROGA-NONIMO",
    on_load=LoginState.clear_login_message,
)
app.add_page(
    register_page,
    route="/register",
    title="Cadastro · DROGA-NONIMO",
    on_load=LoginState.clear_register_message,
)
app.add_page(
    forgot_password_page,
    route="/recuperar-senha",
    title="Recuperar senha · DROGA-NONIMO",
    on_load=ForgotPasswordState.clear_message,
)
app.add_page(
    reset_password_page,
    route="/redefinir-senha",
    title="Redefinir senha · DROGA-NONIMO",
    on_load=ResetPasswordState.prepare_reset,
)
app.add_page(
    splash_page,
    route="/splash",
    title="Carregando · DROGA-NONIMO",
    on_load=SplashState.go_dashboard,
)
app.add_page(
    dashboard_page,
    route="/dashboard",
    title="Painel · DROGA-NONIMO",
    on_load=LoginState.require_login,
)
app.add_page(
    stock_page,
    route="/estoque",
    title="Estoque · DROGA-NONIMO",
    on_load=LoginState.load_stock,
)
app.add_page(
    sales_page,
    route="/vendas",
    title="Vendas · DROGA-NONIMO",
    on_load=LoginState.load_sales,
)

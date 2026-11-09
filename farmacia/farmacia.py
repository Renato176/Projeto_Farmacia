"""DROGA-NONIMO pharmacy application."""

import asyncio
import logging
import unicodedata
from typing import Any, TypedDict
from urllib.parse import urlparse

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
CUSTOMER_DISCOUNT_RATE = 14


class CategoryGroup(TypedDict):
    id: int
    nome: str
    descricao: str
    cor: str
    ativo: bool
    subcategorias: list["CategoryRecord"]


class CategoryRecord(TypedDict):
    id: int
    nome: str
    descricao: str
    cor: str
    categoria_pai_id: int | None
    ativo: bool

logger = logging.getLogger(__name__)


def _normalize_search_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )


def _product_matches_search(product: dict[str, Any], query: str) -> bool:
    normalized_query = _normalize_search_text(query.strip())
    if not normalized_query:
        return True
    return any(
        normalized_query in _normalize_search_text(str(product.get(field, "")))
        for field in ("nome", "codigo_barras")
    )


def _reference_id(value: Any) -> int | None:
    if isinstance(value, dict):
        value = value.get("id")
    if value is None or value == "" or value == "null":
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise ValueError("A referência de categoria não contém um ID válido.") from error


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
    product_category_search: str = ""
    selected_product_category_id: str = ""
    product_form_category_id: str = ""
    category_search_query: str = ""
    categories: list[CategoryRecord] = []
    category_error: str = ""
    category_notice: str = ""
    is_loading_categories: bool = False
    show_category_form: bool = False
    editing_category_id: int = 0
    category_form_name: str = ""
    category_form_description: str = ""
    category_form_parent_id: str = ""
    category_form_active: str = "Ativa"
    category_form_color: str = "#e2e8f0"
    is_saving_category: bool = False
    show_category_delete_confirmation: bool = False
    deleting_category_id: int = 0
    deleting_category_name: str = ""
    is_deleting_category: bool = False
    product_name: str = ""
    product_barcode: str = ""
    product_price: str = ""
    product_stock: str = ""
    product_image_url: str = ""
    product_image_preview_url: str = ""
    original_product_image_url: str = ""
    show_product_form: bool = False
    editing_product_id: int = 0
    stock_error: str = ""
    stock_notice: str = ""
    is_loading_products: bool = False
    is_saving_product: bool = False
    sales_error: str = ""
    sales_notice: str = ""
    is_loading_sales: bool = False
    is_finalizing_sale: bool = False
    show_cart_panel: bool = False
    selected_customer: str = ""
    customer_status: str = "unregistered"
    payment_method: str = "pix"
    show_customer_form: bool = False
    is_saving_customer: bool = False
    customer_form_error: str = ""
    customer_notice: str = ""
    customer_name: str = ""
    customer_cpf: str = ""
    customer_phone: str = ""

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
        self.categories = []
        self.customers = []
        self.sales = []
        self.cart = []
        self.product_search = ""
        self.product_category_search = ""
        self.selected_product_category_id = ""
        self.product_form_category_id = ""
        self.category_error = ""
        self.selected_customer = ""
        self.customer_status = "unregistered"
        self.show_cart_panel = False
        self.customer_name = ""
        self.customer_cpf = ""
        self.customer_phone = ""
        self.customer_notice = ""
        self.customer_form_error = ""
        self.show_customer_form = False
        return rx.redirect("/")

    def _category_label(self, category: CategoryRecord) -> str:
        parent_id = category["categoria_pai_id"]
        if parent_id is None:
            return category["nome"]
        parent = next(
            (item for item in self.categories if item["id"] == parent_id),
            None,
        )
        return (
            f"{parent['nome']} / {category['nome']}"
            if parent
            else category["nome"]
        )

    @rx.var
    def category_option_labels(self) -> list[str]:
        return [
            self._category_label(category)
            for category in self.categories
            if category["ativo"]
        ]

    @rx.var
    def product_category_options(self) -> list[str]:
        return ["Todas as categorias", *self.category_option_labels]

    @rx.var
    def product_form_category_options(self) -> list[str]:
        return ["Sem categoria", *self.category_option_labels]

    @rx.var
    def category_parent_options(self) -> list[str]:
        options = [
            "Sem departamento",
            *[
                self._category_label(category)
                for category in self.categories
                if category["ativo"]
                and category["categoria_pai_id"] is None
                and category["id"] != self.editing_category_id
            ],
        ]
        current_category = next(
            (
                category
                for category in self.categories
                if category["id"] == self.editing_category_id
            ),
            None,
        )
        current_parent = (
            next(
                (
                    category
                    for category in self.categories
                    if category["id"] == current_category["categoria_pai_id"]
                ),
                None,
            )
            if current_category and current_category["categoria_pai_id"] is not None
            else None
        )
        if current_parent and not current_parent["ativo"]:
            options.append(self._category_label(current_parent))
        return options

    @rx.var
    def category_form_parent_label(self) -> str:
        parent_id = _reference_id(self.category_form_parent_id)
        if parent_id is None:
            return "Sem departamento"
        parent = next(
            (category for category in self.categories if category["id"] == parent_id),
            None,
        )
        return self._category_label(parent) if parent else "Sem departamento"

    @rx.var
    def product_form_category_label(self) -> str:
        category_id = _reference_id(self.product_form_category_id)
        if category_id is None:
            return "Sem categoria"
        category = next(
            (
                item
                for item in self.categories
                if item["id"] == category_id and item["ativo"]
            ),
            None,
        )
        return self._category_label(category) if category else "Sem categoria"

    @rx.var
    def filtered_categories(self) -> list[CategoryGroup]:
        query = _normalize_search_text(self.category_search_query.strip())
        categories = self.categories
        filtered_groups = []
        for department in categories:
            if department["categoria_pai_id"] is not None:
                continue
            subcategories = [
                category
                for category in categories
                if category["categoria_pai_id"] == department["id"]
            ]
            matching_subcategories = [
                category
                for category in subcategories
                if not query
                or query in _normalize_search_text(category["nome"])
            ]
            group_matches = (
                not query
                or query in _normalize_search_text(department["nome"])
                or query in _normalize_search_text(department["descricao"])
            )
            if group_matches or matching_subcategories:
                filtered_groups.append(
                    {
                        "id": department["id"],
                        "nome": department["nome"],
                        "descricao": department["descricao"],
                        "cor": department["cor"],
                        "ativo": department["ativo"],
                        "subcategorias": (
                            subcategories if group_matches else matching_subcategories
                        ),
                    }
                )
        return filtered_groups

    @rx.var
    def filtered_subcategory_count(self) -> int:
        return sum(
            len(group["subcategorias"])
            for group in self.filtered_categories
        )

    @rx.var
    def filtered_products(self) -> list[dict[str, Any]]:
        filtered = []
        selected_category_id = _reference_id(self.selected_product_category_id)
        category_ids = {selected_category_id} if selected_category_id else set()
        while category_ids:
            descendants = {
                category["id"]
                for category in self.categories
                if category["ativo"]
                and category["categoria_pai_id"] in category_ids
            }
            if descendants <= category_ids:
                break
            category_ids.update(descendants)
        for product in self.products:
            if not _product_matches_search(product, self.product_search):
                continue
            if selected_category_id and _reference_id(
                product.get("categoria_id")
            ) not in category_ids:
                continue
            product_id = int(product.get("id", 0))
            cart_item = next(
                (
                    item
                    for item in self.cart
                    if int(item["produto_id"]) == product_id
                ),
                None,
            )
            filtered.append(
                {
                    **product,
                    "cart_status": (
                        f"No carrinho: {int(cart_item['quantidade'])}"
                        if cart_item
                        else "Ainda não selecionado"
                    ),
                    "cart_status_color": "#2563eb" if cart_item else "#64748b",
                }
            )
        return filtered

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
    def customer_options(self) -> list[str]:
        return [
            f"{customer.get('nome', '')} · CPF {customer.get('cpf', '')}"
            for customer in self.customers
            if (
                customer.get("nome")
                and customer.get("cpf")
                and customer.get("esta_registrado") is True
            )
        ]

    @rx.var
    def selected_customer_is_registered(self) -> bool:
        return self._is_selected_customer_registered()

    def _is_selected_customer_registered(self) -> bool:
        customer = self._selected_customer_record()
        return (
            self.customer_status == "registered"
            and customer is not None
            and bool(customer.get("esta_registrado"))
        )

    def _selected_customer_record(self) -> dict[str, Any] | None:
        if not self.selected_customer:
            return None
        return next(
            (
                customer
                for customer in self.customers
                if f"{customer.get('nome', '')} · CPF {customer.get('cpf', '')}"
                == self.selected_customer
            ),
            None,
        )

    @rx.var
    def cart_discount(self) -> float:
        subtotal = sum(
            float(item["preco"]) * int(item["quantidade"])
            for item in self.cart
        )
        return (
            round(subtotal * CUSTOMER_DISCOUNT_RATE / 100, 2)
            if self._is_selected_customer_registered()
            else 0.0
        )

    @rx.var
    def cart_final_total(self) -> float:
        subtotal = sum(
            float(item["preco"]) * int(item["quantidade"])
            for item in self.cart
        )
        return round(subtotal - self.cart_discount, 2)

    @staticmethod
    def _format_currency(value: float) -> str:
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @rx.var
    def cart_total_formatted(self) -> str:
        return self._format_currency(self.cart_total)

    @rx.var
    def cart_discount_formatted(self) -> str:
        return self._format_currency(self.cart_discount)

    @rx.var
    def cart_final_total_formatted(self) -> str:
        return self._format_currency(self.cart_final_total)

    @staticmethod
    def _stock_quantity(product: dict[str, Any]) -> int:
        try:
            return int(product.get("estoque_quantidade", 0))
        except (TypeError, ValueError):
            return 0

    async def _load_categories(self) -> bool:
        self.category_error = ""
        try:
            response = await xano.request(
                "GET",
                "/categoria",
                auth_token=self._auth_token,
                base_url=xano.XANO_PHARMACY_API_URL,
            )
        except httpx.RequestError:
            logger.warning("A consulta de categorias no Xano falhou.")
            self.categories = []
            self.selected_product_category_id = ""
            self.product_category_search = ""
            self.product_form_category_id = ""
            self.category_error = "Não foi possível conectar às categorias no Xano."
            return False

        if response.status_code != 200:
            self.categories = []
            self.selected_product_category_id = ""
            self.product_category_search = ""
            self.product_form_category_id = ""
            self.category_error = xano.response_message(
                xano.response_data(response),
                f"Não foi possível carregar as categorias (HTTP {response.status_code}).",
            )
            return False

        try:
            records = xano.response_records(
                xano.response_data(response),
                "categorias",
            )
            categories: list[CategoryRecord] = []
            for record in records:
                category_id = _reference_id(record.get("id"))
                name = record.get("nome")
                is_active = record.get("ativo")
                if category_id is None or not isinstance(name, str) or not name.strip():
                    raise ValueError("A categoria não contém ID ou nome válidos.")
                if not isinstance(is_active, bool):
                    raise ValueError("A categoria não contém um status ativo válido.")

                categories.append(
                    {
                        "id": category_id,
                        "nome": name.strip(),
                        "descricao": str(record.get("descricao") or ""),
                        "cor": str(record.get("cor") or "#e2e8f0"),
                        "categoria_pai_id": _reference_id(
                            record.get("categoria_pai_id")
                        ),
                        "ativo": is_active,
                    }
                )

            category_ids = {category["id"] for category in categories}
            if any(
                category["categoria_pai_id"] is not None
                and category["categoria_pai_id"] not in category_ids
                for category in categories
            ):
                raise ValueError("A categoria pai referenciada não existe.")
        except ValueError:
            logger.error("O endpoint /categoria retornou dados fora do formato esperado.")
            self.categories = []
            self.selected_product_category_id = ""
            self.product_category_search = ""
            self.product_form_category_id = ""
            self.category_error = "O Xano retornou uma lista de categorias inválida."
            return False

        self.categories = categories
        active_category_ids = {
            category["id"] for category in categories if category["ativo"]
        }
        if _reference_id(self.selected_product_category_id) not in active_category_ids:
            self.selected_product_category_id = ""
            self.product_category_search = ""
        if _reference_id(self.product_form_category_id) not in active_category_ids:
            self.product_form_category_id = ""
        return True

    @rx.event
    async def load_categories(self):
        if not self._auth_token:
            return rx.redirect("/")

        self.is_loading_categories = True
        try:
            await self._load_categories()
        finally:
            self.is_loading_categories = False

    @rx.event
    def start_new_category(self):
        self.editing_category_id = 0
        self.category_form_name = ""
        self.category_form_description = ""
        self.category_form_parent_id = ""
        self.category_form_active = "Ativa"
        self.category_form_color = "#e2e8f0"
        self.category_error = ""
        self.category_notice = ""
        self.show_category_form = True

    @rx.event
    def start_category_edit(self, category_id: int):
        category = next(
            (item for item in self.categories if item["id"] == category_id),
            None,
        )
        if category is None:
            logger.warning("Foi solicitada a edição de uma categoria não carregada.")
            self.category_error = "A categoria selecionada não está disponível."
            return

        self.editing_category_id = category_id
        self.category_form_name = category["nome"]
        self.category_form_description = category["descricao"]
        self.category_form_parent_id = str(category["categoria_pai_id"] or "")
        self.category_form_active = "Ativa" if category["ativo"] else "Inativa"
        self.category_form_color = category["cor"]
        self.category_error = ""
        self.category_notice = ""
        self.show_category_form = True

    @rx.event
    def set_category_form_open(self, is_open: bool):
        self.show_category_form = is_open
        if not is_open:
            self.editing_category_id = 0
            self.category_form_name = ""
            self.category_form_description = ""
            self.category_form_parent_id = ""
            self.category_form_active = "Ativa"
            self.category_form_color = "#e2e8f0"

    @rx.event
    def set_category_form_name(self, value: str):
        self.category_form_name = value

    @rx.event
    def set_category_form_description(self, value: str):
        self.category_form_description = value

    @rx.event
    def set_category_form_parent(self, value: str):
        if value == "Sem departamento":
            self.category_form_parent_id = ""
            return
        parent = next(
            (
                category
                for category in self.categories
                if category["ativo"]
                and category["categoria_pai_id"] is None
                and self._category_label(category) == value
            ),
            None,
        )
        if parent is None:
            logger.warning("Foi submetido um departamento-pai inválido.")
            self.category_error = "O departamento selecionado não está disponível."
            return
        self.category_form_parent_id = str(parent["id"])

    @rx.event
    def set_category_form_active(self, value: str):
        self.category_form_active = value

    @rx.event
    def set_category_form_color(self, value: str):
        self.category_form_color = value

    @rx.event
    async def save_category(self):
        if not self._auth_token:
            return rx.redirect("/")

        name = self.category_form_name.strip()
        color = self.category_form_color.strip()
        try:
            parent_id = _reference_id(self.category_form_parent_id)
        except ValueError:
            self.category_error = "O departamento selecionado não é válido."
            return
        if not name:
            self.category_error = "Informe o nome da categoria."
            return
        if not color:
            color = "#e2e8f0"
        if (
            len(color) != 7
            or color[0] != "#"
            or any(character not in "0123456789abcdefABCDEF" for character in color[1:])
        ):
            self.category_error = "Informe uma cor hexadecimal válida, como #e2e8f0."
            return
        if self.category_form_active not in ("Ativa", "Inativa"):
            self.category_error = "Selecione um status válido para a categoria."
            return
        if parent_id == self.editing_category_id and parent_id is not None:
            self.category_error = "Uma categoria não pode ser pai dela mesma."
            return

        parent = next(
            (item for item in self.categories if item["id"] == parent_id),
            None,
        )
        current_category = next(
            (
                item
                for item in self.categories
                if item["id"] == self.editing_category_id
            ),
            None,
        )
        unchanged_inactive_parent = (
            parent is not None
            and not parent["ativo"]
            and current_category is not None
            and current_category["categoria_pai_id"] == parent_id
        )
        if parent_id is not None and (
            parent is None or (not parent["ativo"] and not unchanged_inactive_parent)
        ):
            self.category_error = "O departamento selecionado não está disponível."
            return

        ancestor_id = parent_id
        while ancestor_id is not None:
            if ancestor_id == self.editing_category_id:
                self.category_error = (
                    "Uma categoria não pode ser movida para dentro de uma "
                    "de suas subcategorias."
                )
                return
            ancestor = next(
                (item for item in self.categories if item["id"] == ancestor_id),
                None,
            )
            ancestor_id = ancestor["categoria_pai_id"] if ancestor else None

        payload = {
            "nome": name,
            "descricao": self.category_form_description.strip(),
            "categoria_pai_id": parent_id,
            "ativo": self.category_form_active == "Ativa",
            "cor": color,
        }
        category_id = self.editing_category_id
        method = "PATCH" if category_id else "POST"
        endpoint = (
            f"/categoria/{category_id}" if category_id else "/categoria"
        )
        self.is_saving_category = True
        self.category_error = ""
        self.category_notice = ""
        try:
            response = await xano.request(
                method,
                endpoint,
                payload=payload,
                auth_token=self._auth_token,
                base_url=xano.XANO_PHARMACY_API_URL,
            )
            if response.status_code not in (200, 201):
                self.category_error = xano.response_message(
                    xano.response_data(response),
                    f"Não foi possível salvar a categoria (HTTP {response.status_code}).",
                )
                return

            self.set_category_form_open(False)
            self.is_loading_categories = True
            if await self._load_categories():
                self.category_notice = "Categoria salva com sucesso."
            else:
                self.category_notice = (
                    "A categoria foi salva, mas a lista não pôde ser atualizada. "
                    "Atualize a página para confirmar os dados."
                )
        except httpx.RequestError:
            logger.warning("A gravação de categoria no Xano falhou.")
            self.category_error = "Não foi possível conectar ao Xano para salvar."
        finally:
            self.is_loading_categories = False
            self.is_saving_category = False

    @rx.event
    def request_category_delete(self, category_id: int):
        category = next(
            (item for item in self.categories if item["id"] == category_id),
            None,
        )
        if category is None:
            logger.warning("Foi solicitada a exclusão de uma categoria não carregada.")
            self.category_error = "A categoria selecionada não está disponível."
            return
        self.deleting_category_id = category_id
        self.deleting_category_name = category["nome"]
        self.category_error = ""
        self.show_category_delete_confirmation = True

    @rx.event
    def set_category_delete_confirmation_open(self, is_open: bool):
        self.show_category_delete_confirmation = is_open
        if not is_open:
            self.deleting_category_id = 0
            self.deleting_category_name = ""

    @rx.event
    async def delete_category(self):
        if not self._auth_token:
            return rx.redirect("/")
        if not self.deleting_category_id:
            self.category_error = "Selecione uma categoria válida para excluir."
            return

        self.is_deleting_category = True
        self.category_error = ""
        self.category_notice = ""
        try:
            response = await xano.request(
                "DELETE",
                f"/categoria/{self.deleting_category_id}",
                auth_token=self._auth_token,
                base_url=xano.XANO_PHARMACY_API_URL,
            )
            if response.status_code not in (200, 204):
                self.category_error = xano.response_message(
                    xano.response_data(response),
                    f"Não foi possível excluir a categoria (HTTP {response.status_code}).",
                )
                return

            self.set_category_delete_confirmation_open(False)
            self.is_loading_categories = True
            if await self._load_categories():
                self.category_notice = "Categoria excluída com sucesso."
            else:
                self.category_notice = (
                    "A categoria foi excluída, mas a lista não pôde ser "
                    "atualizada. Atualize a página para confirmar os dados."
                )
        except httpx.RequestError:
            logger.warning("A exclusão de categoria no Xano falhou.")
            self.category_error = "Não foi possível conectar ao Xano para excluir."
        finally:
            self.is_loading_categories = False
            self.is_deleting_category = False

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
            self.products = self._normalize_products(
                xano.response_data(response)
            )
        except ValueError:
            logger.error("O endpoint /produto retornou dados fora do formato esperado.")
            self.stock_error = "O Xano retornou uma lista de produtos inválida."
            return False
        return True

    @staticmethod
    def _normalize_products(data: Any) -> list[dict[str, Any]]:
        products = xano.response_records(data, "produtos")
        normalized_products = []
        for product in products:
            try:
                formatted_price = f"{float(product.get('preco', 0)):.2f}".replace(
                    ".",
                    ",",
                )
            except (TypeError, ValueError):
                formatted_price = str(product.get("preco", ""))

            normalized_products.append(
                {
                    **product,
                    "imagem_url": str(product.get("imagem_url") or ""),
                    "preco_formatado": formatted_price,
                    "categoria_id": _reference_id(product.get("categoria_id")),
                }
            )
        return normalized_products

    @rx.event
    async def load_stock(self):
        if not self._auth_token:
            return rx.redirect("/")

        self.is_loading_products = True
        self.stock_error = ""
        try:
            await self._load_products()
            await self._load_categories()
        except httpx.RequestError:
            logger.warning("A consulta de produtos no Xano falhou.")
            self.stock_error = "Não foi possível conectar ao estoque no Xano."
        finally:
            self.is_loading_products = False

    @rx.event
    def set_product_search(self, value: str):
        self.product_search = value

    @rx.event
    def set_product_category_search(self, value: str):
        self.product_category_search = value
        if value in ("", "Todas as categorias"):
            self.selected_product_category_id = ""
            return

        category = next(
            (
                category
                for category in self.categories
                if category["ativo"] and self._category_label(category) == value
            ),
            None,
        )
        if category is None:
            logger.warning("Foi selecionada uma categoria que não está carregada.")
            self.category_error = "A categoria selecionada não está disponível."
            self.product_category_search = ""
            self.selected_product_category_id = ""
            return
        self.selected_product_category_id = str(category["id"])

    @rx.event
    def set_product_form_category(self, value: str):
        if value == "Sem categoria":
            self.product_form_category_id = ""
            return

        category = next(
            (
                category
                for category in self.categories
                if category["ativo"] and self._category_label(category) == value
            ),
            None,
        )
        if category is None:
            logger.warning("Foi submetida uma categoria de produto inválida.")
            self.stock_error = "A categoria selecionada não está disponível."
            return
        self.product_form_category_id = str(category["id"])

    @rx.event
    def set_category_search(self, value: str):
        self.category_search_query = value

    @rx.event
    def clear_category_search(self):
        self.category_search_query = ""

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
    def set_product_image_url(self, value: str):
        self.product_image_url = value
        parsed_image_url = urlparse(value.strip())
        self.product_image_preview_url = (
            value.strip()
            if parsed_image_url.scheme in ("http", "https")
            and parsed_image_url.netloc
            else ""
        )
        self.stock_error = ""

    @rx.event
    def start_new_product(self):
        self.cancel_product_edit()
        self.show_product_form = True

    @rx.event
    def set_product_form_open(self, is_open: bool):
        self.show_product_form = is_open
        if not is_open:
            self.editing_product_id = 0
            self.product_form_category_id = ""
            self.product_name = ""
            self.product_barcode = ""
            self.product_price = ""
            self.product_stock = ""
            self.product_image_url = ""
            self.product_image_preview_url = ""
            self.original_product_image_url = ""

    @rx.event
    def start_product_edit(
        self,
        product_id: int,
        name: str,
        barcode: str,
        price: float,
        stock: int,
        image_url: str,
        category_id: str = "",
    ):
        self.editing_product_id = product_id
        self.product_form_category_id = str(_reference_id(category_id) or "")
        self.product_name = name
        self.product_barcode = barcode
        self.product_price = str(price)
        self.product_stock = str(stock)
        self.product_image_url = image_url
        parsed_image_url = urlparse(image_url.strip())
        self.product_image_preview_url = (
            image_url.strip()
            if parsed_image_url.scheme in ("http", "https")
            and parsed_image_url.netloc
            else ""
        )
        self.original_product_image_url = image_url
        self.show_product_form = True
        self.stock_notice = ""
        self.stock_error = ""

    @rx.event
    def cancel_product_edit(self):
        self.editing_product_id = 0
        self.product_form_category_id = ""
        self.product_name = ""
        self.product_barcode = ""
        self.product_price = ""
        self.product_stock = ""
        self.product_image_url = ""
        self.product_image_preview_url = ""
        self.original_product_image_url = ""
        self.show_product_form = False
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
        image_url = self.product_image_url.strip()
        if image_url:
            parsed_image_url = urlparse(image_url)
            if (
                parsed_image_url.scheme not in ("http", "https")
                or not parsed_image_url.netloc
            ):
                self.stock_error = "Informe uma URL válida começando com http:// ou https://."
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
            "categoria_id": _reference_id(self.product_form_category_id),
        }
        if image_url or self.original_product_image_url:
            payload["imagem_url"] = image_url
        product_id = self.editing_product_id
        image_changed = image_url != self.original_product_image_url
        endpoint = (
            f"/produto/{self.editing_product_id}"
            if self.editing_product_id
            else "/produto"
        )
        method = "PATCH" if self.editing_product_id else "POST"

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
                if image_url:
                    self.stock_error += (
                        " Confirme se o campo imagem_url foi configurado no Xano."
                    )
                return
            if not await self._load_products():
                return

            saved_product = next(
                (
                    product
                    for product in self.products
                    if (
                        int(product.get("id", 0)) == product_id
                        if product_id
                        else product.get("codigo_barras") == barcode
                    )
                ),
                None,
            )
            if image_changed and (
                saved_product is None
                or saved_product.get("imagem_url", "") != image_url
            ):
                self.stock_error = (
                    "O produto foi salvo, mas a foto não foi persistida. "
                    "Confirme o campo imagem_url e os endpoints do Xano."
                )
                return
            self.cancel_product_edit()
            self.stock_notice = "Produto salvo com sucesso."
        except httpx.RequestError:
            logger.warning("A gravação de produto no Xano falhou.")
            self.stock_error = "Não foi possível conectar ao Xano para salvar."
        finally:
            self.is_saving_product = False

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
            self.products = self._normalize_products(
                xano.response_data(products_response)
            )
            self.customers = xano.response_records(
                xano.response_data(customers_response),
                "clientes",
            )
            await self._load_categories()
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
                "preco_formatado": self._format_currency(
                    float(product.get("preco", 0))
                ),
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
        self.selected_customer = ""
        self.customer_status = "unregistered"
        self.show_cart_panel = False
        self.customer_notice = ""
        self.sales_error = ""
        self.sales_notice = ""

    @rx.event
    def set_cart_panel_open(self, value: bool):
        self.show_cart_panel = value

    @rx.event
    def set_customer_status(self, value: str):
        self.customer_status = value
        if value == "unregistered":
            self.selected_customer = ""
            self.customer_notice = ""

    @rx.event
    def set_payment_method(self, value: str):
        self.payment_method = value

    @rx.event
    async def finalize_sale(self):
        if not self._auth_token:
            return rx.redirect("/")
        if self.is_finalizing_sale:
            return
        if not self.cart:
            self.sales_error = "Adicione produtos ao carrinho antes de finalizar."
            return

        payment_methods = {
            "Dinheiro": "dinheiro",
            "PIX": "pix",
            "Crédito": "credito",
            "Débito": "debito",
        }
        payment_method = payment_methods.get(self.payment_method)
        if payment_method is None:
            self.sales_error = "Selecione uma forma de pagamento válida."
            return

        items = []
        for item in self.cart:
            try:
                product_id = int(item["produto_id"])
                quantity = int(item["quantidade"])
            except (KeyError, TypeError, ValueError):
                self.sales_error = "O carrinho contém um produto ou quantidade inválida."
                return
            if product_id < 1 or quantity < 1:
                self.sales_error = "O carrinho contém um produto ou quantidade inválida."
                return
            items.append({"produto_id": product_id, "quantidade": quantity})

        customer_id = None
        if self._is_selected_customer_registered():
            customer = self._selected_customer_record()
            customer_id = _reference_id(customer.get("id")) if customer else None
            if customer_id is None:
                self.sales_error = (
                    "Não foi possível confirmar o cliente selecionado. "
                    "Atualize a lista de clientes e tente novamente."
                )
                return

        self.is_finalizing_sale = True
        self.sales_error = ""
        self.sales_notice = ""
        try:
            response = await xano.request(
                "POST",
                "/venda/finalizar",
                auth_token=self._auth_token,
                base_url=xano.XANO_PHARMACY_API_URL,
                payload={
                    "itens": items,
                    "cliente_id": customer_id,
                    "forma_pagamento": payment_method,
                },
            )
            response_data = xano.response_data(response)
            if response.status_code not in (200, 201):
                self.sales_error = xano.response_message(
                    response_data,
                    f"Não foi possível finalizar a venda (HTTP {response.status_code}).",
                )
                return

            sale = (
                response_data.get("venda")
                if isinstance(response_data, dict)
                else None
            )
            sale_id = sale.get("id") if isinstance(sale, dict) else None
            if (
                not isinstance(response_data, dict)
                or response_data.get("success") is not True
                or isinstance(sale_id, bool)
                or not isinstance(sale_id, int)
                or sale_id < 1
            ):
                logger.error("O Xano retornou sucesso sem confirmar uma venda válida.")
                self.sales_error = xano.response_message(
                    response_data,
                    "O Xano não confirmou a venda. O carrinho foi preservado; "
                    "atualize o histórico antes de tentar novamente.",
                )
                return

            self.cart = []
            self.selected_customer = ""
            self.customer_status = "unregistered"
            self.customer_notice = ""
            self.show_cart_panel = False
            await self.load_sales()
            if self.sales_error:
                self.sales_notice = (
                    "Venda finalizada, mas não foi possível atualizar o catálogo "
                    "e o histórico. Atualize a tela antes de iniciar outra venda."
                )
                logger.error(
                    "A venda foi finalizada, mas a atualização do catálogo/histórico falhou."
                )
                return
            self.sales_notice = "Venda finalizada e estoque atualizado com sucesso."
        except httpx.RequestError:
            logger.warning("A finalização de venda no Xano falhou.")
            self.sales_error = (
                "Não foi possível confirmar a finalização no Xano. "
                "O carrinho foi preservado; atualize o histórico antes de tentar novamente."
            )
        finally:
            self.is_finalizing_sale = False

    @rx.event
    def set_selected_customer(self, value: str):
        self.selected_customer = value
        self.customer_status = "registered" if value else "unregistered"
        self.customer_notice = ""

    @rx.event
    def open_customer_form(self):
        self.customer_name = ""
        self.customer_cpf = ""
        self.customer_phone = ""
        self.customer_form_error = ""
        self.customer_status = "registered"
        self.show_customer_form = True

    @rx.event
    def set_customer_form_open(self, value: bool):
        self.show_customer_form = value

    @rx.event
    def set_customer_name(self, value: str):
        self.customer_name = value

    @rx.event
    def set_customer_cpf(self, value: str):
        self.customer_cpf = value

    @rx.event
    def set_customer_phone(self, value: str):
        self.customer_phone = value

    @staticmethod
    def _cpf_digits(value: str) -> str:
        return "".join(character for character in value if character.isdigit())

    @rx.event
    async def save_customer(self):
        name = self.customer_name.strip()
        cpf = self._cpf_digits(self.customer_cpf)
        phone = self.customer_phone.strip()
        if not name or len(cpf) != 11 or not phone:
            self.customer_form_error = (
                "Informe o nome, um CPF com 11 dígitos e o telefone."
            )
            return

        if any(
            self._cpf_digits(str(customer.get("cpf", ""))) == cpf
            for customer in self.customers
        ):
            self.customer_form_error = "Já existe um cliente cadastrado com este CPF."
            return

        self.is_saving_customer = True
        self.customer_form_error = ""
        try:
            response = await xano.request(
                "POST",
                "/cliente",
                auth_token=self._auth_token,
                base_url=xano.XANO_PHARMACY_API_URL,
                payload={
                    "nome": name,
                    "cpf": cpf,
                    "telefone": phone,
                    "esta_registrado": True,
                },
            )
            response_data = xano.response_data(response)
            if response.status_code not in (200, 201):
                self.customer_form_error = xano.response_message(
                    response_data,
                    f"Não foi possível cadastrar o cliente (HTTP {response.status_code}).",
                )
                return

            customers_response = await xano.request(
                "GET",
                "/cliente",
                auth_token=self._auth_token,
                base_url=xano.XANO_PHARMACY_API_URL,
            )
            if customers_response.status_code != 200:
                self.customer_form_error = (
                    "Cliente cadastrado, mas não foi possível atualizar a lista. "
                    "Tente atualizar a tela."
                )
                logger.error(
                    "O cliente foi criado, mas a lista /cliente não pôde ser atualizada."
                )
                return

            try:
                self.customers = xano.response_records(
                    xano.response_data(customers_response),
                    "clientes",
                )
            except ValueError:
                logger.error(
                    "O endpoint /cliente retornou uma lista inválida após o cadastro."
                )
                self.customer_form_error = (
                    "Cliente cadastrado, mas o Xano retornou uma lista inválida."
                )
                return

            self.selected_customer = f"{name} · CPF {cpf}"
            self.customer_status = "registered"
            self.customer_notice = (
                "Cliente cadastrado e selecionado; desconto de "
                f"{CUSTOMER_DISCOUNT_RATE}% aplicado ao carrinho."
            )
            self.show_customer_form = False
        except httpx.RequestError:
            logger.warning("O cadastro de cliente no Xano falhou.")
            self.customer_form_error = (
                "Não foi possível conectar ao Xano para cadastrar o cliente."
            )
        finally:
            self.is_saving_customer = False


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
            response = await xano.request(
                "GET",
                "/reset/request-reset-link",
                params={"email": email},
            )
            if response.status_code not in (200, 201):
                logger.warning(
                    "A solicitacao de redefinicao no Xano retornou HTTP %s.",
                    response.status_code,
                )
        except httpx.RequestError:
            logger.warning("A solicitacao de link de redefinicao para o Xano falhou.")

        self.is_loading = False
        self.message = (
            "Se o e-mail estiver cadastrado, enviaremos um link de recuperação. "
            "Verifique sua caixa de entrada e a pasta de spam."
        )


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
            item("Categorias", "tag", "/categorias", "categories"),
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


def product_category_search_control() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Filtrar por departamento ou categoria",
            color="#34485b",
            font_size="0.88rem",
            font_weight="700",
        ),
        rx.select(
            LoginState.product_category_options,
            value=LoginState.product_category_search,
            on_change=LoginState.set_product_category_search,
            placeholder="Todas as categorias",
            aria_label="Filtrar por departamento ou categoria",
            width="100%",
            background="white",
            color="#1f2c39",
        ),
        rx.cond(
            LoginState.category_error != "",
            rx.text(
                LoginState.category_error,
                color="#b91c1c",
                font_size="0.76rem",
                role="alert",
            ),
            rx.text(
                "O filtro usa a categoria associada ao produto e inclui as "
                "subcategorias do departamento selecionado.",
                color="#64748b",
                font_size="0.76rem",
                line_height="1.4",
            ),
        ),
        width="100%",
        spacing="2",
        align_items="stretch",
    )


def stock_page() -> rx.Component:
    def product_input(
        label: str,
        placeholder: str,
        value: rx.Var,
        on_change: Any,
        input_type: str = "text",
    ) -> rx.Component:
        return rx.vstack(
            rx.text(
                label,
                color="#34485b",
                font_size="0.9rem",
                font_weight="600",
            ),
            rx.input(
                placeholder=placeholder,
                value=value,
                on_change=on_change,
                type=input_type,
                aria_label=label,
                width="100%",
                height="48px",
                padding="0 0.9rem",
                background="#f8fafc",
                border="1px solid #cbd5e1",
                border_radius="10px",
                color="#1f2c39",
                _placeholder={"color": "#94a3b8"},
                _focus={
                    "border": "1px solid #16a34a",
                    "box_shadow": "0 0 0 3px rgba(22,163,74,0.12)",
                    "outline": "none",
                },
            ),
            width="100%",
            spacing="2",
            align_items="stretch",
        )

    def product_row(product: rx.Var) -> rx.Component:
        quantity = product["estoque_quantidade"].to(int)
        return rx.hstack(
            rx.box(
                rx.cond(
                    product["imagem_url"] != "",
                    rx.image(
                        src=product["imagem_url"],
                        alt=product["nome"],
                        width="56px",
                        height="56px",
                        object_fit="cover",
                        border_radius="10px",
                    ),
                    rx.box(
                        rx.icon("image", size=22, color="#94a3b8"),
                        width="56px",
                        height="56px",
                        background="#f1f5f9",
                        border_radius="10px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                ),
                width="12%",
                flex_shrink="0",
            ),
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
                width="38%",
                flex_shrink="0",
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
                width="16%",
                flex_shrink="0",
            ),
            rx.text(
                "R$ ",
                product["preco_formatado"],
                color="#34485b",
                font_weight="600",
                width="16%",
                flex_shrink="0",
            ),
            rx.box(
                rx.button(
                    "Editar",
                    on_click=LoginState.start_product_edit(
                        product["id"],
                        product["nome"],
                        product["codigo_barras"],
                        product["preco"],
                        quantity,
                        product["imagem_url"],
                        product["categoria_id"].to_string(),
                    ),
                    variant="outline",
                    color="#1d4ed8",
                    size="2",
                ),
                width="18%",
                flex_shrink="0",
            ),
            width="100%",
            padding="0.9rem 1rem",
            border_bottom="1px solid #e5e7eb",
            align_items="center",
            spacing="0",
            min_width="700px",
        )

    content = rx.vstack(
        rx.vstack(
            rx.text(
                "Pesquisar produtos",
                color="#34485b",
                font_size="0.9rem",
                font_weight="700",
            ),
            rx.hstack(
                rx.icon("search", size=19, color="#475569"),
                rx.input(
                    placeholder="Nome ou código de barras",
                    value=LoginState.product_search,
                    on_change=LoginState.set_product_search,
                    aria_label="Pesquisar produtos por nome ou código de barras",
                    width="100%",
                    height="48px",
                    padding="0 0.2rem",
                    color="#1f2c39",
                    border="none",
                    outline="none",
                    background="transparent",
                    _placeholder={"color": "#64748b", "opacity": "1"},
                    _focus={"box_shadow": "none"},
                ),
                width="100%",
                min_height="54px",
                padding="0 0.9rem",
                background="#ffffff",
                border="1px solid #94a3b8",
                border_radius="12px",
                box_shadow="0 2px 6px rgba(15,23,42,0.06)",
                spacing="3",
                align_items="center",
                _focus_within={
                    "border": "1px solid #16a34a",
                    "box_shadow": "0 0 0 3px rgba(22,163,74,0.14)",
                },
            ),
            width="100%",
            max_width="620px",
            spacing="2",
            align_items="stretch",
        ),
        product_category_search_control(),
        rx.hstack(
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=17),
                "Incluir produto",
                on_click=LoginState.start_new_product,
                background="#16a34a",
                color="white",
                border_radius="10px",
                padding="0.8rem 1rem",
            ),
            width="100%",
        ),
        rx.cond(
            (LoginState.stock_error != "")
            & (LoginState.show_product_form == False),
            rx.text(LoginState.stock_error, color="#dc2626", role="alert"),
            rx.fragment(),
        ),
        rx.cond(
            LoginState.stock_notice != "",
            rx.text(LoginState.stock_notice, color="#16a34a", role="status"),
            rx.fragment(),
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.hstack(
                    rx.vstack(
                        rx.dialog.title(
                            rx.cond(
                                LoginState.editing_product_id > 0,
                                "Editar produto",
                                "Incluir produto",
                            ),
                            color="#1f2c39",
                            font_size="1.35rem",
                            font_weight="700",
                        ),
                        rx.dialog.description(
                            "Preencha os dados abaixo para manter seu estoque atualizado.",
                            color="#64748b",
                            font_size="0.9rem",
                        ),
                        align_items="flex-start",
                        spacing="1",
                    ),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=18),
                            variant="ghost",
                            color="#64748b",
                            aria_label="Fechar formulário",
                        )
                    ),
                    width="100%",
                    justify="between",
                    align_items="flex-start",
                    margin_bottom="0.5rem",
                ),
                rx.cond(
                    LoginState.stock_error != "",
                    rx.text(
                        LoginState.stock_error,
                        color="#b91c1c",
                        background="#fef2f2",
                        padding="0.75rem 0.9rem",
                        border="1px solid #fecaca",
                        border_radius="10px",
                        font_size="0.88rem",
                        role="alert",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                rx.hstack(
                    product_input(
                        "Nome do produto",
                        "Ex.: Paracetamol 750 mg",
                        LoginState.product_name,
                        LoginState.set_product_name,
                    ),
                    product_input(
                        "Código de barras",
                        "Digite o código de barras",
                        LoginState.product_barcode,
                        LoginState.set_product_barcode,
                    ),
                    width="100%",
                    spacing="4",
                    flex_wrap="wrap",
                ),
                rx.hstack(
                    product_input(
                        "Preço (R$)",
                        "Ex.: 12,50",
                        LoginState.product_price,
                        LoginState.set_product_price,
                        "number",
                    ),
                    product_input(
                        "Quantidade em estoque",
                        "Ex.: 25",
                        LoginState.product_stock,
                        LoginState.set_product_stock,
                        "number",
                    ),
                    width="100%",
                    spacing="4",
                    flex_wrap="wrap",
                ),
                rx.vstack(
                    rx.text(
                        "Categoria do produto",
                        color="#34485b",
                        font_size="0.88rem",
                        font_weight="700",
                    ),
                    rx.select(
                        LoginState.product_form_category_options,
                        value=LoginState.product_form_category_label,
                        on_change=LoginState.set_product_form_category,
                        aria_label="Categoria do produto",
                        width="100%",
                        background="white",
                        color="#1f2c39",
                    ),
                    width="100%",
                    spacing="2",
                    align_items="stretch",
                ),
                product_input(
                    "Foto do produto (opcional)",
                    "Cole aqui a URL da imagem",
                    LoginState.product_image_url,
                    LoginState.set_product_image_url,
                    "url",
                ),
                rx.cond(
                    LoginState.product_image_preview_url != "",
                    rx.vstack(
                        rx.text(
                            "Pré-visualização da foto",
                            color="#34485b",
                            font_size="0.85rem",
                            font_weight="600",
                        ),
                        rx.image(
                            src=LoginState.product_image_preview_url,
                            alt="Pré-visualização da foto do produto",
                            width="128px",
                            height="128px",
                            object_fit="contain",
                            background="#f8fafc",
                            border="1px solid #e2e8f0",
                            border_radius="12px",
                            padding="0.4rem",
                        ),
                        width="100%",
                        spacing="2",
                        align_items="flex-start",
                    ),
                    rx.fragment(),
                ),
                rx.text(
                    "A foto aparece aqui pela URL informada. Para mantê-la após salvar, o Xano precisa aceitar e armazenar imagem_url.",
                    color="#64748b",
                    font_size="0.8rem",
                    margin_top="-0.5rem",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="outline",
                            color="#475569",
                            border_color="#cbd5e1",
                            height="44px",
                            padding="0 1.2rem",
                        )
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
                        height="44px",
                        padding="0 1.3rem",
                        border_radius="10px",
                        _hover={"background": "#15803d"},
                    ),
                    width="100%",
                    justify="end",
                    spacing="3",
                    margin_top="0.5rem",
                ),
                width="min(92vw, 620px)",
                max_height="90vh",
                overflow_y="auto",
                padding="1.6rem",
                background="white",
                border="1px solid #e2e8f0",
                border_radius="18px",
                box_shadow="0 24px 80px rgba(15,23,42,0.24)",
                spacing="4",
            ),
            open=LoginState.show_product_form,
            on_open_change=LoginState.set_product_form_open,
        ),
        rx.vstack(
            rx.hstack(
                rx.text("Foto", width="12%", font_weight="700", color="#475569"),
                rx.text("Produto", width="38%", font_weight="700", color="#475569"),
                rx.text("Quantidade", width="16%", font_weight="700", color="#475569"),
                rx.text("Preço", width="16%", font_weight="700", color="#475569"),
                rx.text("Ação", width="18%", font_weight="700", color="#475569"),
                width="100%",
                min_width="700px",
                padding="0.9rem 1rem",
                border_bottom="1px solid #e5e7eb",
                align_items="center",
                spacing="0",
            ),
            rx.cond(
                LoginState.is_loading_products,
                rx.text(
                    "Carregando produtos do Xano...",
                    color="#64748b",
                    padding="1rem",
                ),
                rx.fragment(),
            ),
            rx.foreach(LoginState.filtered_products, product_row),
            rx.cond(
                (LoginState.filtered_products.length() == 0)
                & (LoginState.is_loading_products == False),
                rx.text(
                    rx.cond(
                        LoginState.products.length() == 0,
                        "Ainda não há produtos cadastrados no Xano.",
                        "Nenhum produto encontrado para essa busca.",
                    ),
                    color="#64748b",
                    padding="1rem",
                ),
                rx.fragment(),
            ),
            width="100%",
            min_width="700px",
            background="white",
            border="1px solid #e5e7eb",
            border_radius="16px",
            overflow="auto",
            align_items="stretch",
            spacing="0",
        ),
        width="100%",
        spacing="4",
        align_items="stretch",
    )
    return management_page_shell("stock", "Gestão de Estoque", content)


def categories_page() -> rx.Component:
    def category_form_input(
        label: str,
        placeholder: str,
        value: rx.Var,
        on_change: Any,
    ) -> rx.Component:
        return rx.vstack(
            rx.text(
                label,
                color="#34485b",
                font_size="0.88rem",
                font_weight="700",
            ),
            rx.input(
                placeholder=placeholder,
                value=value,
                on_change=on_change,
                aria_label=label,
                width="100%",
                height="46px",
                padding="0 0.8rem",
                background="#f8fafc",
                border="1px solid #cbd5e1",
                border_radius="10px",
                color="#1f2c39",
                _focus={
                    "border": "1px solid #16a34a",
                    "box_shadow": "0 0 0 3px rgba(22,163,74,0.12)",
                    "outline": "none",
                },
            ),
            width="100%",
            spacing="2",
            align_items="stretch",
        )

    def subcategory_chip(category: rx.Var) -> rx.Component:
        return rx.hstack(
            rx.text(
                category["nome"],
                color="#475569",
                font_size="0.82rem",
                line_height="1.3",
            ),
            rx.cond(
                category["ativo"],
                rx.badge("Ativa", color_scheme="green", variant="soft"),
                rx.badge("Inativa", color_scheme="gray", variant="soft"),
            ),
            rx.icon_button(
                rx.icon("pencil", size=13),
                on_click=LoginState.start_category_edit(category["id"]),
                aria_label=rx.cond(
                    category["ativo"],
                    "Editar categoria " + category["nome"],
                    "Editar categoria inativa " + category["nome"],
                ),
                size="1",
                variant="ghost",
                color="#475569",
            ),
            rx.icon_button(
                rx.icon("trash-2", size=13),
                on_click=LoginState.request_category_delete(category["id"]),
                aria_label="Excluir categoria " + category["nome"],
                size="1",
                variant="ghost",
                color="#b91c1c",
            ),
            width="fit-content",
            padding="0.35rem 0.45rem 0.35rem 0.7rem",
            background="#f8fafc",
            border="1px solid #e2e8f0",
            border_radius="12px",
            align_items="center",
            spacing="2",
        )

    def category_group_card(group: rx.Var) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("shapes", size=22, color="#1f2937"),
                    width="48px",
                    height="48px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    background=group["cor"],
                    border_radius="15px",
                ),
                rx.vstack(
                    rx.text(
                        "DEPARTAMENTO",
                        color="#64748b",
                        font_size="0.68rem",
                        font_weight="700",
                        letter_spacing="0.08em",
                    ),
                    rx.heading(
                        group["nome"],
                        color="#1f2c39",
                        size="4",
                    ),
                    rx.cond(
                        group["ativo"],
                        rx.badge("Ativo", color_scheme="green", variant="soft"),
                        rx.badge("Inativo", color_scheme="gray", variant="soft"),
                    ),
                    align_items="flex-start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.icon_button(
                    rx.icon("pencil", size=16),
                    on_click=LoginState.start_category_edit(group["id"]),
                    aria_label="Editar categoria " + group["nome"],
                    variant="outline",
                    color="#1d4ed8",
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=16),
                    on_click=LoginState.request_category_delete(group["id"]),
                    aria_label="Excluir categoria " + group["nome"],
                    variant="outline",
                    color="#b91c1c",
                ),
                width="100%",
                align_items="center",
                spacing="3",
            ),
            rx.text(
                group["descricao"],
                color="#64748b",
                font_size="0.88rem",
                line_height="1.5",
                width="100%",
            ),
            rx.hstack(
                rx.foreach(group["subcategorias"], subcategory_chip),
                width="100%",
                flex_wrap="wrap",
                align_items="center",
                spacing="2",
            ),
            width="100%",
            padding="1.2rem",
            background="white",
            border="1px solid #e5e7eb",
            border_radius="16px",
            align_items="stretch",
            spacing="3",
            box_shadow="0 4px 14px rgba(15,23,42,0.04)",
            _hover={
                "border_color": "#cbd5e1",
                "box_shadow": "0 10px 24px rgba(15,23,42,0.07)",
            },
        )

    content = rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text(
                    "Navegue por departamentos e encontre os grupos de produtos da farmácia.",
                    color="#64748b",
                    font_size="0.95rem",
                    line_height="1.6",
                ),
                rx.text(
                    "Uma visão organizada para facilitar a consulta do catálogo.",
                    color="#64748b",
                    font_size="0.88rem",
                ),
                align_items="flex-start",
                spacing="1",
            ),
            rx.spacer(),
            rx.vstack(
                rx.hstack(
                    rx.icon("layers-3", size=17, color="#15803d"),
                    rx.text(
                        LoginState.filtered_categories.length(),
                        " departamentos",
                        color="#166534",
                        font_size="0.85rem",
                        font_weight="700",
                    ),
                    rx.text("·", color="#94a3b8"),
                    rx.text(
                        LoginState.filtered_subcategory_count,
                        " subcategorias",
                        color="#166534",
                        font_size="0.85rem",
                        font_weight="700",
                    ),
                    padding="0.65rem 0.85rem",
                    background="#f0fdf4",
                    border="1px solid #bbf7d0",
                    border_radius="999px",
                    align_items="center",
                    spacing="2",
                ),
                rx.button(
                    rx.icon("plus", size=16),
                    "Nova categoria",
                    on_click=LoginState.start_new_category,
                    background="#16a34a",
                    color="white",
                    border_radius="10px",
                    padding="0.75rem 1rem",
                    _hover={"background": "#15803d"},
                ),
                width="100%",
                align_items=["flex-start", "flex-end"],
                spacing="3",
            ),
            width="100%",
            align_items=["flex-start", "center"],
            flex_wrap="wrap",
            spacing="4",
        ),
        rx.hstack(
            rx.icon("search", size=18, color="#64748b"),
            rx.input(
                placeholder="Buscar departamento ou subcategoria",
                value=LoginState.category_search_query,
                on_change=LoginState.set_category_search,
                aria_label="Buscar departamento ou subcategoria",
                width="100%",
                height="48px",
                border="none",
                outline="none",
                background="transparent",
                color="#1f2c39",
                _placeholder={"color": "#64748b"},
                _focus={"box_shadow": "none"},
            ),
            width="100%",
            max_width="680px",
            min_height="52px",
            padding="0 0.9rem",
            background="white",
            border="1px solid #cbd5e1",
            border_radius="12px",
            spacing="3",
            align_items="center",
            _focus_within={
                "border": "1px solid #16a34a",
                "box_shadow": "0 0 0 3px rgba(22,163,74,0.12)",
            },
        ),
        rx.cond(
            LoginState.is_loading_categories,
            rx.text(
                "Carregando categorias do Xano...",
                color="#64748b",
                role="status",
            ),
            rx.fragment(),
        ),
        rx.cond(
            LoginState.category_error != "",
            rx.text(LoginState.category_error, color="#b91c1c", role="alert"),
            rx.fragment(),
        ),
        rx.cond(
            LoginState.category_notice != "",
            rx.text(LoginState.category_notice, color="#15803d", role="status"),
            rx.fragment(),
        ),
        rx.callout(
            "Departamentos e subcategorias são carregados do Xano. A categoria "
            "selecionada no cadastro de produto fica associada ao produto.",
            icon="info",
            color_scheme="blue",
            width="100%",
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.hstack(
                    rx.vstack(
                        rx.dialog.title(
                            rx.cond(
                                LoginState.editing_category_id > 0,
                                "Editar categoria",
                                "Nova categoria",
                            ),
                            color="#1f2c39",
                            font_size="1.3rem",
                            font_weight="700",
                        ),
                        rx.dialog.description(
                            "Gerencie o catálogo persistido no Xano.",
                            color="#64748b",
                            font_size="0.9rem",
                        ),
                        align_items="flex-start",
                        spacing="1",
                    ),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=18),
                            variant="ghost",
                            color="#64748b",
                            aria_label="Fechar formulário de categoria",
                        )
                    ),
                    width="100%",
                    justify="between",
                    align_items="flex-start",
                ),
                rx.cond(
                    LoginState.category_error != "",
                    rx.text(
                        LoginState.category_error,
                        color="#b91c1c",
                        background="#fef2f2",
                        padding="0.75rem 0.9rem",
                        border="1px solid #fecaca",
                        border_radius="10px",
                        font_size="0.88rem",
                        role="alert",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                category_form_input(
                    "Nome",
                    "Ex.: Medicamentos",
                    LoginState.category_form_name,
                    LoginState.set_category_form_name,
                ),
                category_form_input(
                    "Descrição",
                    "Descrição do departamento ou subcategoria",
                    LoginState.category_form_description,
                    LoginState.set_category_form_description,
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "Departamento pai",
                            color="#34485b",
                            font_size="0.88rem",
                            font_weight="700",
                        ),
                        rx.select(
                            LoginState.category_parent_options,
                            value=LoginState.category_form_parent_label,
                            on_change=LoginState.set_category_form_parent,
                            aria_label="Departamento pai",
                            width="100%",
                            background="white",
                            color="#1f2c39",
                        ),
                        width="100%",
                        align_items="stretch",
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text(
                            "Status",
                            color="#34485b",
                            font_size="0.88rem",
                            font_weight="700",
                        ),
                        rx.select(
                            ["Ativa", "Inativa"],
                            value=LoginState.category_form_active,
                            on_change=LoginState.set_category_form_active,
                            aria_label="Status da categoria",
                            width="100%",
                            background="white",
                            color="#1f2c39",
                        ),
                        width="100%",
                        align_items="stretch",
                        spacing="2",
                    ),
                    width="100%",
                    flex_wrap="wrap",
                    spacing="4",
                ),
                category_form_input(
                    "Cor (hexadecimal)",
                    "#e2e8f0",
                    LoginState.category_form_color,
                    LoginState.set_category_form_color,
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="outline",
                            color="#475569",
                            border_color="#cbd5e1",
                            height="44px",
                            padding="0 1.2rem",
                        )
                    ),
                    rx.button(
                        rx.cond(
                            LoginState.is_saving_category,
                            "Salvando...",
                            "Salvar categoria",
                        ),
                        on_click=LoginState.save_category,
                        loading=LoginState.is_saving_category,
                        disabled=LoginState.is_saving_category,
                        background="#16a34a",
                        color="white",
                        height="44px",
                        padding="0 1.2rem",
                        border_radius="10px",
                    ),
                    width="100%",
                    justify="end",
                    spacing="3",
                ),
                width="min(92vw, 560px)",
                max_height="90vh",
                overflow_y="auto",
                padding="1.4rem",
                background="white",
                border_radius="18px",
                spacing="4",
            ),
            open=LoginState.show_category_form,
            on_open_change=LoginState.set_category_form_open,
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(
                    "Excluir categoria",
                    color="#1f2c39",
                    font_size="1.2rem",
                    font_weight="700",
                ),
                rx.dialog.description(
                    "Tem certeza de que deseja excluir ",
                    rx.text(
                        LoginState.deleting_category_name,
                        as_="span",
                        font_weight="700",
                    ),
                    "? A operação pode ser recusada pelo Xano se houver produtos "
                    "ou subcategorias vinculados.",
                    color="#64748b",
                    font_size="0.9rem",
                ),
                rx.cond(
                    LoginState.category_error != "",
                    rx.text(
                        LoginState.category_error,
                        color="#b91c1c",
                        background="#fef2f2",
                        padding="0.75rem 0.9rem",
                        border="1px solid #fecaca",
                        border_radius="10px",
                        font_size="0.88rem",
                        role="alert",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="outline",
                            color="#475569",
                            border_color="#cbd5e1",
                        )
                    ),
                    rx.button(
                        rx.cond(
                            LoginState.is_deleting_category,
                            "Excluindo...",
                            "Excluir",
                        ),
                        on_click=LoginState.delete_category,
                        loading=LoginState.is_deleting_category,
                        disabled=LoginState.is_deleting_category,
                        background="#dc2626",
                        color="white",
                    ),
                    width="100%",
                    justify="end",
                    spacing="3",
                ),
                width="min(92vw, 460px)",
                padding="1.4rem",
                background="white",
                border_radius="18px",
                spacing="4",
            ),
            open=LoginState.show_category_delete_confirmation,
            on_open_change=LoginState.set_category_delete_confirmation_open,
        ),
        rx.grid(
            rx.foreach(LoginState.filtered_categories, category_group_card),
            columns="repeat(auto-fit, minmax(min(100%, 360px), 1fr))",
            gap="1rem",
            width="100%",
        ),
        rx.cond(
            (LoginState.filtered_categories.length() == 0)
            & (LoginState.is_loading_categories == False)
            & (LoginState.category_error == ""),
            rx.text(
                "Nenhuma categoria encontrada.",
                color="#64748b",
                padding="1rem 0",
                role="status",
            ),
            rx.fragment(),
        ),
        rx.hstack(
            rx.text(
                "Classificação inspirada na organização pública de categorias da ",
                color="#64748b",
                font_size="0.78rem",
            ),
            rx.link(
                "Drogasil",
                href="https://www.drogasil.com.br/categorias",
                color="#15803d",
                font_size="0.78rem",
                font_weight="600",
                text_decoration="underline",
            ),
            rx.text(
                "; nomes e grupos foram adaptados para este projeto.",
                color="#64748b",
                font_size="0.78rem",
            ),
            width="100%",
            flex_wrap="wrap",
            spacing="1",
        ),
        width="100%",
        spacing="4",
        align_items="stretch",
    )
    return management_page_shell("categories", "Categorias", content)


def sales_page() -> rx.Component:
    def catalog_row(product: rx.Var) -> rx.Component:
        return rx.vstack(
            rx.cond(
                product["imagem_url"] != "",
                rx.image(
                    src=product["imagem_url"],
                    alt=product["nome"],
                    width="100%",
                    height="150px",
                    object_fit="contain",
                    background="#f8fafc",
                    border_radius="12px",
                ),
                rx.box(
                    rx.icon("pill", size=34, color="#16a34a"),
                    width="100%",
                    height="150px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    background="#f0fdf4",
                    border_radius="12px",
                ),
            ),
            rx.vstack(
                rx.text(
                    product["nome"],
                    color="#1f2c39",
                    font_weight="700",
                    font_size="1rem",
                ),
                rx.text("R$ ", product["preco_formatado"], color="#16a34a", font_size="1.15rem", font_weight="800"),
                rx.text("Disponível: ", product["estoque_quantidade"], color="#64748b", font_size="0.82rem"),
                rx.text(
                    product["cart_status"],
                    color=product["cart_status_color"],
                    font_size="0.82rem",
                    font_weight="600",
                ),
                align_items="flex-start",
                spacing="2",
                width="100%",
            ),
            rx.button(
                rx.icon("plus", size=16),
                "Adicionar",
                on_click=LoginState.add_to_cart(product["id"]),
                size="3",
                background="#16a34a",
                color="white",
                width="100%",
            ),
            width="100%",
            padding="1rem",
            background="white",
            border="1px solid #e5e7eb",
            border_radius="16px",
            align_items="stretch",
            spacing="3",
            min_width="0",
            max_width="100%",
            _hover={"box_shadow": "0 8px 24px rgba(15,23,42,0.08)", "border_color": "#86efac"},
        )

    def cart_row(item: rx.Var) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.text(
                    item["nome"],
                    color="#1f2c39",
                    font_weight="600",
                    flex="1",
                    min_width="0",
                    white_space="normal",
                ),
                width="100%",
                align_items="flex-start",
            ),
            rx.hstack(
                rx.text(
                    "R$ ",
                    item["preco_formatado"],
                    " cada",
                    color="#64748b",
                    font_size="0.8rem",
                    flex="1",
                    min_width="0",
                ),
                rx.hstack(
                    rx.button(
                        "−",
                        on_click=LoginState.change_cart_quantity(item["produto_id"], -1),
                        variant="outline",
                        size="1",
                        min_width="32px",
                        padding="0",
                    ),
                    rx.text(
                        item["quantidade"],
                        color="#1f2c39",
                        font_weight="700",
                        min_width="20px",
                        text_align="center",
                    ),
                    rx.button(
                        "+",
                        on_click=LoginState.change_cart_quantity(item["produto_id"], 1),
                        variant="outline",
                        size="1",
                        min_width="32px",
                        padding="0",
                    ),
                    align_items="center",
                    spacing="1",
                    flex_shrink="0",
                ),
                width="100%",
                align_items="center",
                spacing="2",
            ),
            width="100%",
            min_width="0",
            padding="0.7rem",
            align_items="stretch",
            spacing="2",
            border_bottom="1px solid #e5e7eb",
        )

    def sale_row(sale: rx.Var) -> rx.Component:
        return rx.hstack(
            rx.text(
                "#",
                sale["id"],
                color="#1f2c39",
                font_weight="700",
                width=["100%", "16%"],
            ),
            rx.text(
                "Cliente: ",
                sale["cliente_id"],
                color="#64748b",
                width=["100%", "24%"],
            ),
            rx.text("R$ ", sale["valor_total"], color="#1f2c39", width=["100%", "24%"]),
            rx.text(sale["forma_pagamento"], color="#475569", width=["100%", "20%"]),
            rx.text(sale["criado_em"], color="#64748b", font_size="0.82rem", width=["100%", "16%"]),
            width="100%",
            padding="0.85rem 1rem",
            border_bottom="1px solid #e5e7eb",
            align_items="center",
            flex_wrap="wrap",
        )

    content = rx.vstack(
        rx.hstack(
            rx.spacer(),
            rx.dialog.root(
                rx.dialog.trigger(
                    rx.button(
                        rx.icon("history", size=17),
                        "Histórico",
                        variant="outline",
                        color="#15803d",
                        border_color="#86efac",
                        background="white",
                    )
                ),
                rx.dialog.content(
                    rx.vstack(
                        rx.hstack(
                            rx.dialog.title(
                                "Histórico de vendas",
                                color="#1f2c39",
                                size="4",
                            ),
                            rx.spacer(),
                            rx.dialog.close(
                                rx.button(
                                    rx.icon("x", size=18),
                                    variant="ghost",
                                    color="#64748b",
                                    aria_label="Fechar histórico",
                                )
                            ),
                            width="100%",
                            align_items="center",
                        ),
                        rx.hstack(
                            rx.text("Venda", width=["100%", "16%"], font_weight="700", color="#475569"),
                            rx.text("Cliente", width=["100%", "24%"], font_weight="700", color="#475569"),
                            rx.text("Total", width=["100%", "24%"], font_weight="700", color="#475569"),
                            rx.text("Pagamento", width=["100%", "20%"], font_weight="700", color="#475569"),
                            rx.text("Data", width=["100%", "16%"], font_weight="700", color="#475569"),
                            width="100%",
                            padding="0.9rem 1rem",
                            border_bottom="1px solid #e5e7eb",
                            flex_wrap="wrap",
                        ),
                        rx.foreach(LoginState.sales, sale_row),
                        rx.cond(
                            LoginState.is_loading_sales,
                            rx.text(
                                "Carregando histórico do Xano...",
                                color="#64748b",
                                padding="1rem",
                            ),
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
                        rx.hstack(
                            rx.spacer(),
                            rx.button(
                                "Atualizar",
                                on_click=LoginState.load_sales,
                                loading=LoginState.is_loading_sales,
                                variant="outline",
                            ),
                            width="100%",
                        ),
                        width="100%",
                        padding="0.25rem",
                        spacing="2",
                        align_items="stretch",
                    ),
                    width="min(94vw, 900px)",
                    max_height="85vh",
                    overflow_y="auto",
                    padding="1.4rem",
                    background="white",
                    border="1px solid #e2e8f0",
                    border_radius="18px",
                    box_shadow="0 24px 80px rgba(15,23,42,0.24)",
                ),
            ),
            width="100%",
            align_items="center",
        ),
        rx.cond(
            LoginState.sales_error != "",
            rx.text(LoginState.sales_error, color="#dc2626", role="alert"),
            rx.fragment(),
        ),
        rx.cond(
            LoginState.sales_notice != "",
            rx.text(LoginState.sales_notice, color="#15803d", role="status"),
            rx.fragment(),
        ),
        rx.hstack(
            rx.vstack(
                rx.heading("Catálogo", color="#1f2c39", size="4"),
                rx.input(
                    placeholder="Buscar por nome ou código de barras",
                    value=LoginState.product_search,
                    on_change=LoginState.set_product_search,
                    width="100%",
                    background="white",
                ),
                product_category_search_control(),
                rx.grid(
                    rx.foreach(LoginState.filtered_products, catalog_row),
                    columns="repeat(auto-fill, minmax(min(100%, 210px), 1fr))",
                    gap="1rem",
                    width="100%",
                    padding="0.15rem",
                    min_width="0",
                ),
                rx.cond(
                    (LoginState.filtered_products.length() == 0)
                    & (LoginState.is_loading_sales == False),
                    rx.text(
                        "Nenhum produto encontrado no catálogo.",
                        color="#64748b",
                        padding="1rem 0",
                    ),
                    rx.fragment(),
                ),
                width="100%",
                min_width="0",
                padding="1.2rem",
                background="white",
                border="1px solid #e5e7eb",
                border_radius="16px",
                spacing="3",
                align_items="stretch",
            ),
            width="100%",
            align_items="stretch",
            spacing="4",
        ),
        rx.cond(
            LoginState.cart.length() > 0,
            rx.dialog.root(
                rx.dialog.trigger(
                    rx.button(
                        rx.icon("shopping-cart", size=21),
                        rx.text("Ver carrinho", display=["none", "block"]),
                        rx.text(
                            "R$ ",
                            LoginState.cart_final_total_formatted,
                            font_weight="800",
                            font_size="1.05rem",
                        ),
                        rx.badge(
                            LoginState.cart_item_count,
                            color_scheme="green",
                            variant="solid",
                            border_radius="999px",
                        ),
                        position="fixed",
                        right="24px",
                        bottom="24px",
                        z_index="1000",
                        background="#16a34a",
                        color="white",
                        border_radius="999px",
                        padding="0.9rem 1.2rem",
                        height="58px",
                        box_shadow="0 12px 32px rgba(22,163,74,0.35)",
                        _hover={"background": "#15803d", "transform": "translateY(-2px)"},
                    )
                ),
                rx.dialog.content(
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.dialog.title(
                                    "Seu carrinho",
                                    color="#1f2c39",
                                    font_size="1.35rem",
                                    font_weight="700",
                                ),
                                rx.text(
                                    "Itens selecionados: ",
                                    LoginState.cart_item_count,
                                    color="#64748b",
                                    font_size="0.88rem",
                                ),
                                align_items="flex-start",
                                spacing="1",
                            ),
                            rx.dialog.close(
                                rx.button(
                                    rx.icon("x", size=18),
                                    variant="ghost",
                                    color="#64748b",
                                    aria_label="Fechar carrinho",
                                    on_click=LoginState.set_cart_panel_open(False),
                                )
                            ),
                            width="100%",
                            justify="between",
                        ),
                        rx.vstack(
                            rx.foreach(LoginState.cart, cart_row),
                            width="100%",
                            align_items="stretch",
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text(
                                "Identificação do cliente (opcional)",
                                color="#475569",
                                font_weight="700",
                                font_size="0.9rem",
                            ),
                            rx.grid(
                                rx.button(
                                    rx.icon("user-round-plus", size=14),
                                    "Criar cadastro",
                                    on_click=LoginState.open_customer_form,
                                    variant="outline",
                                    color="#15803d",
                                    border_color="#86efac",
                                    size="2",
                                    width="100%",
                                    min_width="0",
                                    padding="0.4rem 0.25rem",
                                    font_size="0.75rem",
                                    white_space="normal",
                                    line_height="1.15",
                                ),
                                rx.button(
                                    rx.icon("user-round-check", size=14),
                                    "Cliente cadastrado",
                                    on_click=LoginState.set_customer_status("registered"),
                                    variant=rx.cond(
                                        LoginState.customer_status == "registered",
                                        "solid",
                                        "outline",
                                    ),
                                    background=rx.cond(
                                        LoginState.customer_status == "registered",
                                        "#16a34a",
                                        "white",
                                    ),
                                    color=rx.cond(
                                        LoginState.customer_status == "registered",
                                        "white",
                                        "#475569",
                                    ),
                                    size="2",
                                    width="100%",
                                    min_width="0",
                                    padding="0.4rem 0.25rem",
                                    font_size="0.75rem",
                                    white_space="normal",
                                    line_height="1.15",
                                ),
                                columns="repeat(2, minmax(0, 1fr))",
                                gap="0.5rem",
                                width="100%",
                                min_width="0",
                            ),
                            rx.cond(
                                LoginState.customer_status == "registered",
                                rx.vstack(
                                    rx.select(
                                        LoginState.customer_options,
                                        value=LoginState.selected_customer,
                                        on_change=LoginState.set_selected_customer,
                                        placeholder="Selecione o cliente cadastrado",
                                        width="100%",
                                        color="#111827",
                                        background="white",
                                        _placeholder={"color": "#111827"},
                                    ),
                                    rx.cond(
                                        LoginState.selected_customer_is_registered,
                                        rx.text(
                                            f"Desconto de {CUSTOMER_DISCOUNT_RATE}% aplicado.",
                                            color="#15803d",
                                            font_size="0.86rem",
                                            font_weight="600",
                                            role="status",
                                        ),
                                        rx.text(
                                            "Selecione um cliente para aplicar o desconto.",
                                            color="#64748b",
                                            font_size="0.86rem",
                                        ),
                                    ),
                                    width="100%",
                                    align_items="stretch",
                                    spacing="2",
                                ),
                                rx.text(
                                    "Compra sem identificação de cliente.",
                                    color="#64748b",
                                    font_size="0.86rem",
                                ),
                            ),
                            rx.text(
                                "Você pode continuar sem selecionar um cliente.",
                                color="#64748b",
                                font_size="0.76rem",
                            ),
                            width="100%",
                            min_width="0",
                            padding="0.75rem",
                            background="#f8fafc",
                            border="1px solid #e2e8f0",
                            border_radius="12px",
                            align_items="stretch",
                            spacing="2",
                        ),
                        rx.cond(
                            LoginState.customer_notice != "",
                            rx.text(LoginState.customer_notice, color="#15803d", role="status"),
                            rx.fragment(),
                        ),
                        rx.hstack(
                            rx.text("Subtotal", color="#475569"),
                            rx.spacer(),
                            rx.text(
                                "R$ ",
                                LoginState.cart_total_formatted,
                                color="#1f2c39",
                                font_weight="600",
                            ),
                            width="100%",
                        ),
                        rx.cond(
                            LoginState.selected_customer_is_registered,
                            rx.hstack(
                                rx.text(
                                    f"Desconto ({CUSTOMER_DISCOUNT_RATE}%)",
                                    color="#15803d",
                                    font_weight="600",
                                ),
                                rx.spacer(),
                                rx.text(
                                    "− R$ ",
                                    LoginState.cart_discount_formatted,
                                    color="#15803d",
                                    font_weight="700",
                                ),
                                width="100%",
                            ),
                            rx.fragment(),
                        ),
                        rx.hstack(
                            rx.text("Total", color="#475569", font_weight="700"),
                            rx.spacer(),
                            rx.text(
                                "R$ ",
                                LoginState.cart_final_total_formatted,
                                color="#1f2c39",
                                font_size="1.35rem",
                                font_weight="800",
                            ),
                            width="100%",
                            padding_top="0.8rem",
                            border_top="1px solid #e5e7eb",
                        ),
                        rx.text("Forma de pagamento", color="#475569", font_weight="600"),
                        rx.select(
                            ["Dinheiro", "PIX", "Crédito", "Débito"],
                            value=LoginState.payment_method,
                            on_change=LoginState.set_payment_method,
                            width="100%",
                            color="#111827",
                            background="white",
                        ),
                        rx.cond(
                            LoginState.sales_error != "",
                            rx.text(
                                LoginState.sales_error,
                                color="#b91c1c",
                                background="#fef2f2",
                                padding="0.75rem",
                                border="1px solid #fecaca",
                                border_radius="10px",
                                font_size="0.84rem",
                                role="alert",
                            ),
                            rx.fragment(),
                        ),
                        rx.hstack(
                            rx.button(
                                "Limpar carrinho",
                                on_click=LoginState.clear_cart,
                                variant="outline",
                                width="100%",
                                disabled=LoginState.is_finalizing_sale,
                            ),
                            rx.button(
                                rx.cond(
                                    LoginState.is_finalizing_sale,
                                    "Finalizando...",
                                    "Finalizar venda",
                                ),
                                on_click=LoginState.finalize_sale,
                                loading=LoginState.is_finalizing_sale,
                                disabled=LoginState.is_finalizing_sale
                                | (LoginState.cart.length() == 0),
                                width="100%",
                                background="#16a34a",
                                color="white",
                            ),
                            width="100%",
                            flex_wrap="wrap",
                        ),
                        width="100%",
                        spacing="3",
                        align_items="stretch",
                    ),
                    width="min(94vw, 460px)",
                    max_height="min(90vh, 820px)",
                    overflow_y="auto",
                    padding="1.4rem",
                    background="white",
                    border="1px solid #e2e8f0",
                    border_radius="18px",
                    box_shadow="0 24px 80px rgba(15,23,42,0.24)",
                    position="fixed",
                    top="auto",
                    right="16px",
                    bottom="16px",
                    left="auto",
                    transform="none",
                ),
                open=LoginState.show_cart_panel,
                on_open_change=LoginState.set_cart_panel_open,
            ),
            rx.fragment(),
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.dialog.title(
                                "Cadastrar cliente",
                                color="#1f2c39",
                                font_size="1.35rem",
                                font_weight="700",
                            ),
                            rx.dialog.description(
                                f"Clientes cadastrados recebem {CUSTOMER_DISCOUNT_RATE}% de desconto no carrinho.",
                                color="#64748b",
                                font_size="0.9rem",
                            ),
                            align_items="flex-start",
                            spacing="1",
                        ),
                        rx.dialog.close(
                            rx.button(
                                rx.icon("x", size=18),
                                variant="ghost",
                                color="#64748b",
                                aria_label="Fechar cadastro de cliente",
                            )
                        ),
                        width="100%",
                        justify="between",
                        align_items="flex-start",
                    ),
                    rx.cond(
                        LoginState.customer_form_error != "",
                        rx.text(
                            LoginState.customer_form_error,
                            color="#b91c1c",
                            background="#fef2f2",
                            padding="0.75rem 0.9rem",
                            border="1px solid #fecaca",
                            border_radius="10px",
                            font_size="0.88rem",
                            role="alert",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.vstack(
                        rx.text("Nome completo", color="#34485b", font_weight="600"),
                        rx.input(
                            placeholder="Nome do cliente",
                            value=LoginState.customer_name,
                            on_change=LoginState.set_customer_name,
                            width="100%",
                        ),
                        width="100%",
                        align_items="stretch",
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("CPF", color="#34485b", font_weight="600"),
                        rx.input(
                            placeholder="000.000.000-00",
                            value=LoginState.customer_cpf,
                            on_change=LoginState.set_customer_cpf,
                            width="100%",
                        ),
                        width="100%",
                        align_items="stretch",
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text("Telefone", color="#34485b", font_weight="600"),
                        rx.input(
                            placeholder="(00) 00000-0000",
                            value=LoginState.customer_phone,
                            on_change=LoginState.set_customer_phone,
                            type="tel",
                            width="100%",
                        ),
                        width="100%",
                        align_items="stretch",
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                variant="outline",
                                color="#475569",
                                border_color="#cbd5e1",
                                height="44px",
                                padding="0 1.2rem",
                            )
                        ),
                        rx.button(
                            rx.cond(
                                LoginState.is_saving_customer,
                                "Cadastrando...",
                                "Cadastrar e aplicar desconto",
                            ),
                            on_click=LoginState.save_customer,
                            loading=LoginState.is_saving_customer,
                            background="#16a34a",
                            color="white",
                            height="44px",
                            padding="0 1.3rem",
                            border_radius="10px",
                        ),
                        width="100%",
                        justify="end",
                        spacing="3",
                    ),
                    width="100%",
                    spacing="4",
                    align_items="stretch",
                ),
                width="min(92vw, 520px)",
                max_height="90vh",
                overflow_y="auto",
                padding="1.6rem",
                background="white",
                border="1px solid #e2e8f0",
                border_radius="18px",
                box_shadow="0 24px 80px rgba(15,23,42,0.24)",
            ),
            open=LoginState.show_customer_form,
            on_open_change=LoginState.set_customer_form_open,
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
                    rx.link(
                        sidebar_item("Categorias", "tag"),
                        href="/categorias",
                        width="100%",
                        text_decoration="none",
                    ),
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
    categories_page,
    route="/categorias",
    title="Categorias · DROGA-NONIMO",
    on_load=[
        LoginState.require_login,
        LoginState.load_categories,
        LoginState.clear_category_search,
    ],
)
app.add_page(
    sales_page,
    route="/vendas",
    title="Vendas · DROGA-NONIMO",
    on_load=LoginState.load_sales,
)

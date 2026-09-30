import reflex as rx
import httpx
import sys
from pathlib import Path

# Adiciona a pasta raiz do frontend ao caminho do Python
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Importa a função da página de login do arquivo login.py
from frontend.login import login_page

# URL base da API do Xano
XANO_API_URL = "https://x8ki-letl-twmt.n7.xano.io/api:VzEWcgd6"


class State(rx.State):
    """Estado da aplicação para gerenciar dados e interações."""
    produtos: list[dict] = []
    carrinho: list[dict] = []
    cliente_id: str = ""
    mensagem_venda: str = ""

    def set_cliente_id(self, value: str):
        self.cliente_id = value

    def carregar_produtos(self):
        try:
            response = httpx.get(f"{XANO_API_URL}/produtos")
            if response.status_code == 200:
                self.produtos = response.json()
            else:
                self.produtos = []
        except Exception:
            self.produtos = [
                {"id": 1, "nome": "Dipirona 500mg", "preco": 10.00, "estoque": 50},
                {"id": 2, "nome": "Paracetamol 750mg", "preco": 15.00, "estoque": 30},
            ]

    def adicionar_ao_carrinho(self, produto: dict):
        self.carrinho.append(produto)

    def finalizar_venda(self):
        if not self.carrinho:
            self.mensagem_venda = "O carrinho está vazio!"
            return
        
        self.mensagem_venda = f"Venda realizada com sucesso para o cliente ID: {self.cliente_id or 'Balcão'}!"
        self.carrinho.clear()


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.icon(),
        rx.vstack(
            rx.heading("💊 Farmacia_Anonima - Painel de Vendas", size="8"),
            rx.text("Sistema acadêmico integrado com Xano e Reflex", color="gray"),
            
            rx.divider(),
            
            # Seção de Produtos
            rx.heading("Produtos Disponíveis", size="5"),
            rx.button("Carregar Produtos", on_click=State.carregar_produtos, color_scheme="blue"),
            
            rx.foreach(
                State.produtos,
                lambda p: rx.hstack(
                    rx.text(p["nome"], font_weight="bold"),
                    rx.text(f"R$ {p['preco']:.2f}"),
                    rx.button("Adicionar", on_click=lambda: State.adicionar_ao_carrinho(p), size="1"),
                    width="100%",
                    justify="between",
                    padding="2",
                    border_bottom="1px solid #eaeaea",
                ),
            ),
            
            rx.divider(),
            
            # Seção do Carrinho e Finalização
            rx.heading("Carrinho de Compras", size="5"),
            rx.foreach(
                State.carrinho,
                lambda item: rx.text(f"- {item['nome']} (R$ {item['preco']:.2f})"),
            ),
            
            rx.input(
                placeholder="ID do Cliente (Opcional para desconto)",
                value=State.cliente_id,
                on_change=State.set_cliente_id,
                width="300px",
            ),
            
            rx.button("Finalizar Venda", on_click=State.finalizar_venda, color_scheme="green"),
            rx.text(State.mensagem_venda, color="green", font_weight="bold"),
            
            spacing="5",
            align="center",
            padding_top="50px",
        ),
    )


# Inicialização da aplicação com as duas páginas registradas:
app = rx.App()

# 1. Tela de Login como Página Inicial
app.add_page(login_page, route="/") 

# 2. Tela de Vendas (Dashboard) na rota /dashboard
app.add_page(index, route="/dashboard")
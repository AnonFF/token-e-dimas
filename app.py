import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs

# Credenciais via Streamlit Secrets
USER_ID = st.secrets["USER_ID"]
API_KEY = st.secrets["API_KEY"]
BASE_URL = "https://freefireshop.com.br/api/v1"

def auth():
    return {"userId": USER_ID, "key": API_KEY}

def extrair_token(link):
    if "eat=" in link:
        return link.split("eat=")[1].split("&")[0]
    if "#" in link:
        params = parse_qs(link.split("#")[1])
        if "access_token" in params:
            return params["access_token"][0]
    parsed = urlparse(link)
    params = parse_qs(parsed.query)
    if "access_token" in params:
        return params["access_token"][0]
    return None

def post(endpoint, extra={}):
    try:
        r = requests.post(f"{BASE_URL}{endpoint}", json={**auth(), **extra})
        return r.json()
    except Exception as e:
        return {"status": "ERRO", "mensagem": str(e)}

# ───────────────────────────────────────────
st.set_page_config(page_title="🎮 FF Revendedor", layout="centered")
st.title("🎮 Free Fire - Painel do Revendedor")

menu = st.sidebar.selectbox("📋 Menu", [
    "🏠 Minha Conta",
    "💰 Meu Saldo",
    "📦 Estoque de Diamantes",
    "🔍 Verificar Jogador",
    "💎 Enviar Diamantes",
    "🎁 Enviar Token (Caixa)",
    "🏆 Enviar Passe Booyah",
    "🔗 Extrator de Token",
])

# ── MINHA CONTA ──────────────────────────
if menu == "🏠 Minha Conta":
    st.header("🏠 Informações da Conta")
    if st.button("Carregar"):
        res = post("/reseller/info")
        if res.get("status") == "OK":
            d = res["data"]
            col1, col2, col3 = st.columns(3)
            col1.metric("Apelido", d.get("apelido", "-"))
            col2.metric("Saldo", f"R$ {d.get('saldo', 0):.2f}")
            col3.metric("Total Gasto", f"R$ {d.get('gasto', 0):.2f}")
            if "historico" in d and d["historico"]:
                st.subheader("📜 Histórico recente")
                st.dataframe(d["historico"])
        else:
            st.error(res)

# ── SALDO ─────────────────────────────────
elif menu == "💰 Meu Saldo":
    st.header("💰 Consultar Saldo")
    if st.button("Ver Saldo"):
        res = post("/reseller/balance")
        if res.get("status") == "OK":
            saldo = res["data"]["saldo"]
            st.success(f"💰 Saldo atual: **R$ {saldo:.2f}**")
        else:
            st.error(res)

# ── ESTOQUE ───────────────────────────────
elif menu == "📦 Estoque de Diamantes":
    st.header("📦 Estoque Disponível")
    if st.button("Verificar Estoque"):
        res = post("/diamonds/stock")
        if res.get("status") == "OK":
            stock = res["data"]["stock"]
            st.table({f"💎 {k} Diamantes": [v] for k, v in stock.items()})
        else:
            st.error(res)

# ── VERIFICAR JOGADOR ─────────────────────
elif menu == "🔍 Verificar Jogador":
    st.header("🔍 Verificar Token do Jogador")
    token = st.text_input("Access Token do jogador:")
    qtd = st.selectbox("Pacote (opcional):", ["", "200", "620", "1040", "2120", "4360", "5300", "11200", "22400"])
    if st.button("Verificar") and token:
        extra = {"accessToken": token}
        if qtd:
            extra["diamondAmount"] = qtd
        res = post("/diamonds/verify", extra)
        if res.get("status") == "OK":
            p = res["data"]["player"]
            st.success(f"✅ Jogador: **{p['name']}** | Nível: {p['level']} | Região: {p['region']}")
            st.info(res["data"].get("message", ""))
        else:
            st.error(res)

# ── ENVIAR DIAMANTES ──────────────────────
elif menu == "💎 Enviar Diamantes":
    st.header("💎 Enviar Diamantes")
    token = st.text_input("Access Token do jogador:")
    qtd = st.selectbox("Pacote:", ["200", "620", "1040", "2120", "4360", "5300", "11200", "22400"])
    if st.button("Enviar Diamantes") and token:
        res = post("/diamonds/send", {"accessToken": token, "diamondAmount": qtd})
        if res.get("status") == "OK":
            t = res["transacao"]
            st.success(res.get("mensagem", "Enviado!"))
            st.json(t)
        else:
            st.error(res)

# ── ENVIAR TOKEN/CAIXA ────────────────────
elif menu == "🎁 Enviar Token (Caixa)":
    st.header("🎁 Enviar Caixa Universal (Token)")
    uid = st.text_input("UID do jogador:")
    qtd = st.number_input("Quantidade:", min_value=1, max_value=200, value=1)
    msg = st.text_input("Mensagem (opcional):")
    if st.button("Enviar Token") and uid:
        extra = {"playerID": uid, "quantity": qtd}
        if msg:
            extra["mensagem"] = msg
        res = post("/tokens/send", extra)
        if res.get("status") == "OK":
            st.success(res.get("mensagem", "Enviado!"))
            st.json(res["transacao"])
        else:
            st.error(res)

# ── PASSE BOOYAH ──────────────────────────
elif menu == "🏆 Enviar Passe Booyah":
    st.header("🏆 Enviar Passe Booyah")
    uid = st.text_input("UID do jogador:")
    if st.button("Enviar Passe") and uid:
        res = post("/pass/send", {"uid": uid})
        if res.get("status") == "OK":
            st.success(res.get("mensagem", "Enviado!"))
            st.json(res["transacao"])
        else:
            st.error(res)

# ── EXTRATOR DE TOKEN ─────────────────────
elif menu == "🔗 Extrator de Token":
    st.header("🔗 Extrair Token do Link")
    link = st.text_area("Cole o link completo aqui:", height=100)
    if st.button("Extrair Token") and link:
        token = extrair_token(link)
        if token:
            st.success("✅ Token extraído!")
            st.code(token, language=None)
            st.info("👆 Clique no ícone de copiar acima.")
        else:
            st.error("❌ Token não encontrado. Verifique se o link contém 'access_token=' ou 'eat='")

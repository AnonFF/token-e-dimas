import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs

BASE_URL = "https://freefireshop.com.br/api/v1"

USER_ID = st.secrets["USER_ID"]
API_KEY = st.secrets["API_KEY"]

def post(endpoint, extra={}):
    try:
        r = requests.post(f"{BASE_URL}{endpoint}", json={"userId": USER_ID, "key": API_KEY, **extra})
        return r.json()
    except Exception as e:
        return {"status": "ERRO", "mensagem": str(e)}

def extrair_token(link):
    try:
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
    except:
        pass
    return None

st.set_page_config(page_title="FF Revendedor", layout="centered")
st.title("🎮 Free Fire - Painel Revendedor")

menu = st.sidebar.selectbox("Menu", [
    "🏠 Minha Conta",
    "💰 Meu Saldo",
    "📦 Estoque de Diamantes",
    "🔍 Verificar Jogador",
    "💎 Enviar Diamantes",
    "🎁 Enviar Token (Caixa)",
    "🏆 Enviar Passe Booyah",
    "🔗 Extrator de Token",
])

if menu == "🏠 Minha Conta":
    st.header("🏠 Minha Conta")
    if st.button("Carregar"):
        res = post("/reseller/info")
        st.json(res)

elif menu == "💰 Meu Saldo":
    st.header("💰 Meu Saldo")
    if st.button("Ver Saldo"):
        res = post("/reseller/balance")
        if res.get("status") == "OK":
            st.success(f"💰 Saldo: R$ {res['data']['saldo']:.2f}")
        else:
            st.error(str(res))

elif menu == "📦 Estoque de Diamantes":
    st.header("📦 Estoque")
    if st.button("Verificar Estoque"):
        res = post("/diamonds/stock")
        if res.get("status") == "OK":
            for k, v in res["data"]["stock"].items():
                st.write(f"💎 {k} diamantes — {v} disponíveis")
        else:
            st.error(str(res))

elif menu == "🔍 Verificar Jogador":
    st.header("🔍 Verificar Jogador")
    token = st.text_input("Access Token do jogador:")
    qtd = st.selectbox("Pacote (opcional):", ["", "200", "620", "1040", "2120", "4360", "5300", "11200", "22400"])
    if st.button("Verificar") and token:
        extra = {"accessToken": token}
        if qtd:
            extra["diamondAmount"] = qtd
        res = post("/diamonds/verify", extra)
        if res.get("status") == "OK":
            p = res["data"]["player"]
            st.success(f"✅ {p['name']} | Nível {p['level']} | Região {p['region']}")
        else:
            st.error(str(res))

elif menu == "💎 Enviar Diamantes":
    st.header("💎 Enviar Diamantes")
    token = st.text_input("Access Token do jogador:")
    qtd = st.selectbox("Pacote:", ["200", "620", "1040", "2120", "4360", "5300", "11200", "22400"])
    if st.button("Enviar") and token:
        res = post("/diamonds/send", {"accessToken": token, "diamondAmount": qtd})
        if res.get("status") == "OK":
            st.success(res.get("mensagem", "Enviado!"))
            st.json(res.get("transacao", {}))
        else:
            st.error(str(res))

elif menu == "🎁 Enviar Token (Caixa)":
    st.header("🎁 Enviar Caixa Universal")
    uid = st.text_input("UID do jogador:")
    qtd = st.number_input("Quantidade:", min_value=1, max_value=200, value=1)
    msg = st.text_input("Mensagem (opcional):")
    if st.button("Enviar") and uid:
        extra = {"playerID": uid, "quantity": int(qtd)}
        if msg:
            extra["mensagem"] = msg
        res = post("/tokens/send", extra)
        if res.get("status") == "OK":
            st.success(res.get("mensagem", "Enviado!"))
            st.json(res.get("transacao", {}))
        else:
            st.error(str(res))

elif menu == "🏆 Enviar Passe Booyah":
    st.header("🏆 Enviar Passe Booyah")
    uid = st.text_input("UID do jogador:")
    if st.button("Enviar") and uid:
        res = post("/pass/send", {"uid": uid})
        if res.get("status") == "OK":
            st.success(res.get("mensagem", "Enviado!"))
            st.json(res.get("transacao", {}))
        else:
            st.error(str(res))

elif menu == "🔗 Extrator de Token":
    st.header("🔗 Extrair Token do Link")
    link = st.text_area("Cole o link aqui:", height=100)
    if st.button("Extrair") and link:
        token = extrair_token(link)
        if token:
            st.success("✅ Token encontrado!")
            st.code(token, language=None)
        else:
            st.error("❌ Token não encontrado no link.")

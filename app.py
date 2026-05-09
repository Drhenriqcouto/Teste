# app.py

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Calculadora de Arbitragem 1X2",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Calculadora de Arbitragem 1X2")
st.write("Calcule apostas para Time A, Empate e Time B com base nas odds informadas.")

# -----------------------------
# Barra lateral
# -----------------------------
st.sidebar.header("Configurações")

odd_a = st.sidebar.number_input("Odd Time A", min_value=1.01, value=2.37, step=0.01)
odd_empate = st.sidebar.number_input("Odd Empate", min_value=1.01, value=4.20, step=0.01)
odd_b = st.sidebar.number_input("Odd Time B", min_value=1.01, value=3.30, step=0.01)

modo = st.sidebar.radio(
    "Modo de cálculo",
    ["Lucro desejado", "Banca fixa"]
)

if modo == "Lucro desejado":
    lucro_desejado = st.sidebar.number_input(
        "Lucro líquido desejado",
        min_value=1.0,
        value=10.0,
        step=1.0
    )
    valor_total = None
else:
    valor_total = st.sidebar.number_input(
        "Valor total da banca",
        min_value=1.0,
        value=300.0,
        step=10.0
    )
    lucro_desejado = None

# -----------------------------
# Cálculos
# -----------------------------
soma_inversos = (1 / odd_a) + (1 / odd_empate) + (1 / odd_b)
existe_arbitragem = soma_inversos < 1

st.subheader("📊 Análise das Odds")

col1, col2, col3 = st.columns(3)

col1.metric("Soma dos inversos", f"{soma_inversos:.4f}")
col2.metric("Margem", f"{(1 - soma_inversos) * 100:.2f}%")

if existe_arbitragem:
    col3.success("✅ Existe arbitragem")
else:
    col3.error("❌ Não existe arbitragem")

# -----------------------------
# Distribuição das apostas
# -----------------------------
if existe_arbitragem:

    if modo == "Lucro desejado":
        retorno_garantido = lucro_desejado / (1 - soma_inversos)

        aposta_a = retorno_garantido / odd_a
        aposta_empate = retorno_garantido / odd_empate
        aposta_b = retorno_garantido / odd_b

        total_apostado = aposta_a + aposta_empate + aposta_b

    else:
        total_apostado = valor_total

        aposta_a = valor_total * ((1 / odd_a) / soma_inversos)
        aposta_empate = valor_total * ((1 / odd_empate) / soma_inversos)
        aposta_b = valor_total * ((1 / odd_b) / soma_inversos)

        retorno_garantido = aposta_a * odd_a

    retorno_a = aposta_a * odd_a
    retorno_empate = aposta_empate * odd_empate
    retorno_b = aposta_b * odd_b

    lucro_a = retorno_a - total_apostado
    lucro_empate = retorno_empate - total_apostado
    lucro_b = retorno_b - total_apostado

    df = pd.DataFrame({
        "Resultado": ["Time A", "Empate", "Time B"],
        "Odd": [odd_a, odd_empate, odd_b],
        "Valor apostado": [aposta_a, aposta_empate, aposta_b],
        "Retorno bruto": [retorno_a, retorno_empate, retorno_b],
        "Lucro líquido": [lucro_a, lucro_empate, lucro_b]
    })

    st.subheader("💰 Distribuição ideal das apostas")

    st.dataframe(
        df.style.format({
            "Odd": "{:.2f}",
            "Valor apostado": "R$ {:.2f}",
            "Retorno bruto": "R$ {:.2f}",
            "Lucro líquido": "R$ {:.2f}"
        }),
        use_container_width=True
    )

    st.subheader("Resumo")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total apostado", f"R$ {total_apostado:.2f}")
    c2.metric("Retorno garantido", f"R$ {retorno_garantido:.2f}")
    c3.metric("Lucro mínimo", f"R$ {min(lucro_a, lucro_empate, lucro_b):.2f}")

    st.success("A distribuição acima cobre os três resultados possíveis.")

else:
    st.warning("Com essas odds, não é possível garantir lucro cobrindo os três resultados.")

    st.subheader("Simulação com banca fixa")

    banca_simulada = st.number_input(
        "Digite uma banca para simular mesmo sem arbitragem",
        min_value=1.0,
        value=300.0,
        step=10.0
    )

    aposta_a = banca_simulada * ((1 / odd_a) / soma_inversos)
    aposta_empate = banca_simulada * ((1 / odd_empate) / soma_inversos)
    aposta_b = banca_simulada * ((1 / odd_b) / soma_inversos)

    retorno_a = aposta_a * odd_a
    retorno_empate = aposta_empate * odd_empate
    retorno_b = aposta_b * odd_b

    lucro_a = retorno_a - banca_simulada
    lucro_empate = retorno_empate - banca_simulada
    lucro_b = retorno_b - banca_simulada

    df_prejuizo = pd.DataFrame({
        "Resultado": ["Time A", "Empate", "Time B"],
        "Odd": [odd_a, odd_empate, odd_b],
        "Valor apostado": [aposta_a, aposta_empate, aposta_b],
        "Retorno bruto": [retorno_a, retorno_empate, retorno_b],
        "Lucro/Prejuízo": [lucro_a, lucro_empate, lucro_b]
    })

    st.dataframe(
        df_prejuizo.style.format({
            "Odd": "{:.2f}",
            "Valor apostado": "R$ {:.2f}",
            "Retorno bruto": "R$ {:.2f}",
            "Lucro/Prejuízo": "R$ {:.2f}"
        }),
        use_container_width=True
    )

    st.error(f"Prejuízo estimado: R$ {abs(min(lucro_a, lucro_empate, lucro_b)):.2f}")

# -----------------------------
# Rodapé
# -----------------------------
st.divider()
st.caption("Use apenas como ferramenta matemática. Odds podem mudar rapidamente antes da confirmação da aposta.")
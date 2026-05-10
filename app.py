import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO


from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


st.set_page_config(
    page_title="Calculadora de Arbitragem 1X2",
    page_icon="⚽",
    layout="wide"
)


# --------------------------------------------------
# Funções auxiliares
# --------------------------------------------------
def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")




def numero(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")




def calcular_distribuicao(odd_a, odd_empate, odd_b, modo, lucro_desejado=None, valor_total=None):
    soma_inversos = (1 / odd_a) + (1 / odd_empate) + (1 / odd_b)
    existe_arbitragem = soma_inversos < 1


    if existe_arbitragem:
        if modo == "Lucro desejado":
            retorno_base = lucro_desejado / (1 - soma_inversos)
            aposta_a = retorno_base / odd_a
            aposta_empate = retorno_base / odd_empate
            aposta_b = retorno_base / odd_b
            total_apostado = aposta_a + aposta_empate + aposta_b
        else:
            total_apostado = valor_total
            aposta_a = valor_total * ((1 / odd_a) / soma_inversos)
            aposta_empate = valor_total * ((1 / odd_empate) / soma_inversos)
            aposta_b = valor_total * ((1 / odd_b) / soma_inversos)
    else:
        total_apostado = valor_total if valor_total is not None else 300.0
        aposta_a = total_apostado * ((1 / odd_a) / soma_inversos)
        aposta_empate = total_apostado * ((1 / odd_empate) / soma_inversos)
        aposta_b = total_apostado * ((1 / odd_b) / soma_inversos)


    retorno_a = aposta_a * odd_a
    retorno_empate = aposta_empate * odd_empate
    retorno_b = aposta_b * odd_b


    lucro_a = retorno_a - total_apostado
    lucro_empate = retorno_empate - total_apostado
    lucro_b = retorno_b - total_apostado


    retorno_garantido = min(retorno_a, retorno_empate, retorno_b)
    lucro_minimo = min(lucro_a, lucro_empate, lucro_b)
    margem = (1 - soma_inversos) * 100
    roi = (lucro_minimo / total_apostado) * 100 if total_apostado > 0 else 0


    return {
        "soma_inversos": soma_inversos,
        "existe_arbitragem": existe_arbitragem,
        "margem": margem,
        "apostas": [aposta_a, aposta_empate, aposta_b],
        "retornos": [retorno_a, retorno_empate, retorno_b],
        "lucros": [lucro_a, lucro_empate, lucro_b],
        "total_apostado": total_apostado,
        "retorno_garantido": retorno_garantido,
        "lucro_minimo": lucro_minimo,
        "roi": roi,
    }




def gerar_pdf(apostas_registradas):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )


    styles = getSampleStyleSheet()
    elementos = []


    elementos.append(Paragraph("Relatório de Apostas Registradas", styles["Title"]))
    elementos.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["N
    elementos.append(Spacer(1, 0.4 * cm))


    if not apostas_registradas:
        elementos.append(Paragraph("Nenhuma aposta registrada.", styles["Normal"]))
    else:
        for aposta in apostas_registradas:
            elementos.append(Paragraph(f"Aposta {aposta['id']} - {aposta['jogo']}", styles["Heading
            elementos.append(Paragraph(f"Cartões: {aposta['mercado_cartao']} | Odd: {numero(aposta[
            elementos.append(Paragraph(f"Escanteios: {aposta['mercado_escanteio']} | Odd: {numero(a
            elementos.append(Paragraph(
                f"Arbitragem: {'Sim' if aposta['existe_arbitragem'] else 'Não'} | "
                f"Soma dos inversos: {numero(aposta['soma_inversos'], 4)} | "
                f"Margem: {numero(aposta['margem'])}% | ROI: {numero(aposta['roi'])}%",
                styles["Normal"]
            ))
            elementos.append(Spacer(1, 0.2 * cm))


            dados = [["Resultado", "Odd base", "Odd final", "Valor apostado", "Retorno", "Lucro"]]
            for linha in aposta["linhas"]:
                dados.append([
                    linha["Resultado"],
                    numero(linha["Odd base"]),
                    numero(linha["Odd final"]),
                    moeda(linha["Valor apostado"]),
                    moeda(linha["Retorno bruto"]),
                    moeda(linha["Lucro/Prejuízo"]),
                ])


            tabela = Table(dados, repeatRows=1)
            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elementos.append(tabela)
            elementos.append(Spacer(1, 0.25 * cm))
            elementos.append(Paragraph(
                f"Total apostado: {moeda(aposta['total_apostado'])} | "
                f"Retorno garantido: {moeda(aposta['retorno_garantido'])} | "
                f"Lucro mínimo: {moeda(aposta['lucro_minimo'])}",
                styles["Normal"]
            ))
            elementos.append(Spacer(1, 0.55 * cm))


    doc.build(elementos)
    buffer.seek(0)
    return buffer




# --------------------------------------------------
# Estado temporário do app
# --------------------------------------------------
if "apostas_registradas" not in st.session_state:
    st.session_state.apostas_registradas = []


# --------------------------------------------------
# Título
# --------------------------------------------------
st.title("⚽ Calculadora de Arbitragem 1X2")
st.write(
    "Monte uma aposta combinando resultado, cartões e escanteios. "
    "O app calcula as odds finais e aplica a lógica original de arbitragem."
)


# --------------------------------------------------
# Barra lateral
# --------------------------------------------------
st.sidebar.header("Configurações")


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
    banca_simulacao = st.sidebar.number_input(
        "Banca para simular quando não houver arbitragem",
        min_value=1.0,
        value=300.0,
        step=10.0
    )
else:
    valor_total = st.sidebar.number_input(
        "Valor total da banca",
        min_value=1.0,
        value=300.0,
        step=10.0
    )
    lucro_desejado = None
    banca_simulacao = valor_total


# --------------------------------------------------
# Dados da aposta
# --------------------------------------------------
st.subheader("🧾 Dados do jogo")


col_time_a, col_time_b = st.columns(2)
with col_time_a:
    time_a = st.text_input("Time A", value="Flamengo")
with col_time_b:
    time_b = st.text_input("Time B", value="Palmeiras")


st.subheader("🎯 Odds principais 1X2")


col1, col2, col3 = st.columns(3)
with col1:
    odd_a_base = st.number_input(f"Odd {time_a}", min_value=1.01, value=2.10, step=0.01)
with col2:
    odd_empate_base = st.number_input("Odd Empate", min_value=1.01, value=4.00, step=0.01)
with col3:
    odd_b_base = st.number_input(f"Odd {time_b}", min_value=1.01, value=3.40, step=0.01)


st.subheader("🟨 Mercado de cartões")


col_cartao_1, col_cartao_2 = st.columns(2)
with col_cartao_1:
    cartao_opcao = st.radio(
        "Ambos os times recebem cartão?",
        ["Sim", "Não"],
        horizontal=True
    )
with col_cartao_2:
    odd_cartao = st.number_input("Odd cartões", min_value=1.01, value=1.30, step=0.01)


mercado_cartao = f'Ambos recebem cartão: {cartao_opcao}'


st.subheader("🚩 Mercado de escanteios")


col_esc_1, col_esc_2, col_esc_3 = st.columns(3)
with col_esc_1:
    tipo_escanteio = st.selectbox(
        "Tipo de mercado",
        ["Mais que", "Menos que", "Exatamente"]
    )
with col_esc_2:
    linha_escanteio = st.number_input("Linha de escanteios", min_value=0.5, value=10.0, step=0.5)
with col_esc_3:
    odd_escanteio = st.number_input("Odd escanteios", min_value=1.01, value=1.10, step=0.01)


mercado_escanteio = f"{tipo_escanteio} {numero(linha_escanteio, 1)} escanteios"


# --------------------------------------------------
# Odds finais e cálculo
# --------------------------------------------------
odd_a = odd_a_base * odd_cartao * odd_escanteio
odd_empate = odd_empate_base * odd_cartao * odd_escanteio
odd_b = odd_b_base * odd_cartao * odd_escanteio


valor_total_calculo = valor_total if modo == "Banca fixa" else banca_simulacao


resultado = calcular_distribuicao(
    odd_a=odd_a,
    odd_empate=odd_empate,
    odd_b=odd_b,
    modo=modo,
    lucro_desejado=lucro_desejado,
    valor_total=valor_total_calculo,
)


# Ajuste para lucro desejado: quando não houver arbitragem, simula com banca informada
if modo == "Lucro desejado" and not resultado["existe_arbitragem"]:
    resultado = calcular_distribuicao(
        odd_a=odd_a,
        odd_empate=odd_empate,
        odd_b=odd_b,
        modo="Banca fixa",
        valor_total=banca_simulacao,
    )


st.subheader("📊 Análise das odds finais")


c1, c2, c3, c4 = st.columns(4)
c1.metric("Soma dos inversos", f"{resultado['soma_inversos']:.4f}")
c2.metric("Margem", f"{resultado['margem']:.2f}%")
c3.metric("ROI mínimo", f"{resultado['roi']:.2f}%")


if resultado["existe_arbitragem"]:
    c4.success("✅ Existe arbitragem")
else:
    c4.error("❌ Não existe arbitragem")


linhas = [
    {
        "Resultado": time_a,
        "Odd base": odd_a_base,
        "Cartões": mercado_cartao,
        "Odd cartões": odd_cartao,
        "Escanteios": mercado_escanteio,
        "Odd escanteios": odd_escanteio,
        "Odd final": odd_a,
        "Valor apostado": resultado["apostas"][0],
        "Retorno bruto": resultado["retornos"][0],
        "Lucro/Prejuízo": resultado["lucros"][0],
    },
    {
        "Resultado": "Empate",
        "Odd base": odd_empate_base,
        "Cartões": mercado_cartao,
        "Odd cartões": odd_cartao,
        "Escanteios": mercado_escanteio,
        "Odd escanteios": odd_escanteio,
        "Odd final": odd_empate,
        "Valor apostado": resultado["apostas"][1],
        "Retorno bruto": resultado["retornos"][1],
        "Lucro/Prejuízo": resultado["lucros"][1],
    },
    {
        "Resultado": time_b,
        "Odd base": odd_b_base,
        "Cartões": mercado_cartao,
        "Odd cartões": odd_cartao,
        "Escanteios": mercado_escanteio,
        "Odd escanteios": odd_escanteio,
        "Odd final": odd_b,
        "Valor apostado": resultado["apostas"][2],
        "Retorno bruto": resultado["retornos"][2],
        "Lucro/Prejuízo": resultado["lucros"][2],
    },
]


df = pd.DataFrame(linhas)


st.subheader("💰 Distribuição recomendada")
st.dataframe(
    df.style.format({
        "Odd base": "{:.2f}",
        "Odd cartões": "{:.2f}",
        "Odd escanteios": "{:.2f}",
        "Odd final": "{:.2f}",
        "Valor apostado": "R$ {:.2f}",
        "Retorno bruto": "R$ {:.2f}",
        "Lucro/Prejuízo": "R$ {:.2f}",
    }),
    use_container_width=True
)


st.subheader("Resumo")
r1, r2, r3 = st.columns(3)
r1.metric("Total apostado", moeda(resultado["total_apostado"]))
r2.metric("Retorno garantido", moeda(resultado["retorno_garantido"]))
r3.metric("Lucro mínimo", moeda(resultado["lucro_minimo"]))


if resultado["existe_arbitragem"]:
    st.success("A distribuição acima cobre os três resultados possíveis usando as odds finais combi
else:
    st.warning("Com essas odds finais, não é possível garantir lucro cobrindo os três resultados.")


# --------------------------------------------------
# Registro temporário
# --------------------------------------------------
st.divider()
st.subheader("📌 Registro temporário de apostas")


col_add, col_clear = st.columns([1, 1])


with col_add:
    if st.button("Adicionar aposta", type="primary", use_container_width=True):
        novo_id = len(st.session_state.apostas_registradas) + 1
        st.session_state.apostas_registradas.append({
            "id": novo_id,
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "jogo": f"{time_a} x {time_b}",
            "time_a": time_a,
            "time_b": time_b,
            "mercado_cartao": mercado_cartao,
            "odd_cartao": odd_cartao,
            "mercado_escanteio": mercado_escanteio,
            "odd_escanteio": odd_escanteio,
            "soma_inversos": resultado["soma_inversos"],
            "margem": resultado["margem"],
            "roi": resultado["roi"],
            "existe_arbitragem": resultado["existe_arbitragem"],
            "total_apostado": resultado["total_apostado"],
            "retorno_garantido": resultado["retorno_garantido"],
            "lucro_minimo": resultado["lucro_minimo"],
            "linhas": linhas,
        })
        st.success(f"Aposta {novo_id} adicionada ao relatório temporário.")


with col_clear:
    if st.button("Limpar apostas registradas", use_container_width=True):
        st.session_state.apostas_registradas = []
        st.info("Histórico temporário limpo.")


if st.session_state.apostas_registradas:
    resumo_apostas = []
    detalhes_apostas = []


    for aposta in st.session_state.apostas_registradas:
        resumo_apostas.append({
            "Aposta": aposta["id"],
            "Data/Hora": aposta["data_hora"],
            "Jogo": aposta["jogo"],
            "Cartões": aposta["mercado_cartao"],
            "Odd cartões": aposta["odd_cartao"],
            "Escanteios": aposta["mercado_escanteio"],
            "Odd escanteios": aposta["odd_escanteio"],
            "Arbitragem": "Sim" if aposta["existe_arbitragem"] else "Não",
            "Lucro mínimo": aposta["lucro_minimo"],
            "ROI mínimo (%)": aposta["roi"],
        })


        for linha in aposta["linhas"]:
            detalhes_apostas.append({
                "Aposta": aposta["id"],
                "Jogo": aposta["jogo"],
                **linha,
            })


    st.write("### Apostas registradas no uso atual")
    st.dataframe(
        pd.DataFrame(resumo_apostas).style.format({
            "Odd cartões": "{:.2f}",
            "Odd escanteios": "{:.2f}",
            "Lucro mínimo": "R$ {:.2f}",
            "ROI mínimo (%)": "{:.2f}%",
        }),
        use_container_width=True
    )


    with st.expander("Ver detalhes de todas as possibilidades registradas"):
        st.dataframe(
            pd.DataFrame(detalhes_apostas).style.format({
                "Odd base": "{:.2f}",
                "Odd cartões": "{:.2f}",
                "Odd escanteios": "{:.2f}",
                "Odd final": "{:.2f}",
                "Valor apostado": "R$ {:.2f}",
                "Retorno bruto": "R$ {:.2f}",
                "Lucro/Prejuízo": "R$ {:.2f}",
            }),
            use_container_width=True
        )


    pdf = gerar_pdf(st.session_state.apostas_registradas)
    st.download_button(
        label="📄 Exportar relatório em PDF",
        data=pdf,
        file_name=f"relatorio_apostas_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
else:
    st.info("Nenhuma aposta registrada ainda. Configure a aposta acima e clique em 'Adicionar apost


# --------------------------------------------------
# Rodapé
# --------------------------------------------------
st.divider()
st.caption("Use apenas como ferramenta matemática. Odds podem mudar rapidamente antes da confirmaçã


 #*importar as bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta
from io import BytesIO

#*criar as funções de carregamento de dados
	#*Cotações do Itau - ITUB4 2010 a 2024
@st.cache_data #*Decorator dá uma nova funcionalidade à essa função, salvar as informações em cache
def carregar_dados (empresas):
	tickers = " ".join(empresas)
	dados_acao = yf.Tickers(tickers)
	cotacoes_acao = dados_acao.history(period="1d", start="2010-01-01", end="2024-08-15")
	print(cotacoes_acao)
	cotacoes_acao = cotacoes_acao['Close']
	return cotacoes_acao

def gerar_excel(df):
    output = BytesIO()
    df.index = df.index.tz_localize(None)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer)
    return output.getvalue()

def gerar_pdf(df):
    output = BytesIO()
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    pdf = canvas.Canvas(output, pagesize=letter)
    pdf.setTitle("Dados do filtro selecionadas")
    pdf.drawString(100, 750, "Dados filtrados")
    data = df.reset_index().values.tolist()
    y_offset = 700
    for row in data:
        pdf.drawString(100, y_offset, str(row))
        y_offset -= 20
        if y_offset <100:
           pdf.showPage()
           y_offset = 750
    pdf.save()
    return output.getvalue()



acoes = ["AAGR11.SA", "PETR4.SA", "VALE3.SA", "MGLU3.SA", "ABEV3.SA"]
dados = carregar_dados(acoes)

#*criar a interface do streamlit
st.write("""
	# Preço de Ações
	O gráfico representa a evolução do preço das ações do Itaú (ITUB4) ao longo dos anos
""") #*markdown


#*prepara as visualizações - Agora são Filtros
st.sidebar.header("Filtros")


#*Filtro de Ações
lista_acoes = st.sidebar.multiselect("Escolha as Ações para visualizar", dados.columns)
if lista_acoes:
	dados = dados[lista_acoes]
	if len(lista_acoes) == 1:
		acao_unica = lista_acoes[0]
		dados = dados.rename(columns={acao_unica: "Close"})

#*Filtro de Datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_datas = st.sidebar.slider("Selecione as datas", min_value=data_inicial, max_value=data_final, value=(data_inicial, data_final), step=timedelta(days=15))

dados = dados.loc[intervalo_datas[0]:intervalo_datas[1]]

#*Criar o Gráfico
st.bar_chart(dados)

excel_bytes = gerar_excel(dados)
st.sidebar.download_button(
    label  ="Baixar dados em Excel",
    data=excel_bytes,
    file_name="filtro_acoes_felipe.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

pdf_bytes = gerar_pdf(dados)
st.sidebar.download_button(
    label  ="Baixar dados em PDF",
    data=pdf_bytes,
    file_name="dados_em_pdf.pdf",
    mime="application/pdf"
)

st.write("""
	## Felipe Bugalho
""")
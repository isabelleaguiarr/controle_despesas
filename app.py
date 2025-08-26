import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

# --- CONEXÃO COM O BANCO ---
conn = sqlite3.connect("despesas.db")
cursor = conn.cursor()

# Criar tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    valor REAL,
    categoria TEXT,
    data TEXT
)
""")
conn.commit()

# --- FORMULÁRIO PARA ADICIONAR DESPESA ---
st.title("Controle de Despesas")

st.subheader("Adicionar nova despesa")

descricao = st.text_input("Descrição")
categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Outros"])
valor = st.number_input("Valor", min_value=0.0, step=0.01)
data = st.date_input("Data", datetime.today())

if st.button("Adicionar despesa"):
    cursor.execute(
        "INSERT INTO despesas (descricao, valor, categoria, data) VALUES (?, ?, ?, ?)",
        (descricao, valor, categoria, data.strftime("%d/%m/%Y"))
    )
    conn.commit()
    st.success("Despesa adicionada com sucesso!")

# --- LISTAR DESPESAS ---
st.markdown("---")
st.subheader("Minhas despesas")

cursor.execute("SELECT id, descricao, valor, categoria, data FROM despesas")
dados = cursor.fetchall()

if dados:
    df = pd.DataFrame(dados, columns=["ID", "Descrição", "Valor", "Categoria", "Data"])
    st.dataframe(df)
else:
    st.info("Nenhuma despesa cadastrada ainda.")

# --- GRÁFICO ---
st.markdown("---")
st.subheader("Resumo de Gastos por Categoria")

if dados:
    resumo = df.groupby("Categoria")["Valor"].sum().sort_values(ascending=False)
    st.bar_chart(resumo, use_container_width=True)
else:
    st.info("Nenhuma despesa para mostrar no gráfico.")

# --- GERENCIAR DESPESAS ---
st.markdown("---")
st.subheader("Gerenciar despesas")

# Apagar todo histórico
if st.button("🗑️ Apagar todo histórico"):
    cursor.execute("DELETE FROM despesas")
    conn.commit()
    st.success("Histórico apagado com sucesso!")

# Apagar despesa específica
if dados:
    opcoes = [f"{d[0]} - {d[1]} ({d[2]} R$)" for d in dados]
    escolha = st.selectbox("Escolha a despesa para apagar", opcoes)
    if st.button("🗑️ Apagar despesa selecionada"):
        despesa_id = int(escolha.split(" - ")[0])
        cursor.execute("DELETE FROM despesas WHERE id=?", (despesa_id,))
        conn.commit()
        st.success(f"Despesa '{escolha}' apagada com sucesso!")

# --- BAIXAR ARQUIVOS ---
st.markdown("---")
st.subheader("Exportar despesas")

# CSV
if dados:
    df_export = df.drop(columns=["ID"])
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Baixar CSV", data=csv, file_name="despesas.csv", mime="text/csv")

    

import streamlit as st
import pandas as pd
import pickle
from datetime import datetime, timedelta
from components.login import require_login ,show_logout_button
import os
from dotenv import load_dotenv


load_dotenv()
# Caminho para o arquivo de favoritos
FAVORITOS_FILE = "cache/favoritos.pkl"

# Função para carregar os favoritos
def load_favoritos():
    if os.path.exists(FAVORITOS_FILE):
        with open(FAVORITOS_FILE, "rb") as f:
            favoritos_data = pickle.load(f)
            # Verificar se os favoritos são mais recentes que 24 horas
            if favoritos_data["timestamp"] > datetime.now() - timedelta(hours=24):
                return favoritos_data["favoritos"]
    return set()

# Função para salvar os favoritos
def save_favoritos(favoritos):
    with open(FAVORITOS_FILE, "wb") as f:
        pickle.dump({"favoritos": favoritos, "timestamp": datetime.now()}, f)
def home_page():
    # Configuração da página
    st.set_page_config(page_title="Dashboard de Jogos", layout="wide")

    # Título do dashboard
    st.title("📅 Dashboard de Próximos Jogos")

    # Inicializar favoritos no session_state
    if "favoritos" not in st.session_state:
        st.session_state.favoritos = load_favoritos()  # Carregar favoritos salvos ou iniciar vazio

    # Função para carregar dados
    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv("proximos_jogos_tratados.csv")

            df["estrategia"] = "sem entrada"  # Define um valor padrão

            df.loc[
                #(df["DifAbs_HomeDraw"].between(1.8, 2.7)) &
                (df["A_D"].between(1.5, 2.4)) &
                (df["Media_P_OASJ"].between(0.35, 0.45)) &
                (df["Odd_Over05_FT"].between(1.01, 1.10)) &
                (df["Favorito"] == "Casa_Fav")&
                (df["Equilibrio"] == "Desequilibrado"),
                "estrategia"
            ] = "Dutching Casa 70%"

            # Remover espaços extras dos nomes das colunas
            df.columns = df.columns.str.strip()
            df = df[df["estrategia"] != "sem entrada"]            

            # Verificar se a coluna "Date" existe e converter para datetime
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
            return df
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo CSV: {e}")
            return pd.DataFrame()

    df = load_data()

    if not df.empty:
        # Sidebar para filtros
        st.sidebar.header("Filtros")

        if "Date" in df.columns:
            df = df.dropna(subset=["Date"])  # Remover datas inválidas

            # Data mínima e máxima
            min_date = df["Date"].dt.date.min()
            max_date = df["Date"].dt.date.max()

            # Definir data padrão como hoje, se possível
            default_date = datetime.today().date()
            if default_date < min_date or default_date > max_date:
                default_date = min_date

            # Seleção da data
            selected_date = st.sidebar.date_input(
                "Escolha uma data",
                value=default_date,
                min_value=min_date,
                max_value=max_date
            )

            # Filtrar os dados pela data selecionada
            filtered_df = df[df["Date"].dt.date == selected_date]

        else:
            st.sidebar.warning("A coluna 'Date' não foi encontrada no arquivo CSV.")
            filtered_df = df

        # Exibir os dados filtrados
        st.header(f"Jogos para {selected_date.strftime('%d/%m/%Y')}")
        st.write(f"Total de registros encontrados: {len(filtered_df)}")

        # Garantir que as colunas 'Home' e 'Away' existem
        if "Home" not in df.columns or "Away" not in df.columns:
            st.error("As colunas 'Home' e 'Away' não foram encontradas no CSV! Verifique o arquivo.")
        else:
            # Exibir tabela de jogos com opção de favoritar
            with st.expander("📊 Visualizar Jogos", expanded=True):
                for index, row in filtered_df.iterrows():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"🏆 - {row['League']} - {row['Home']} vs {row['Away']} - ⌚ - {row['Time']} - ♟️{row['estrategia']}")
                    with col2:
                        favorito_key = f"{row['Date'].strftime('%d/%m/%Y')} - {row['League']} - {row['Home']} vs {row['Away']} - ⌚ - {row['Time']} - ♟️{row['estrategia']}"
                        if favorito_key in st.session_state.favoritos:
                            if st.button("⭐ Remover", key=f"remover-{index}"):

                                st.session_state.favoritos.remove(favorito_key)
                                save_favoritos(st.session_state.favoritos)  # Salvar favoritos após a remoção
                                st.rerun()
                        else:
                            if st.button("☆ Favoritar", key=f"favoritar-{index}"):

                                st.session_state.favoritos.add(favorito_key)
                                save_favoritos(st.session_state.favoritos)  # Salvar favoritos após adicionar
                                st.rerun()
            st.markdown("---")                    
            # Seção para exibir jogos favoritados                    
            if st.session_state.favoritos:
                st.header("⭐ Jogos Favoritados")
                for favorito in list(st.session_state.favoritos):
                    st.write(f"✅ {favorito}")
                        

            # Exibir o DataFrame com a tabela
            st.markdown("---")
            st.header("Jogos Estratégias")
            if st.button("♟️ Estratégias"):
              st.subheader("Dutching Casa 70%")
              ftr = filtered_df[filtered_df["estrategia"] == "Dutching Casa 70%"]  
              st.dataframe(ftr)


            # Botão para download com ícone
            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False)

            csv = convert_df_to_csv(filtered_df)
            
            # Exibindo o botão com emoji de download
            st.markdown(f'<a href="data:file/csv;base64,{csv}" download="jogos_{selected_date.strftime("%Y-%m-%d")}.csv">📥 Baixar CSV</a>', unsafe_allow_html=True)


    else:
        st.error("Nenhum dado foi carregado. Verifique o caminho do arquivo CSV.")


def main():
    if require_login():
        home_page()
        st.sidebar.success(f"💚 Bem-vindo , {os.getenv('APP_USERNAME')}")
        show_logout_button()

if __name__ == "__main__":
    main()







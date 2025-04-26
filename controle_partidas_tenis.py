
import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit as st

# Funções de carregamento inicial
def carregar_dados():
    if os.path.exists('jogadores.csv'):
        jogadores_df = pd.read_csv('jogadores.csv')
    else:
        jogadores_df = pd.DataFrame({'Nome': [], 'Apelido': [], 'Data de Cadastro': []})

    if os.path.exists('partidas_tenis.csv'):
        partidas_df = pd.read_csv('partidas_tenis.csv')
    else:
        partidas_df = pd.DataFrame({'Data': [], 'Jogador 1': [], 'Jogador 2': [], 'Resultado': [], 'Sets': [], 'Observações': []})

    return jogadores_df, partidas_df

# Funções de salvamento
def salvar_dados(jogadores_df, partidas_df):
    jogadores_df.to_csv('jogadores.csv', index=False)
    partidas_df.to_csv('partidas_tenis.csv', index=False)

# Função principal do aplicativo
def app():
    st.title('🎾 Controle de Partidas de Tênis')

    jogadores, partidas_tenis = carregar_dados()

    menu = st.sidebar.selectbox("Menu", ["Cadastrar Jogador", "Cadastrar Partida", "Listar Jogadores", "Listar Partidas", "Relatório de Desempenho"])

    if menu == "Cadastrar Jogador":
        st.subheader("Adicionar Novo Jogador")
        nome = st.text_input("Nome do Jogador")
        apelido = st.text_input("Apelido (opcional)")
        if st.button("Salvar Jogador"):
            novo_jogador = {'Nome': nome, 'Apelido': apelido, 'Data de Cadastro': pd.Timestamp.now().strftime('%d/%m/%Y')}
            jogadores = pd.concat([jogadores, pd.DataFrame([novo_jogador])], ignore_index=True)
            salvar_dados(jogadores, partidas_tenis)
            st.success("Jogador cadastrado com sucesso!")

    elif menu == "Cadastrar Partida":
        st.subheader("Adicionar Nova Partida")
        data_partida = st.date_input("Data da Partida").strftime('%d/%m/%Y')
        jogador1 = st.selectbox("Jogador 1", jogadores['Nome'].tolist())
        jogador2 = st.selectbox("Jogador 2", jogadores['Nome'].tolist())
        resultado = st.text_input("Resultado (ex: 6-4, 7-5)")
        sets = st.text_input("Placar de Sets (ex: 2x0)")
        observacoes = st.text_area("Observações")
        if st.button("Salvar Partida"):
            nova_partida = {'Data': data_partida, 'Jogador 1': jogador1, 'Jogador 2': jogador2, 'Resultado': resultado, 'Sets': sets, 'Observações': observacoes}
            partidas_tenis = pd.concat([partidas_tenis, pd.DataFrame([nova_partida])], ignore_index=True)
            salvar_dados(jogadores, partidas_tenis)
            st.success("Partida registrada com sucesso!")

    elif menu == "Listar Jogadores":
        st.subheader("Jogadores Cadastrados")
        st.dataframe(jogadores)

    elif menu == "Listar Partidas":
        st.subheader("Partidas Registradas")
        st.dataframe(partidas_tenis)

    elif menu == "Relatório de Desempenho":
        st.subheader("Relatório de Desempenho")
        if partidas_tenis.empty:
            st.warning("Nenhuma partida registrada.")
        else:
            partidas_tenis['Data'] = pd.to_datetime(partidas_tenis['Data'], dayfirst=True)

            filtrar = st.checkbox("Filtrar por Período")
            if filtrar:
                inicio = st.date_input("Data Inicial")
                fim = st.date_input("Data Final")
                partidas_filtradas = partidas_tenis[(partidas_tenis['Data'] >= inicio) & (partidas_tenis['Data'] <= fim)]
            else:
                partidas_filtradas = partidas_tenis.copy()

            if partidas_filtradas.empty:
                st.warning("Nenhuma partida encontrada no período informado.")
            else:
                vitorias = {}
                derrotas = {}
                partidas_jogadas = {}
                sets_vencidos = {}

                for idx, partida in partidas_filtradas.iterrows():
                    jogador1 = partida['Jogador 1']
                    jogador2 = partida['Jogador 2']
                    resultado = partida['Resultado']

                    sets = resultado.split(',')
                    sets_jogador1 = 0
                    sets_jogador2 = 0

                    for s in sets:
                        games1, games2 = map(int, s.split('-'))
                        if games1 > games2:
                            sets_jogador1 += 1
                        else:
                            sets_jogador2 += 1

                    vencedor = jogador1 if sets_jogador1 > sets_jogador2 else jogador2
                    perdedor = jogador2 if vencedor == jogador1 else jogador1

                    vitorias[vencedor] = vitorias.get(vencedor, 0) + 1
                    derrotas[perdedor] = derrotas.get(perdedor, 0) + 1

                    partidas_jogadas[jogador1] = partidas_jogadas.get(jogador1, 0) + 1
                    partidas_jogadas[jogador2] = partidas_jogadas.get(jogador2, 0) + 1

                    sets_vencidos[jogador1] = sets_vencidos.get(jogador1, 0) + sets_jogador1
                    sets_vencidos[jogador2] = sets_vencidos.get(jogador2, 0) + sets_jogador2

                relatorio = []
                for jogador in partidas_jogadas:
                    total = partidas_jogadas[jogador]
                    wins = vitorias.get(jogador, 0)
                    losses = derrotas.get(jogador, 0)
                    sets_win = sets_vencidos.get(jogador, 0)
                    aproveitamento = (wins / total) * 100 if total > 0 else 0
                    relatorio.append([jogador, total, wins, losses, sets_win, f"{aproveitamento:.2f}%"])

                df_relatorio = pd.DataFrame(relatorio, columns=["Jogador", "Partidas", "Vitórias", "Derrotas", "Sets Vencidos", "Aproveitamento"])
                st.dataframe(df_relatorio)

                st.bar_chart(df_relatorio.set_index("Jogador")["Vitórias"])
                st.bar_chart(df_relatorio.set_index("Jogador")["Aproveitamento"].str.rstrip('%').astype(float))

if __name__ == "__main__":
    app()

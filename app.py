import streamlit as st 
from statsbombpy import sb 
from mplsoccer import Pitch 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns 

df_comp = sb.competitions()
df_comp = df_comp[df_comp ['competition_international'] == False]
competition_names = df_comp['competition_name'].unique()
competition_ids = df_comp['competition_id'].unique()
competition_name_selected = st.selectbox("competição:", competition_names)

df_comp_sel = df_comp[df_comp ['competition_name'] == competition_name_selected]
df_comp_sel = df_comp_sel.sort_values('season_name')
season_names = df_comp_sel['season_name']
season_name_selected = st.selectbox("Temporada:", season_names)

competition_season_selected = df_comp_sel[(df_comp_sel['competition_name'] == competition_name_selected) & \
                            (df_comp_sel['season_name']==season_name_selected)]
competition_id_selected = competition_season_selected['competition_id'].item()
season_id_selected = competition_season_selected['season_id'].item()
matches = sb.matches(competition_id=competition_id_selected, season_id=season_id_selected)
home_team_names = matches ['home_team'].unique()
away_team_names = matches ['away_team'].unique()
team_name_selected = st.selectbox('Time:', home_team_names)

matches_selected = matches[(matches['home_team']== team_name_selected) |\
                            (matches ['away_team'] == team_name_selected)]
matches_selected['home_score_cumsum'] = matches_selected['home_score'].cumsum()
matches_selected['away_score_cumsum'] = matches_selected['away_score'].cumsum()

#st.selectbox("Temporada:", ["2020", "2021"])
#print(competitions)
#print(competitions.columns)



#df_comp_sel[['year1', 'year2']] = df_comp_sel['season_name'].str.split("/", expand=True)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Soccer Analytics",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Soccer Analytics Dashboard")

# ============================================================
# 1. COMPETIÇÕES
# ============================================================

competitions = sb.competitions()

competition_names = sorted(
    competitions["competition_name"].dropna().unique()
)

competition_name = st.selectbox(
    "🏆 Competição",
    competition_names
)

competition_selected = competitions[
    competitions["competition_name"] == competition_name
]

# ============================================================
# 2. TEMPORADA
# ============================================================

season_names = sorted(
    competition_selected["season_name"].dropna().unique()
)

season_name = st.selectbox(
    "📅 Temporada",
    season_names
)

competition_row = competition_selected[
    competition_selected["season_name"] == season_name
].iloc[0]

competition_id = competition_row["competition_id"]
season_id = competition_row["season_id"]

# ============================================================
# 3. PARTIDAS
# ============================================================

matches = sb.matches(
    competition_id=competition_id,
    season_id=season_id
)

matches["match_name"] = (
    matches["home_team"]
    + " x "
    + matches["away_team"]
)

match_name = st.selectbox(
    "⚽ Partida",
    matches["match_name"].tolist()
)

match = matches[
    matches["match_name"] == match_name
].iloc[0]

match_id = match["match_id"]

home_team = match["home_team"]
away_team = match["away_team"]

home_score = match.get("home_score", 0)
away_score = match.get("away_score", 0)

# ============================================================
# 4. EVENTOS
# ============================================================

events = sb.events(match_id=match_id)

# ============================================================
# 5. CABEÇALHO DA PARTIDA
# ============================================================

st.divider()

st.header(f"{home_team}  {home_score} x {away_score}  {away_team}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Competição", competition_name)

with col2:
    st.metric("Temporada", season_name)

with col3:
    st.metric("ID da partida", match_id)

# ============================================================
# 6. ESTATÍSTICAS BÁSICAS
# ============================================================

st.subheader("📊 Estatísticas da partida")

passes = events[
    events["type"] == "Pass"
].copy()

shots = events[
    events["type"] == "Shot"
].copy()

duels = events[
    events["type"] == "Duel"
].copy()

goals = 0

if "shot_outcome" in shots.columns:
    goals = (
        shots["shot_outcome"] == "Goal"
    ).sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Passes", len(passes))

with col2:
    st.metric("Chutes", len(shots))

with col3:
    st.metric("Duelos", len(duels))

with col4:
    st.metric("Gols", goals)

# ============================================================
# 7. MAPA DE PASSES
# ============================================================

st.divider()

st.header("🗺️ Mapa de Passes")

team_pass = st.selectbox(
    "Escolha o time para visualizar os passes:",
    [home_team, away_team],
    key="team_pass"
)

passes_team = passes[
    passes["team"] == team_pass
].copy()

# Extrair coordenadas dos passes
pass_data = []

for _, row in passes_team.iterrows():

    try:
        x = row["location"][0]
        y = row["location"][1]

        if "pass_end_location" in row and isinstance(
            row["pass_end_location"], list
        ):
            end_x = row["pass_end_location"][0]
            end_y = row["pass_end_location"][1]

            pass_data.append(
                [x, y, end_x, end_y]
            )

    except:
        pass

df_pass = pd.DataFrame(
    pass_data,
    columns=[
        "x",
        "y",
        "end_x",
        "end_y"
    ]
)

if len(df_pass) > 0:

    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color="#f5f5f5",
        line_color="#333333"
    )

    fig, ax = pitch.draw(
        figsize=(12, 7)
    )

    # Setas dos passes
    pitch.arrows(
        df_pass["x"],
        df_pass["y"],
        df_pass["end_x"],
        df_pass["end_y"],
        ax=ax,
        color="blue",
        width=1.5,
        headwidth=4,
        alpha=0.55
    )

    # Localização inicial dos passes
    pitch.scatter(
        df_pass["x"],
        df_pass["y"],
        ax=ax,
        s=15,
        color="black",
        alpha=0.6
    )

    ax.set_title(
        f"Mapa de Passes — {team_pass}",
        fontsize=18
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    st.caption(
        "As setas representam a direção dos passes. "
        "Os pontos representam o local de origem."
    )

else:

    st.warning(
        "Não foram encontradas coordenadas de passes "
        "para esse time."
    )

# ============================================================
# 8. MAPA DE CHUTES
# ============================================================

st.divider()

st.header("🥅 Mapa de Chutes")

team_shots = st.selectbox(
    "Escolha o time para visualizar os chutes:",
    [home_team, away_team],
    key="team_shots"
)

shots_team = shots[
    shots["team"] == team_shots
].copy()

shot_data = []

for _, row in shots_team.iterrows():

    try:

        x = row["location"][0]
        y = row["location"][1]

        outcome = row.get(
            "shot_outcome",
            "Unknown"
        )

        player = row.get(
            "player",
            "Desconhecido"
        )

        shot_data.append(
            [x, y, outcome, player]
        )

    except:
        pass

df_shots = pd.DataFrame(
    shot_data,
    columns=[
        "x",
        "y",
        "outcome",
        "player"
    ]
)

if len(df_shots) > 0:

    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color="#f5f5f5",
        line_color="#333333"
    )

    fig, ax = pitch.draw(
        figsize=(12, 7)
    )

    # Chutes
    pitch.scatter(
        df_shots["x"],
        df_shots["y"],
        ax=ax,
        s=100,
        color="red",
        edgecolors="black",
        alpha=0.75
    )

    # Mostrar número do chute
    for i, row in df_shots.iterrows():

        pitch.annotate(
            str(i + 1),
            xy=(row["x"], row["y"]),
            ax=ax,
            fontsize=8,
            color="black"
        )

    ax.set_title(
        f"Mapa de Chutes — {team_shots}",
        fontsize=18
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    # Tabela dos chutes
    st.write("**Detalhes dos chutes**")

    st.dataframe(
        df_shots,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "Não foram encontrados chutes "
        "para esse time."
    )

# ============================================================
# 9. HEATMAP DE PASSES
# ============================================================

st.divider()

st.header("🔥 Heatmap de Passes")

if len(df_pass) > 0:

    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color="#eeeeee",
        line_color="#333333"
    )

    fig, ax = pitch.draw(
        figsize=(12, 7)
    )

    bin_statistic = pitch.bin_statistic(
        df_pass["x"],
        df_pass["y"],
        statistic="count",
        bins=(12, 8)
    )

    pitch.heatmap(
        bin_statistic,
        ax=ax,
        cmap="Reds"
    )

    pitch.scatter(
        df_pass["x"],
        df_pass["y"],
        ax=ax,
        s=5,
        color="black",
        alpha=0.4
    )

    ax.set_title(
        f"Zonas de maior concentração de passes — {team_pass}"
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

# ============================================================
# 10. RELAÇÃO PASSES x CHUTES
# ============================================================

st.divider()

st.header("📈 Relação entre Passes e Chutes")

team_stats = []

for team in [home_team, away_team]:

    team_events = events[
        events["team"] == team
    ]

    team_passes = (
        team_events["type"] == "Pass"
    ).sum()

    team_shots = (
        team_events["type"] == "Shot"
    ).sum()

    team_goals = 0

    if "shot_outcome" in team_events.columns:

        team_goals = (
            (
                team_events["type"] == "Shot"
            )
            &
            (
                team_events["shot_outcome"] == "Goal"
            )
        ).sum()

    team_stats.append(
        {
            "Time": team,
            "Passes": team_passes,
            "Chutes": team_shots,
            "Gols": team_goals
        }
    )

df_stats = pd.DataFrame(team_stats)

# Scatter Matplotlib
fig, ax = plt.subplots(
    figsize=(8, 5)
)

ax.scatter(
    df_stats["Passes"],
    df_stats["Gols"],
    s=150
)

for _, row in df_stats.iterrows():

    ax.annotate(
        row["Time"],
        (
            row["Passes"],
            row["Gols"]
        ),
        xytext=(5, 5),
        textcoords="offset points"
    )

ax.set_xlabel("Número de passes")
ax.set_ylabel("Número de gols")
ax.set_title("Relação entre Passes e Gols")

ax.grid(
    alpha=0.3
)

st.pyplot(
    fig,
    use_container_width=True
)

# ============================================================
# 11. SEABORN — PASSES E CHUTES POR TIME
# ============================================================

st.subheader("📊 Comparação entre os times")

df_melt = df_stats.melt(
    id_vars="Time",
    value_vars=[
        "Passes",
        "Chutes",
        "Gols"
    ],
    var_name="Estatística",
    value_name="Quantidade"
)

fig, ax = plt.subplots(
    figsize=(10, 5)
)

sns.barplot(
    data=df_melt,
    x="Estatística",
    y="Quantidade",
    hue="Time",
    ax=ax
)

ax.set_title(
    "Comparação das principais estatísticas"
)

st.pyplot(
    fig,
    use_container_width=True
)

# ============================================================
# 12. VISUALIZAÇÃO MPLSOCCER — PASS FLOW
# ============================================================

st.divider()

st.header("🔄 Pass Flow Map")

if len(df_pass) > 0:

    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color="#f5f5f5",
        line_color="#333333"
    )

    fig, ax = pitch.draw(
        figsize=(12, 7)
    )

    pitch.flow(
        df_pass["x"],
        df_pass["y"],
        df_pass["end_x"],
        df_pass["end_y"],
        bins=(6, 4),
        ax=ax,
        color="darkblue",
        arrow_type="scale",
        arrow_length=5
    )

    ax.set_title(
        f"Pass Flow — {team_pass}",
        fontsize=18
    )

    st.pyplot(
        fig,
        use_container_width=True
    )

    st.caption(
        "A espessura/direção das setas ajuda a identificar "
        "os principais fluxos de circulação da equipe."
    )

# ============================================================
# 13. DATAFRAME DE EVENTOS
# ============================================================

st.divider()

st.header("📋 Eventos da partida")

colunas = [
    "minute",
    "second",
    "team",
    "player",
    "type"
]

colunas_disponiveis = [
    c for c in colunas
    if c in events.columns
]

df_eventos = events[
    colunas_disponiveis
].copy()

st.dataframe(
    df_eventos,
    use_container_width=True,
    hide_index=True
)

#Exercicio 6
# ============================================================
# INTERATIVIDADE
# ============================================================

st.divider()
st.header("🎯 Filtros e interatividade")


# ============================================================
# SESSION STATE
# ============================================================

if "tipo_filtro" not in st.session_state:
    st.session_state.tipo_filtro = "Todos"

if "jogador_filtro" not in st.session_state:
    st.session_state.jogador_filtro = "Todos"


# ============================================================
# CARREGAMENTO DOS EVENTOS
# ============================================================

with st.spinner("⚽ Carregando eventos da partida..."):

    events = sb.events(
        match_id=match_id
    )


# ============================================================
# BARRA DE PROGRESSO
# ============================================================

progress = st.progress(0)

status = st.empty()

status.write("Preparando os dados...")
progress.progress(25)

status.write("Identificando jogadores...")
progress.progress(50)

status.write("Preparando filtros...")
progress.progress(75)

status.write("Dados prontos!")
progress.progress(100)

# Remove os elementos depois do processamento
progress.empty()
status.empty()


# ============================================================
# LISTA DE JOGADORES
# ============================================================

players = sorted(
    events["player"]
    .dropna()
    .unique()
)


# ============================================================
# SELETOR DE JOGADOR
# ============================================================

selected_player = st.selectbox(
    "👤 Selecione o jogador:",
    ["Todos"] + players,
    key="jogador_selecionado"
)


# Atualiza Session State
st.session_state.jogador_filtro = selected_player


# ============================================================
# BOTÕES DE FILTRO
# ============================================================

st.subheader("📌 Tipo de evento")

col1, col2, col3, col4 = st.columns(4)


with col1:

    if st.button(
        "📋 Todos",
        use_container_width=True
    ):

        st.session_state.tipo_filtro = "Todos"


with col2:

    if st.button(
        "🔄 Passes",
        use_container_width=True
    ):

        st.session_state.tipo_filtro = "Pass"


with col3:

    if st.button(
        "🥅 Chutes",
        use_container_width=True
    ):

        st.session_state.tipo_filtro = "Shot"


with col4:

    if st.button(
        "🛡️ Duelos",
        use_container_width=True
    ):

        st.session_state.tipo_filtro = "Duel"


# ============================================================
# MOSTRAR FILTRO ATUAL
# ============================================================

st.info(
    f"Filtro atual: **{st.session_state.tipo_filtro}** | "
    f"Jogador: **{st.session_state.jogador_filtro}**"
)


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

with st.spinner("🔎 Aplicando filtros..."):

    filtered_events = events.copy()


    # --------------------------------------------------------
    # FILTRO DE JOGADOR
    # --------------------------------------------------------

    if st.session_state.jogador_filtro != "Todos":

        filtered_events = filtered_events[
            filtered_events["player"]
            == st.session_state.jogador_filtro
        ]


    # --------------------------------------------------------
    # FILTRO DE EVENTO
    # --------------------------------------------------------

    if st.session_state.tipo_filtro != "Todos":

        filtered_events = filtered_events[
            filtered_events["type"]
            == st.session_state.tipo_filtro
        ]


# ============================================================
# RESULTADO
# ============================================================

st.subheader("📊 Resultado")


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Eventos encontrados",
        len(filtered_events)
    )


with col2:

    st.metric(
        "Eventos na partida",
        len(events)
    )


# ============================================================
# DATAFRAME
# ============================================================

st.subheader("📋 Eventos filtrados")


columns = [
    "minute",
    "second",
    "period",
    "team",
    "player",
    "type"
]


available_columns = [
    column
    for column in columns
    if column in filtered_events.columns
]


df_filtered = filtered_events[
    available_columns
].copy()


st.dataframe(
    df_filtered,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD CSV
# ============================================================

st.divider()

st.subheader("📥 Download")


csv_data = filtered_events.to_csv(
    index=False,
    encoding="utf-8-sig"
)


st.download_button(
    label="⬇️ Baixar eventos filtrados em CSV",
    data=csv_data,
    file_name="eventos_filtrados.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# DOWNLOAD COMPLETO
# ============================================================

csv_complete = events.to_csv(
    index=False,
    encoding="utf-8-sig"
)


st.download_button(
    label="📄 Baixar todos os eventos da partida",
    data=csv_complete,
    file_name="todos_eventos_partida.csv",
    mime="text/csv",
    use_container_width=True
)

#Exercicio 7

# ============================================================
# MÉTRICAS E INDICADORES
# ============================================================

st.divider()
st.header("📊 Métricas e indicadores")

# ============================================================
# 1. TOTAL DE GOLS DA PARTIDA
# ============================================================

# Conta os eventos do tipo Shot que resultaram em gol
total_gols = 0

if "type" in events.columns and "shot_outcome" in events.columns:

    gols = events[
        (events["type"] == "Shot") &
        (events["shot_outcome"] == "Goal")
    ]

    total_gols = len(gols)


# ============================================================
# 2. PASSES BEM-SUCEDIDOS DO JOGADOR
# ============================================================

passes_sucesso = 0

if selected_player != "Todos":

    player_passes = events[
        (events["player"] == selected_player) &
        (events["type"] == "Pass")
    ].copy()

    # No StatsBomb, normalmente:
    # pass_outcome vazio (NaN) = passe completado

    if "pass_outcome" in player_passes.columns:

        passes_sucesso = player_passes[
            player_passes["pass_outcome"].isna()
        ].shape[0]

    else:

        passes_sucesso = len(player_passes)


# ============================================================
# 3. TAXA DE CONVERSÃO DE CHUTES EM GOL
# ============================================================

total_chutes = 0
taxa_conversao = 0

if "type" in events.columns:

    chutes = events[
        events["type"] == "Shot"
    ]

    total_chutes = len(chutes)

    if total_chutes > 0:

        gols_chutes = chutes[
            chutes["shot_outcome"] == "Goal"
        ]

        taxa_conversao = (
            len(gols_chutes) / total_chutes
        ) * 100


# ============================================================
# CARDS DE MÉTRICAS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        label="⚽ Total de gols",
        value=total_gols
    )

with col2:

    if selected_player != "Todos":

        st.metric(
            label=f"🎯 Passes certos — {selected_player}",
            value=passes_sucesso
        )

    else:

        st.metric(
            label="🎯 Passes certos",
            value="Selecione um jogador"
        )

with col3:

    st.metric(
        label="📈 Conversão de chutes",
        value=f"{taxa_conversao:.1f}%"
    )


# ============================================================
# DESTAQUE VISUAL DAS MÉTRICAS
# ============================================================

st.markdown(
    """
    <style>

    /* Cards das métricas */
    div[data-testid="stMetric"] {
        background-color: #f5f7fa;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #dfe3e8;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    /* Valor das métricas */
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: bold;
    }

    /* Primeira métrica - gols */
    div[data-testid="stMetric"]:nth-child(1)
    div[data-testid="stMetricValue"] {
        color: #008000;
    }

    /* Segunda métrica - passes */
    div[data-testid="stMetric"]:nth-child(2)
    div[data-testid="stMetricValue"] {
        color: #0066cc;
    }

    /* Terceira métrica - conversão */
    div[data-testid="stMetric"]:nth-child(3)
    div[data-testid="stMetricValue"] {
        color: #cc6600;
    }

    </style>
    """,
    unsafe_allow_html=True
)
#Exercicio 8

# ============================================================
# FORMULÁRIOS INTERATIVOS
# ============================================================

st.divider()
st.header("📝 Formulários interativos")

with st.form("formulario_analise"):

    st.subheader("⚽ Configurações da análise")

    # --------------------------------------------------------
    # CAIXA DE TEXTO
    # --------------------------------------------------------

    nome_analise = st.text_input(
        "🔎 Nome da análise:",
        value="Análise da partida"
    )

    # --------------------------------------------------------
    # DROPDOWN - JOGADOR
    # --------------------------------------------------------

    jogadores_disponiveis = sorted(
        events["player"]
        .dropna()
        .unique()
        .tolist()
    )

    jogador_form = st.selectbox(
        "👤 Escolha o jogador:",
        ["Todos"] + jogadores_disponiveis
    )

    # --------------------------------------------------------
    # QUANTIDADE DE EVENTOS
    # --------------------------------------------------------

    quantidade_eventos = st.number_input(
        "📊 Quantidade de eventos:",
        min_value=10,
        max_value=len(events),
        value=min(50, len(events)),
        step=10
    )

    # --------------------------------------------------------
    # INTERVALO DE TEMPO
    # --------------------------------------------------------

    st.write("⏱️ Intervalo da partida")

    minuto_inicial, minuto_final = st.slider(
        "Selecione os minutos:",
        min_value=0,
        max_value=120,
        value=(0, 90)
    )

    # --------------------------------------------------------
    # RADIO BUTTON
    # --------------------------------------------------------

    tipo_visualizacao = st.radio(
        "📈 Tipo de visualização:",
        [
            "Todos os eventos",
            "Passes",
            "Chutes",
            "Duelos"
        ],
        horizontal=True
    )

    # --------------------------------------------------------
    # CHECKBOX
    # --------------------------------------------------------

    mostrar_detalhes = st.checkbox(
        "📋 Mostrar detalhes dos eventos",
        value=True
    )

    mostrar_graficos = st.checkbox(
        "📊 Mostrar gráficos",
        value=True
    )

    # --------------------------------------------------------
    # BOTÃO ENVIAR
    # --------------------------------------------------------

    enviar = st.form_submit_button(
        "🚀 Aplicar análise",
        use_container_width=True
    )


# ============================================================
# PROCESSAMENTO DO FORMULÁRIO
# ============================================================

if enviar:

    st.success(
        f"Análise **{nome_analise}** aplicada com sucesso!"
    )

    # --------------------------------------------------------
    # FILTRO POR TEMPO
    # --------------------------------------------------------

    eventos_form = events[
        (events["minute"] >= minuto_inicial) &
        (events["minute"] <= minuto_final)
    ].copy()

    # --------------------------------------------------------
    # FILTRO POR JOGADOR
    # --------------------------------------------------------

    if jogador_form != "Todos":

        eventos_form = eventos_form[
            eventos_form["player"] == jogador_form
        ]

    # --------------------------------------------------------
    # FILTRO POR TIPO DE EVENTO
    # --------------------------------------------------------

    if tipo_visualizacao != "Todos os eventos":

        tipo_evento = tipo_visualizacao.rstrip("s")

        eventos_form = eventos_form[
            eventos_form["type"] == tipo_evento
        ]

    # --------------------------------------------------------
    # LIMITAR QUANTIDADE DE EVENTOS
    # --------------------------------------------------------

    eventos_form = eventos_form.head(
        quantidade_eventos
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    st.subheader("📊 Resultado da análise")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Eventos encontrados",
            len(eventos_form)
        )

    with col2:
        st.metric(
            "Minuto inicial",
            minuto_inicial
        )

    with col3:
        st.metric(
            "Minuto final",
            minuto_final
        )

    # --------------------------------------------------------
    # DETALHES
    # --------------------------------------------------------

    if mostrar_detalhes:

        st.subheader("📋 Eventos selecionados")

        colunas_exibir = [
            "minute",
            "second",
            "period",
            "team",
            "player",
            "type"
        ]

        colunas_disponiveis = [
            coluna
            for coluna in colunas_exibir
            if coluna in eventos_form.columns
        ]

        st.dataframe(
            eventos_form[colunas_disponiveis],
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # GRÁFICO
    # --------------------------------------------------------

    if mostrar_graficos:

        st.subheader("📈 Distribuição dos eventos")

        eventos_por_tipo = (
            eventos_form["type"]
            .value_counts()
            .reset_index()
        )

        eventos_por_tipo.columns = [
            "Tipo",
            "Quantidade"
        ]

        st.bar_chart(
            eventos_por_tipo.set_index("Tipo")
        )



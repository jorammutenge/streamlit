import streamlit as st 
import polars as pl
import plotly.express as px

with open( "styles.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.set_page_config(page_title='Acquired Episode Tracker', layout='wide', page_icon=':bar_chart:')

@st.cache_data
def load_data():
    sheet_id = '1Nq1K9stOYtVX7cW54MJVzzuZv_fTm2XoBPDMgLR6Y_0'
    sheet_name = 'Acquired'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

    cols = list(range(7))
    df = (pl.read_csv(url,
                has_header=False,
                columns=cols,
                skip_rows=1,
                new_columns=['Company','Ticker','Episode_Date','Gain_Since_Episode','NASDAQ_Gain','Multiple_of_Benchmark','Delta_vs_Benchmark'])
    .with_columns(Episode_Date=pl.col.Episode_Date.str.strptime(pl.Date,"%b %d, %Y"),
                Gain_Since_Episode=pl.col.Gain_Since_Episode.str.replace("%","").cast(pl.Float64),
                NASDAQ_Gain=pl.col.NASDAQ_Gain.str.replace("%","").cast(pl.Float64),
                Delta_vs_Benchmark=pl.col.Delta_vs_Benchmark.str.replace("%","").cast(pl.Float64))
    .with_columns(pl.when(pl.col('Multiple_of_Benchmark') >= 0)
                .then(pl.lit('Positive'))
                .when(pl.col('Multiple_of_Benchmark') < 0)
                .then(pl.lit('Negative'))
                .alias('Gain_or_Loss'))
    .with_columns(Performance=pl.col('Gain_Since_Episode').cut([-20, 0, 10, 50], labels=['Worst', 'Bad', 'Good', 'Better', 'Best']))
    .to_pandas()
    )
    return df

df = load_data()

########

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
performance = st.sidebar.multiselect(
    "Select the Performance by Benchmark:",
    options=df["Performance"].unique(),
    default=df["Performance"].unique()[0]
)

df_filt = df.query(
    "Performance == @performance"
)


# Chart 1
fig1 = px.bar(df_filt, x='Company', y='Multiple_of_Benchmark',
              color='Gain_or_Loss', color_discrete_sequence=['#5cc489', '#ff0000'],
              labels={'Multiple_of_Benchmark': 'Multiple of Benchmark', 'Company': ''},
              title='Company Performance Since Episode Release',
              height=400, width=1000)

fig1.update_layout(
    xaxis=dict(tickangle=90),
    font_family="Poppins",
    title={'text': '<b>Company Performance Since Episode Release</b>', 'font_size':30},
    plot_bgcolor='#243039',
    paper_bgcolor='#243039',
    legend_title=None,
    bargap=0.2,
    font_color="#ffffff",
    title_font_color="#ffffff",
)

# Chart 2
fig2 = px.bar(df_filt, x='Company', y=['Gain_Since_Episode', 'NASDAQ_Gain'],
              color_discrete_sequence=['#5cc489', '#483D8B'],
              labels={'value': 'Gain or Loss', 'Company': '', 'Performance': ''},
              height=400, width=1000,
              barmode='group')

fig2.update_layout(
    xaxis=dict(tickangle=90),
    font_family="Poppins",
    title={'text': '<b>Gain since Episode Release vs NASDAQ Gain</b>','font_size':30},
    plot_bgcolor='#243039',
    paper_bgcolor='#243039',
    legend_title=None,
    bargap=0.2,
    font_color="#ffffff",
    title_font_color="#ffffff"
)

# Streamlit App

# Set the title with green color
st.markdown("<h1 style='color: #5cc489;'>Acquired.fm Stock Tracker</h1>", unsafe_allow_html=True)

st.markdown("""---""")


# st.header("Chart 1: Company Performance Since Episode Release")
st.plotly_chart(fig1, use_container_width=True)

# st.header("Chart 2: Gain since Episode Release vs NASDAQ Gain")
st.plotly_chart(fig2, use_container_width=True)


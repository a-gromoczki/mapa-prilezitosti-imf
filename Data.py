import streamlit as st
import pandas as pd
from pathlib import Path

from mapatools.chartjsbubble import chartjs_plot
from mapatools.highchartpolararea import chart_highcharts_variable_pie
from mapatools.variable_names import get_plot_and_hover_display_names, get_hover_data
import streamlit.components.v1 as components
from mapatools.visualsetup import load_visual_identity

DATA_DIR = Path("BACI_analysis/outputs")


def available_years():
    years = []
    for f in DATA_DIR.glob("SVK_*.csv"):
        stem = f.stem  # e.g. "SVK_2023"
        parts = stem.split("_")
        if len(parts) == 2 and parts[1].isdigit():
            years.append(parts[1])
    return sorted(set(years))


FX_USD_EUR = {
    "2022": 0.95,
    "2023": 0.93,
    "2024": 0.92,
}


def USDtoEURdefault(year):
    if year in FX_USD_EUR:
        return FX_USD_EUR[year]
    # Fallback – use last known FX
    return list(FX_USD_EUR.values())[-1]


YEARS = available_years()
if not YEARS:
    raise RuntimeError("No SVK_YYYY.csv files found in BACI_analysis/outputs.")

st.set_page_config(
    page_title="Mapa Príležitostí",
    page_icon="resources/imf_favicon.ico",
    layout="wide"
)
# Loading custom CSS and identity assets
load_visual_identity("resources/header.jpg")
col1, col2 = st.columns([11, 4])
col1.subheader("")
col2.subheader("")
col2.subheader("Nastavenia grafu")

# Sidebar: Year selection
year = col2.radio("Rok", YEARS, index=len(YEARS) - 1, horizontal=True)
topsubcol2 = col2.container()

@st.cache_resource
def load_data(datayear):
    USD_to_eur = USDtoEURdefault(datayear)
    taxonomy = pd.read_csv("BACI_analysis/outputs/PlnaDatabaze3.0.csv")
    SVK = pd.read_csv('BACI_analysis/outputs/SVK_' + datayear + '.csv')
    GreenProducts = taxonomy.merge(SVK, how='left', left_on='HS_ID', right_on='prod')
       
    df = GreenProducts.rename(columns={
        'ExportValue': 'Slovenský export ' + datayear + ' EUR',
        'export_Rank': 'Poradie Slovenska na svetovom trhu ' + datayear,
        'pci': 'Komplexita výrobku (unikátnosť) ' + datayear,
        'relatedness': 'Príbuznosť SVK ' + datayear,
        'PCI_Rank': 'Rebríček komplexity ' + datayear,
        'PCI_Percentile': 'Percentil komplexity ' + datayear,
        'relatedness_Rank': 'Rebríček príbuznosti' + datayear,
        'relatedness_Percentile': 'Percentil príbuznosti ' + datayear,
        'WorldExport': 'Veľkosť svetového trhu ' + datayear + ' EUR',
        'EUWorldMarketShare': 'EÚ Svetový Podiel ' + datayear + ' %',
        'euhhi': 'Koncentrácia európskeho exportu ' + datayear,
        'hhi': 'Koncentrácia svetového trhu ' + datayear,
        'SVK_WorldMarketShare': 'Podiel Slovenska na svetovom trhu ' + datayear + ' %',
        'SVK_EUMarketShare': 'SVK-EÚ Podiel ' + datayear + ' %',
        'rca': 'RCA ' + datayear,
        'EUTopExporter': 'EÚ Najväčší Exportér ' + datayear,
        'CZ_Nazev': 'Názov',
    })
    df = df[df.Included == "IN"]
    df['SVK-EÚ Podiel ' + datayear + ' %'] = 100 * df['SVK-EÚ Podiel ' + datayear + ' %']
    df['EÚ Svetový Podiel ' + datayear + ' %'] = 100 * df['EÚ Svetový Podiel ' + datayear + ' %']
    df['Podiel Slovenska na svetovom trhu ' + datayear + ' %'] = 100 * df['Podiel Slovenska na svetovom trhu ' + datayear + ' %']
    df['Slovenský export ' + datayear + ' USD'] = df['Slovenský export ' + datayear + ' EUR']
    df['Slovenský export ' + datayear + ' EUR'] = USD_to_eur * df['Slovenský export ' + datayear + ' EUR']
    df['Veľkosť svetového trhu ' + datayear + ' USD'] = df['Veľkosť svetového trhu ' + datayear + ' EUR']
    df['Veľkosť svetového trhu ' + datayear + ' EUR'] = USD_to_eur * df['Veľkosť svetového trhu ' + datayear + ' EUR']
    df['Kód výrobku HS6'] = df['HS_ID'].astype(str)
    df['HS_Lookup'] = df['Kód výrobku HS6'] + " - " + df['Názov']
    total_svk_export = USD_to_eur * SVK['ExportValue'].sum()
    total_svk_green_export = df['Slovenský export ' + datayear + ' EUR'].sum()
    return df, total_svk_export, total_svk_green_export


def load_all_years(years):
    dfs = {}
    total_exports = {}
    total_green_exports = {}
    for y in years:
        df_y, total_y, green_total_y = load_data(y)
        dfs[y] = df_y
        total_exports[y] = total_y
        total_green_exports[y] = green_total_y
    return dfs, total_exports, total_green_exports


# Define the default year_placeholder and get plotting lists
year_placeholder = " ‎"
plot_display_names, hover_display_data = get_plot_and_hover_display_names(year_placeholder)

# Sidebar selection boxes using display names
x_axis = col2.selectbox("Vyber osu X:", plot_display_names, index=0)
y_axis = col2.selectbox("Vyber osu Y:", plot_display_names, index=1)
markersize = col2.selectbox("Veľkosť podľa:", plot_display_names, index=4)

# Load datasets for all available years
dfs_by_year, total_export_by_year, green_export_by_year = load_all_years(YEARS)
df = dfs_by_year[year]
svk_total_export = total_export_by_year[year]
svk_total_green_export = green_export_by_year[year]

# Initialize the session state for filtering by groups
if 'filtrovat_dle_skupin' not in st.session_state:
    st.session_state.filtrovat_dle_skupin = False

with col2:
    # Fixed label button, with a key
    if st.button("Prepnúť zobrazenie", use_container_width=True, key="toggle_filter_button"):
        st.session_state.filtrovat_dle_skupin = not st.session_state.filtrovat_dle_skupin

# **MOVE THE SESSION STATE FILTER MODE CHECK UP HERE** so that "color" is defined before filtering.
if st.session_state.filtrovat_dle_skupin:
    col2.markdown("**Aktuálne zobrazenie:** 🧩 Jednotlivé skupiny")
    color = 'Kategorie'
    # Use the current year's dataframe for group options.
    cur_df = dfs_by_year[year]
    skupiny = cur_df['Skupina'].unique()
    Skupina = col2.segmented_control('Skupina', skupiny, default=skupiny[5])
else:
    col2.markdown("**Aktuálne zobrazenie:** ✅ Všetky zelené produkty")
    color = 'Skupina'

# Define the filtering function
def apply_filters(df, year_str, x_axis, y_axis, color, markersize):
    filtered = df.copy()

    # If filtering by groups is active, assume Skupina is defined already.
    if st.session_state.filtrovat_dle_skupin:
        filtered = filtered[filtered['Skupina'].isin([Skupina])]

    for filter in st.session_state.filters:
        if filter['column'] is not None and filter['range'] is not None:
            colname = filter['column'].replace(year_placeholder, year_str)
            filtered = filtered[
                (filtered[colname] >= filter['range'][0]) &
                (filtered[colname] <= filter['range'][1])
            ]

    # Replace negative marker sizes with 0
    col_ms = markersize.replace(year_placeholder, year_str)
    filtered[col_ms] = filtered[col_ms].clip(lower=0)

    # Drop rows with missing values for plotting columns
    filtered = filtered.dropna(subset=[
        x_axis.replace(year_placeholder, year_str),
        y_axis.replace(year_placeholder, year_str),
        color,
        col_ms
    ])

    return filtered

# Ensure session state filters exist
if 'filters' not in st.session_state:
    st.session_state.filters = []

# Calculate filtered data for all years
filtered_by_year = {
    y: apply_filters(dfs_by_year[y], y, x_axis, y_axis, color, markersize)
    for y in YEARS
}
filtered_df = filtered_by_year[year]

# Filter control buttons
subcol1, subcol2 = col2.columns(2)
with subcol1:
    if st.button("Filtrovanie", use_container_width=True):
        st.session_state.filters.append({'column': None, 'range': None})
with subcol2:
    if st.button("Odstrániť filtre", use_container_width=True):
        st.session_state.filters = []

# Display existing filters using display names
for i, filter in enumerate(st.session_state.filters):
    filter_col = col2.selectbox(f"Filter {i+1}", plot_display_names, key=f"filter_col_{i}")
    filter_min, filter_max = df[filter_col.replace(year_placeholder, year)].min(), df[filter_col.replace(year_placeholder, year)].max()
    filter_range = col2.slider(
        f"Filter {i+1}",
        float(filter_min),
        float(filter_max),
        (float(filter_min), float(filter_max)),
        key=f"filter_range_{i}"
    )
    st.session_state.filters[i]['column'] = filter_col
    st.session_state.filters[i]['range'] = filter_range

# Apply numerical filters (on already filtered_df)
for filter in st.session_state.filters:
    if filter['column'] is not None and filter['range'] is not None:
        filtered_df = filtered_df[
            (filtered_df[filter['column'].replace(year_placeholder, year)] >= filter['range'][0]) &
            (filtered_df[filter['column'].replace(year_placeholder, year)] <= filter['range'][1])
        ]

# Update axis names after replacing placeholder
markersize = markersize.replace(year_placeholder, year)
x_axis = x_axis.replace(year_placeholder, year)
y_axis = y_axis.replace(year_placeholder, year)

# Ensure no negative values and remove NA for plotting
filtered_df[markersize] = filtered_df[markersize].clip(lower=0)
filtered_df = filtered_df.dropna(subset=[x_axis, y_axis, color, markersize])

HS_select = topsubcol2.multiselect("Filtrovať jednotlivé produkty", filtered_df['HS_Lookup'])
st.divider()

hover_info = col2.multiselect("Čo sa zobrazí pri prechode myšou:", hover_display_data, default=['Názov'])
hover_data = get_hover_data(year, year_placeholder, hover_info, x_axis, y_axis, markersize)

bottom_text = "Analýza je založená na obchodných dátach UN COMTRADE, ktoré sú vyčistené organizáciou CEPII a publikované každý rok ako dataset BACI"

if st.session_state.filtrovat_dle_skupin is False:
    if HS_select == []:
        chart_js = chartjs_plot(filtered_df, markersize, hover_data, color, x_axis, y_axis, year,
                                  chart_title="Slovenské zelené príležitosti", bottom_text=bottom_text)
    else:
        chart_js = chartjs_plot(filtered_df[filtered_df['HS_Lookup'].isin(HS_select)],
                                  markersize, hover_data, color, x_axis, y_axis, year,
                                  chart_title="Slovenské zelené príležitosti", bottom_text=bottom_text)
elif st.session_state.filtrovat_dle_skupin is True and Skupina is None:
    chart_js = None
elif st.session_state.filtrovat_dle_skupin is True and Skupina is not None:
    if HS_select == []:
        chart_js = chartjs_plot(filtered_df, markersize, hover_data, color, x_axis, y_axis, year,
                                  chart_title=Skupina, bottom_text=bottom_text)
    else:
        chart_js = chartjs_plot(filtered_df[filtered_df['HS_Lookup'].isin(HS_select)],
                                  markersize, hover_data, color, x_axis, y_axis, year,
                                  chart_title=Skupina, bottom_text=bottom_text)

# Render chart in main area
html_bytes = chart_js
with col1:
    components.html(chart_js, height=800,width=1500)

# Determine previous and current years for comparative views
if len(YEARS) >= 2:
    prev_year, curr_year = YEARS[-2], YEARS[-1]
else:
    prev_year = curr_year = YEARS[-1]

filtered_prev = filtered_by_year[prev_year]
filtered_curr = filtered_by_year[curr_year]

svk_export_prev = total_export_by_year[prev_year]
svk_export_curr = total_export_by_year[curr_year]
svk_green_export_prev = green_export_by_year[prev_year]
svk_green_export_curr = green_export_by_year[curr_year]

# Example: render the polar area chart in a Streamlit component
polar_js_skupiny = chart_highcharts_variable_pie(
    filtered_prev,
    filtered_curr,
    svk_export_prev,
    svk_export_curr,
    svk_green_export_prev,
    svk_green_export_curr,
    group_field="Skupina",
    chart_title="Rast exportu podľa skupiny",
    bottom_text=(
        f"Šírka koláča vyjadruje % z celkového slovenského exportu v roku {curr_year}<br>"
        f"Vzdialenosť dielu koláča od stredu vyjadruje rast skupiny medzi rokmi {prev_year} a {curr_year}"
    ),
    usd_to_eur_22=USDtoEURdefault(prev_year),
    usd_to_eur_23=USDtoEURdefault(curr_year),
    year_22=prev_year,
    year_23=curr_year,
)
polar_js_kategorie = chart_highcharts_variable_pie(
    filtered_prev,
    filtered_curr,
    svk_export_prev,
    svk_export_curr,
    svk_green_export_prev,
    svk_green_export_curr,
    group_field="Kategorie",
    chart_title="Rast zeleného exportu podľa kategórie",
    bottom_text=(
        f"Šírka koláča vyjadruje % zo slovenského zeleného exportu v roku {curr_year}<br>"
        f"Vzdialenosť dielu koláča od stredu vyjadruje rast kategórie medzi rokmi {prev_year} a {curr_year}"
    ),
    usd_to_eur_22=USDtoEURdefault(prev_year),
    usd_to_eur_23=USDtoEURdefault(curr_year),
    relative_to_green_only=True,
    year_22=prev_year,
    year_23=curr_year,
)

# Comparison columns - now you can compare metrics between prev_year and curr_year
if HS_select == []:
    pie1, pie2 = st.columns(2)
    with pie1:
        st.components.v1.html(polar_js_skupiny, height=690, width=1500)
    with pie2:
        st.components.v1.html(polar_js_kategorie, height=690, width=1500)
    st.divider()
    mcol1, mcol2, mcol3 = st.columns(3)
    selected_SVK_growth = (
        filtered_curr[f"Slovenský export {curr_year} EUR"].sum() / USDtoEURdefault(curr_year)
        - filtered_prev[f"Slovenský export {prev_year} EUR"].sum() / USDtoEURdefault(prev_year)
    )
    selected_SVK_growth_perc = selected_SVK_growth / (
        filtered_prev[f"Slovenský export {prev_year} EUR"].sum() / USDtoEURdefault(prev_year)
    )
    mcol1.metric(
        f"Vybraný slovenský export za rok {year}",
        "{:,.0f}".format(sum(filtered_df[f"Slovenský export {year} EUR"]) / 1e9),
        "miliard EUR",
    )
    mcol2.metric(
        f"Rast vybraného slovenského exportu medzi rokmi {prev_year} a {curr_year}",
        "{:,.0f}".format(selected_SVK_growth / 1e6),
        "miliónov USD",
    )
    mcol3.metric(
        f"Rast vybraného slovenského exportu medzi rokmi {prev_year} a {curr_year}",
        "{:,.1%}".format(selected_SVK_growth_perc),
        "%",
    )
else:
    mcol1, mcol2, mcol3 = st.columns(3)
    lookup_year = filtered_df["HS_Lookup"].isin(HS_select)
    lookup_prev = filtered_prev["HS_Lookup"].isin(HS_select)
    lookup_curr = filtered_curr["HS_Lookup"].isin(HS_select)
    selected_SVK_growth = (
        filtered_curr[lookup_curr][f"Slovenský export {curr_year} EUR"].sum()
        / USDtoEURdefault(curr_year)
        - filtered_prev[lookup_prev][f"Slovenský export {prev_year} EUR"].sum()
        / USDtoEURdefault(prev_year)
    )
    selected_SVK_growth_perc = selected_SVK_growth / (
        filtered_prev[lookup_prev][f"Slovenský export {prev_year} EUR"].sum()
        / USDtoEURdefault(prev_year)
    )
    mcol1.metric(
        f"Vybraný slovenský export za rok {year}",
        "{:,.0f}".format(
            sum(filtered_df[lookup_year][f"Slovenský export {year} EUR"]) / 1e6
        ),
        "miliónov EUR",
    )
    mcol2.metric(
        f"Rast vybraného slovenského exportu medzi rokmi {prev_year} a {curr_year}",
        "{:,.0f}".format(selected_SVK_growth / 1e6),
        "miliónov USD",
    )
    mcol3.metric(
        f"Rast vybraného slovenského exportu medzi rokmi {prev_year} a {curr_year}",
        "{:,.1%}".format(selected_SVK_growth_perc),
        "%",
    )

total_SVK_growth = (
    svk_export_curr / USDtoEURdefault(curr_year)
    - svk_export_prev / USDtoEURdefault(prev_year)
)
total_SVK_growth_perc = total_SVK_growth / (
    svk_export_prev / USDtoEURdefault(prev_year)
)
mcol1.metric(
    f"Celkový slovenský export za rok {year}",
    "{:,.0f}".format(svk_total_export / 1e9),
    "miliard EUR",
)
mcol2.metric(
    f"Rast celkového slovenského exportu medzi rokmi {prev_year} a {curr_year}",
    "{:,.0f}".format(total_SVK_growth / 1e9),
    "miliard USD",
)
mcol3.metric(
    f"Rast celkového slovenského exportu medzi rokmi {prev_year} a {curr_year}",
    "{:,.1%}".format(total_SVK_growth_perc),
    "%",
)

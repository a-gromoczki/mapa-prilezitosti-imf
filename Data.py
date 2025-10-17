import streamlit as st
import pandas as pd

from mapatools.chartjsbubble import chartjs_plot
from mapatools.highchartpolararea import chart_highcharts_variable_pie
from mapatools.variable_names import get_plot_and_hover_display_names, get_hover_data
import streamlit.components.v1 as components
from mapatools.visualsetup import load_visual_identity

st.set_page_config(
    page_title="Mapa Příležitostí",
    page_icon="resources/logo_notext.svg",
    layout="wide"
)
# Loading custom CSS and identity assets
load_visual_identity("resources/header.jpg")
col1, col2 = st.columns([11, 4])
col1.subheader("")
col2.subheader("")
col2.subheader("Nastavení grafu")

# Sidebar: Year selection
year = col2.radio("Rok", ["2022", "2023"], index=1,horizontal=True)
topsubcol2 = col2.container()
def USDtoEURdefault(year):
    if year == "2022":
        return 0.95
    elif year == "2023":
        return 0.93

@st.cache_resource
def load_data(datayear):
    USD_to_eur = USDtoEURdefault(datayear)
    taxonomy = pd.read_csv("BACI_analysis/outputs/PlnaDatabaze3.0.csv")
    SVK = pd.read_csv('BACI_analysis/outputs/SVK_' + datayear + '.csv')
    GreenProducts = taxonomy.merge(SVK, how='left', left_on='HS_ID', right_on='prod')
       
    df = GreenProducts.rename(columns={
        'ExportValue': 'Slovenský export ' + datayear + ' EUR',
        'export_Rank': 'Pořadí Slovenska na světovém trhu ' + datayear,
        'pci': 'Komplexita výrobku (unikátnost) ' + datayear,
        'relatedness': 'Příbuznost SVK ' + datayear,
        'PCI_Rank': 'Žebříček komplexity ' + datayear,
        'PCI_Percentile': 'Percentil komplexity ' + datayear,
        'relatedness_Rank': 'Žebříček příbuznosti' + datayear,
        'relatedness_Percentile': 'Percentil příbuznosti ' + datayear,
        'WorldExport': 'Velikost světového trhu ' + datayear + ' EUR',
        'EUWorldMarketShare': 'EU Světový Podíl ' + datayear + ' %',
        'euhhi': 'Koncentrace evropského exportu ' + datayear,
        'hhi': 'Koncentrace světového trhu ' + datayear,
        'SVK_WorldMarketShare': 'Podíl Slovenska na světovém trhu ' + datayear + ' %',
        'SVK_EUMarketShare': 'SVK-EU Podíl ' + datayear + ' %',
        'rca': 'RCA ' + datayear,
        'EUTopExporter': 'EU Největší Exportér ' + datayear,
        'CZ_Nazev': 'Název',
    })
    df = df[df.Included == "IN"]
    df['SVK-EU Podíl ' + datayear + ' %'] = 100 * df['SVK-EU Podíl ' + datayear + ' %']
    df['EU Světový Podíl ' + datayear + ' %'] = 100 * df['EU Světový Podíl ' + datayear + ' %']
    df['Podíl Slovenska na světovém trhu ' + datayear + ' %'] = 100 * df['Podíl Slovenska na světovém trhu ' + datayear + ' %']
    df['Slovenský export ' + datayear + ' USD'] = df['Slovenský export ' + datayear + ' EUR']
    df['Slovenský export ' + datayear + ' EUR'] = USD_to_eur * df['Slovenský export ' + datayear + ' EUR']
    df['Velikost světového trhu ' + datayear + ' USD'] = df['Velikost světového trhu ' + datayear + ' EUR']
    df['Velikost světového trhu ' + datayear + ' EUR'] = USD_to_eur * df['Velikost světového trhu ' + datayear + ' EUR']
    df['Kód výrobku HS6'] = df['HS_ID'].astype(str)
    df['HS_Lookup'] = df['Kód výrobku HS6'] + " - " + df['Název']
    total_svk_export = USD_to_eur * SVK['ExportValue'].sum()
    total_svk_green_export = df['Slovenský export ' + datayear + ' EUR'].sum()
    return df, total_svk_export, total_svk_green_export

# Define the default year_placeholder and get plotting lists
year_placeholder = " ‎"
plot_display_names, hover_display_data = get_plot_and_hover_display_names(year_placeholder)

# Sidebar selection boxes using display names
x_axis = col2.selectbox("Vyber osu X:", plot_display_names, index=0)
y_axis = col2.selectbox("Vyber osu Y:", plot_display_names, index=1)
markersize = col2.selectbox("Velikost dle:", plot_display_names, index=4)

# Load datasets for both years
df_2022, svk_export_22, svk_green_export_22 = load_data("2022")
df_2023, svk_export_23, svk_green_export_23 = load_data("2023")
if year == "2022":
    df = df_2022
    svk_total_export = svk_export_22
    svk_total_green_export = svk_export_22
else:
    df = df_2023
    svk_total_export = svk_export_23
    svk_total_green_export = svk_export_23

# Initialize the session state for filtering by groups
if 'filtrovat_dle_skupin' not in st.session_state:
    st.session_state.filtrovat_dle_skupin = False

with col2:
    # Fixed label button, with a key
    if st.button("Přepnout zobrazení", use_container_width=True, key="toggle_filter_button"):
        st.session_state.filtrovat_dle_skupin = not st.session_state.filtrovat_dle_skupin

# **MOVE THE SESSION STATE FILTER MODE CHECK UP HERE** so that "color" is defined before filtering.
if st.session_state.filtrovat_dle_skupin:
    col2.markdown("**Aktuální zobrazení:** 🧩 Jednotlivé skupiny")
    color = 'Kategorie'
    # Use the current year's dataframe for group options.
    cur_df = df_2022 if year == "2022" else df_2023
    skupiny = cur_df['Skupina'].unique()
    Skupina = col2.segmented_control('Skupina', skupiny, default=skupiny[5])
else:
    col2.markdown("**Aktuální zobrazení:** ✅ Všechny zelené produkty")
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

# Calculate filtered data for both years
filtered_df_2022 = apply_filters(df_2022, "2022", x_axis, y_axis, color, markersize)
filtered_df_2023 = apply_filters(df_2023, "2023", x_axis, y_axis, color, markersize)
filtered_df = filtered_df_2022 if year == "2022" else filtered_df_2023

# Filter control buttons
subcol1, subcol2 = col2.columns(2)
with subcol1:
    if st.button("Filtrování", use_container_width=True):
        st.session_state.filters.append({'column': None, 'range': None})
with subcol2:
    if st.button("Odstranit filtry", use_container_width=True):
        st.session_state.filters = []

# Display existing filters using display names
for i, filter in enumerate(st.session_state.filters):
    filter_col = col2.selectbox(f"Filtr {i+1}", plot_display_names, key=f"filter_col_{i}")
    filter_min, filter_max = df[filter_col.replace(year_placeholder, year)].min(), df[filter_col.replace(year_placeholder, year)].max()
    filter_range = col2.slider(
        f"Filtr {i+1}",
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

HS_select = topsubcol2.multiselect("Filtrovat jednotlivé produkty", filtered_df['HS_Lookup'])
st.divider()

hover_info = col2.multiselect("Co se zobrazí při najetí myší:", hover_display_data, default=['Název'])
hover_data = get_hover_data(year, year_placeholder, hover_info, x_axis, y_axis, markersize)

bottom_text = "Analýza je založená na obchodních datech UN COMTRADE, která jsou vyčištěna organizací CEPII a publikována každý rok jako dataset BACI"

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

# Example: render the polar area chart in a Streamlit component
polar_js_skupiny = chart_highcharts_variable_pie(filtered_df_2022, filtered_df_2023, svk_export_22,svk_export_23,svk_green_export_22,svk_green_export_23,
                              group_field="Skupina",
                              chart_title="Rast exportu podľa skupiny",
                              bottom_text="Šírka koláča vyjadruje % z celkového slovenského exportu v roku 2023<br>Vzdialenosť dielu koláča od stredu vyjadruje rast skupiny medzi rokmi 2022 a 2023",
                              usd_to_eur_22=USDtoEURdefault("2022"),
                              usd_to_eur_23=USDtoEURdefault("2023"))
polar_js_kategorie = chart_highcharts_variable_pie(filtered_df_2022, filtered_df_2023, svk_export_22,svk_export_23,svk_green_export_22,svk_green_export_23,
                              group_field="Kategorie",
                              chart_title="Rast zeleného exportu podľa kategórie",
                              bottom_text="Šírka koláča vyjadruje % zo slovenského zeleného exportu v roku 2023<br>Vzdialenosť dielu koláča od stredu vyjadruje rast kategórie medzi rokmi 2022 a 2023",
                              usd_to_eur_22=USDtoEURdefault("2022"),
                              usd_to_eur_23=USDtoEURdefault("2023"),
                              relative_to_green_only=True)


# Comparison columns - now you can compare metrics between 2022 and 2023
if HS_select == []:
    pie1,pie2 = st.columns(2)
    with pie1:
        st.components.v1.html(polar_js_skupiny, height=690,width=1500)
    with pie2:
        st.components.v1.html(polar_js_kategorie, height=690,width=1500)
    st.divider()
    mcol1, mcol2, mcol3, = st.columns(3)
    selected_SVK_growth = filtered_df_2023['Slovenský export 2023 EUR'].sum()/USDtoEURdefault("2023") - filtered_df_2022['Slovenský export 2022 EUR'].sum()/USDtoEURdefault("2022")
    selected_SVK_growth_perc = selected_SVK_growth/(filtered_df_2022['Slovenský export 2022 EUR'].sum()/USDtoEURdefault("2022"))
    mcol1.metric("Vybraný slovenský export za rok "+year+"", "{:,.0f}".format(sum(filtered_df['Slovenský export '+year+' EUR'])/1e9),'miliard EUR' )
    mcol2.metric("Rast vybraného slovenského exportu medzi rokmi 2022 a 2023", "{:,.0f}".format(selected_SVK_growth/1e6), "miliónov USD")
    mcol3.metric("Rast vybraného slovenského exportu medzi rokmi 2022 a 2023", "{:,.1%}".format(selected_SVK_growth_perc), "%")


else:
    mcol1, mcol2, mcol3, = st.columns(3)
    lookup_year = filtered_df['HS_Lookup'].isin(HS_select)
    lookup_22 = filtered_df_2022['HS_Lookup'].isin(HS_select)
    lookup_23 = filtered_df_2023['HS_Lookup'].isin(HS_select)
    selected_SVK_growth = filtered_df_2023[lookup_23]['Slovenský export 2023 EUR'].sum()/USDtoEURdefault("2023") - filtered_df_2022[lookup_22]['Slovenský export 2022 EUR'].sum()/USDtoEURdefault("2022")
    selected_SVK_growth_perc = selected_SVK_growth/(filtered_df_2022[lookup_22]['Slovenský export 2022 EUR'].sum()/USDtoEURdefault("2022"))
    mcol1.metric("Vybraný slovenský export za rok "+year+"", "{:,.0f}".format(sum(filtered_df[lookup_year]['Slovenský export '+year+' EUR'])/1e6),'miliónov EUR' )
    mcol2.metric("Rast vybraného slovenského exportu medzi rokmi 2022 a 2023", "{:,.0f}".format(selected_SVK_growth/1e6), "miliónov USD")
    mcol3.metric("Rast vybraného slovenského exportu medzi rokmi 2022 a 2023", "{:,.1%}".format(selected_SVK_growth_perc), "%")

total_SVK_growth = svk_export_23/USDtoEURdefault("2023") - svk_export_22/USDtoEURdefault("2022")
total_SVK_growth_perc = total_SVK_growth/(svk_export_22/USDtoEURdefault("2022"))
mcol1.metric("Celkový slovenský export za rok "+year+"", "{:,.0f}".format(svk_total_export/1e9),'miliard EUR' )
mcol2.metric("Rast celkového slovenského exportu medzi rokmi 2022 a 2023", "{:,.0f}".format(total_SVK_growth/1e9), "miliard USD")
mcol3.metric("Rast celkového slovenského exportu medzi rokmi 2022 a 2023", "{:,.1%}".format(total_SVK_growth_perc), "%")

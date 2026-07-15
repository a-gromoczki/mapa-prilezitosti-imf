import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
import base64
from MapaPrilezitosti.mapatools.visualsetup import load_visual_identity
st.set_page_config(
    page_title="Mapa Příležitostí",
    page_icon="favicon.png",
    layout="wide"
)
#Loading loads of custom css in markdown
load_visual_identity("header.jpg")

st.logo('logo_notext.svg',size='large',icon_image='logo_notext.svg')
col0,col1, colx,col2, = st.columns([1,4, 1,2])
#col1.title("Mapa příležitostí")
logocol1,logocol2 = col1.columns([2,3])
logocol1.image('logo_web.svg',use_container_width=True)
# Sidebar for selecting variables
col2.title("")

col2.subheader("Nastavení Grafu")

# Prumer CNB za rok 2022
USD_to_czk = 23.360

color_discrete_map = {
    'A02. Doprava': '#d6568c',
    'A03. Budovy': '#274001',
    'A04. Výroba nízkoemisní elektřiny a paliv': '#f29f05',
    'A05. Ukládání energie': '#f25c05',
    'A06. Energetické sítě': '#828a00',
    'E01. Měřící a diagnostické přístroje; Monitoring': '#4d8584',
    'A01. Výroba, nízkoemisní výrobní postupy': '#a62f03',
    'B02. Cirkularita a odpady': '#400d01',

    'A02c. Cyklistika a jednostopá': '#808080',
    'A03a. Snižování energetické náročnosti budov': '#94FFB5',
    'A04f. Jádro': '#8F7C00',
    'A05b. Vodik a čpavek': '#9DCC00',
    'A06a. Distribuce a přenos elektřiny': '#C20088',
    'A04a. Větrná': '#003380',
    'E0f. Měření v energetice a síťových odvětvích (HS9028 - 9030, 903210)': '#FFA405',
    'E01c. Měření okolního prostředí (HS9025)': '#FFA8BB',
    'E01i. Ostatní': '#426600',
    'A02a. Železniční (osobní i nákladní)': '#FF0010',
    'E01h. Surveying / Zeměměřičství (HS 9015)': '#5EF1F2',
    'A01a. Nízkoemisní výroba': '#00998F',
    'A04g. Efektivní využití plynu a vodíku': '#E0FF66',
    'E01e. Chemická analýza (HS9027)': '#740AFF',
    'A04b. Solární': '#990000',
    'A03b. Elektrifikace tepelného hospodářství': '#FFFF80',
    'A05a. Baterie': '#FFE100',
    'E01d. Měření vlastností plynů a tekutnin (HS9026)': '#FF5005',
    'E01a. Optická měření (HS 9000 - 9013, HS 903140)': '#F0A0FF',
    'B02b. Cirkularita, využití odpadu': '#0075DC',
    'A05c. Ostatní ukládání': '#993F00',
    'A01c. Elektrifikace výrobních postupů': '#4C005C',
    'A03b. Elektrifikace domácností': '#191919',

    'Díly a vybavení': '#005C31',
    'Zateplení, izolace': '#2BCE48',
    'Komponenty pro jadernou energetiku': '#FFCC99',
    'Vodík (elektrolyzéry)': '#808080',
    'Transformační stanice a další síťové komponenty': '#94FFB5',
    'Komponenty pro větrnou energetiku': '#8F7C00',
    'Termostaty': '#9DCC00',
    'Termometry': '#C20088',
    'Ostatní': '#003380',
    'Nové lokomotivy a vozy': '#FFA405',
    'Surveying / Zeměměřičství': '#FFA8BB',
    'Nízkoemisní výroby ostatní': '#426600',
    'Komponenty pro výrobu energie z plynů': '#FF0010',
    'Spektrometry': '#5EF1F2',
    'Komponenty pro solární energetiku': '#00998F',
    'Tepelná čerpadla a HVAC': '#E0FF66',
    'Infrastruktura (nové tratě a elektrifikace stávajících)': '#740AFF',
    'Baterie': '#990000',
    'Měření odběru a výroby plynů, tekutin, elektřiny': '#FFFF80',
    'Komponenty pro vodní energetiku': '#FFE100',
    'Měření vlastností plynů a tekutin': '#FF5005',
    'Optická měření': '#F0A0FF',
    'Materiálové využití': '#0075DC',
    'Měření ionizujícího záření': '#993F00',
    'Ostatní ukládání (přečerpávací vodní, ohřátá voda,…)': '#4C005C',
    'Hydrometry': '#191919',
    'Elektrifikace ve výrobě': '#005C31',
    'Domácí elektrické spotřebiče': '#2BCE48',
    'Chromatografy': '#FFCC99',
    'Osciloskopy': '#808080',
}


# Load data
@st.cache_data
def load_data():
    # Replace with the path to your data file
    #df                          = pd.read_csv('GreenComplexity_CZE_2022.csv')
    #url = 'https://docs.google.com/spreadsheets/d/1mhv7sJC5wSqJRXdfyFaWtBuEpX6ENj2c/gviz/tq?tqx=out:csv'
    #taxonomy = pd.read_csv(url)
    taxonomy = pd.read_csv('data.csv')
    CZE = pd.read_csv('CZE.csv')
    GreenProducts = taxonomy.merge(CZE,how='left',left_on='HS_ID',right_on='prod')
    # Calculate 2030 export value
    GreenProducts['CountryExport2030'] = GreenProducts['ExportValue'] * (1 + GreenProducts['CAGR_2022_30_FORECAST']) ** 8
    GreenProducts['EUExport2030'] = GreenProducts['EUExport'] * (1 + GreenProducts['CAGR_2022_30_FORECAST']) ** 8

    # Calculate Total Export Value from 2025 to 2030
    # We calculate for each year and sum up
    GreenProducts['CountryExport_25_30'] = sum(GreenProducts['ExportValue'] * (1 + GreenProducts['CAGR_2022_30_FORECAST']) ** i for i in range(3, 9))
    GreenProducts['EUExport_25_30'] = sum(GreenProducts['EUExport'] * (1 + GreenProducts['CAGR_2022_30_FORECAST']) ** i for i in range(3, 9))

    df = GreenProducts.rename(columns={'ExportValue': 'CZ Export 2022 CZK',
                              'pci': 'Komplexita výrobku 2022',
                               'relatedness': 'Příbuznost CZ 2022',
                               'PCI_Rank':'Žebříček komplexity 2022',
                               'PCI_Percentile':'Percentil komplexity 2022',
                               'relatedness_Rank':'Žebříček příbuznosti CZ 2022',
                               'relatedness_Percentile':'Percentil příbuznosti CZ 2022',
                               'WorldExport':'Světový export 2022 CZK',
                               'EUExport':'EU Export 2022 CZK',
                               'EUWorldMarketShare':'EU Světový Podíl 2022 %',
                               'euhhi':'Koncentrace evropského exportu 2022',
                               'hhi':'Koncentrace světového trhu 2022',
                               'CZE_WorldMarketShare':'CZ Světový Podíl 2022 %',
                               'CZE_EUMarketShare':'CZ-EU Podíl 2022 %',
                               'rca':'Výhoda CZ 2022',
                               'EUTopExporter':'EU Největší Exportér 2022',
                               'CZ_Nazev':'Název',
                               'ubiquity':'Počet zemí s výhodou vyšší než 1',
                               'CountryExport2030':'CZ 2030 Export CZK',
                               'EUExport2030':'EU 2030 Export CZK',
                               'CountryExport_25_30':'CZ Celkový Export 25-30 CZK',
                               'EUExport_25_30':'EU Celkový Export 25-30 CZK',
                               'CAGR_2022_30_FORECAST':'CAGR 2022-2030 Předpověď'
                               })
    df                          = df[df.Included == "IN"]
    df['CZ-EU Podíl 2022 %']      = 100 * df['CZ-EU Podíl 2022 %'] 
    df['EU Světový Podíl 2022 %'] = 100 * df['EU Světový Podíl 2022 %'] 
    df['CZ Světový Podíl 2022 %'] = 100 * df['CZ Světový Podíl 2022 %'] 
    df['CZ Export 2022 CZK']        = USD_to_czk*df['CZ Export 2022 CZK'] 
    df['Světový export 2022 CZK']      = USD_to_czk*df['Světový export 2022 CZK'] 
    df['EU Export 2022 CZK']        = USD_to_czk*df['EU Export 2022 CZK'] 
    df['EU Celkový Export 25-30 CZK'] = USD_to_czk*df['EU Celkový Export 25-30 CZK'] 
    df['CZ Celkový Export 25-30 CZK'] = USD_to_czk*df['CZ Celkový Export 25-30 CZK'] 
    df['EU 2030 Export CZK']        = USD_to_czk*df['EU 2030 Export CZK'] 
    df['CZ 2030 Export CZK']        = USD_to_czk*df['CZ 2030 Export CZK'] 
    df['HS_ID']                 = df['HS_ID'].astype(str)
    df['HS_Lookup']              = df['HS_ID']+" - "+df['POPIS']

    return df

df = load_data()

# Create lists of display names for the sidebar
ji_display_names = ['Skupina', 'Podskupina', 'Kategorie výrobku']
plot_display_names = [
    'Příbuznost CZ 2022',
    'Výhoda CZ 2022',
    'Koncentrace světového trhu 2022',
    'Koncentrace evropského exportu 2022',
    'Percentil příbuznosti CZ 2022',
    'Percentil komplexity 2022',
    'Žebříček příbuznosti CZ 2022',
    'Žebříček komplexity 2022',
    'Komplexita výrobku 2022',
    'CZ Export 2022 CZK',
    'Světový export 2022 CZK',
    'EU Export 2022 CZK',
    'EU Světový Podíl 2022 %',
    'CZ Světový Podíl 2022 %',
    'CZ-EU Podíl 2022 %',
    'Počet zemí s výhodou vyšší než 1',
    'density',
    'cog',
    'CZ 2030 Export CZK',
    'CZ Celkový Export 25-30 CZK',
    'EU 2030 Export CZK',
    'EU Celkový Export 25-30 CZK',
    'CAGR 2022-2030 Předpověď'
]

hover_display_data = [
    'HS_ID',
    'Skupina',
    'Podskupina',
    'Název',
    'CZ Celkový Export 25-30 CZK',
    'Příbuznost CZ 2022',
    'Výhoda CZ 2022',
    'Koncentrace světového trhu 2022',
    'Koncentrace evropského exportu 2022',
    'EU Největší Exportér 2022',
    'Komplexita výrobku 2022',
    'CZ Export 2022 CZK',
    'Světový export 2022 CZK',
    'EU Export 2022 CZK',
    'EU Světový Podíl 2022 %',
    'CZ Světový Podíl 2022 %',
    'CZ-EU Podíl 2022 %',
    'CZ 2030 Export CZK',
    'CZ Celkový Export 25-30 CZK',
    'EU 2030 Export CZK',
    'Počet zemí s výhodou vyšší než 1',
    'EU Celkový Export 25-30 CZK',
    'Percentil příbuznosti CZ 2022',
    'Percentil komplexity 2022',
    'Žebříček příbuznosti CZ 2022',
    'Žebříček komplexity 2022',
]

# Sidebar selection boxes using display names
x_axis      = col2.selectbox("Vyber osu X:", plot_display_names, index=4)
y_axis      = col2.selectbox("Vyber osu Y:", plot_display_names, index=5)
markersize  = col2.selectbox("Velikost dle:", plot_display_names, index=9)


# Apply filters to dataframe
filtered_df = df.copy()

filtrovat_dle_skupin = col2.toggle("Filtrovat dle skupin",value=False)

if filtrovat_dle_skupin:
    color       = col2.selectbox("Barva dle:", ji_display_names,index = 1)
    skupiny = df['Skupina'].unique()
    Skupina = col2.multiselect('Skupina',skupiny,default=skupiny[0])
    podskupiny = df['Podskupina'][df['Skupina'].isin(Skupina)].unique()
    Podskupina = col2.multiselect('Podskupina',podskupiny,default=podskupiny)
    filtered_df = filtered_df[filtered_df['Skupina'].isin(Skupina)]
    filtered_df = filtered_df[filtered_df['Podskupina'].isin(Podskupina)]
else:
    color       = 'Skupina'


hover_info  = col2.multiselect("Co se zobrazí při najetí myší:", hover_display_data, default=['Název',x_axis,y_axis])
col2.divider()
# Filter section
if 'filters' not in st.session_state:
    st.session_state.filters = []

subcol1, subcol2, subcol3 = col2.columns(3)
with subcol1:
    if st.button("Filtrování hodnot"):
        st.session_state.filters.append({'column': None, 'range': None})
with subcol2:
    if st.button("Odstranit filtry"):
        st.session_state.filters = []

# Display existing filters using display names
for i, filter in enumerate(st.session_state.filters):
    filter_col= col2.selectbox(f"Filtr {i+1}", plot_display_names, key=f"filter_col_{i}")
    filter_min, filter_max = df[filter_col].min(), df[filter_col].max()
    filter_range = col2.slider(f"Filtr {i+1}", float(filter_min), float(filter_max), (float(filter_min), float(filter_max)), key=f"filter_range_{i}")
    st.session_state.filters[i]['column'] = filter_col
    st.session_state.filters[i]['range'] = filter_range

# Apply numerical filters
for filter in st.session_state.filters:
    if filter['column'] is not None and filter['range'] is not None:
        filtered_df = filtered_df[
            (filtered_df[filter['column']] >= filter['range'][0]) &
            (filtered_df[filter['column']] <= filter['range'][1])
        ]

# Replace negative values in markersize column with zero
filtered_df[markersize] = filtered_df[markersize].clip(lower=0)

# Remove NA values
filtered_df = filtered_df.dropna(subset=[x_axis, y_axis, color, markersize])


HS_select = col1.multiselect("Filtrovat HS6 kódy",filtered_df['HS_Lookup'])

# Initialize the hover_data dictionary with default values of False for x, y, and markersize
hover_data = {}

# Columns without decimals, which should also have thousands separators
no_decimal = [
    'HS_ID',
    'CZ Celkový Export 25-30 CZK',
    'CZ Export 2022 CZK',
    'Světový export 2022 CZK',
    'EU Export 2022 CZK',
    'CZ 2030 Export CZK',
    'CZ Celkový Export 25-30 CZK',
    'EU 2030 Export CZK',
    'EU Celkový Export 25-30 CZK',
    'Žebříček příbuznosti CZ 2022',
    'Žebříček komplexity 2022',
    'ubiquity',
    'Percentil příbuznosti CZ 2022',
    'Percentil komplexity 2022',
]

# Columns requiring three significant figures and percentage formatting
two_sigfig = [
    'Příbuznost CZ 2022',
    'Výhoda CZ 2022',
    'Koncentrace světového trhu 2022',
    'Koncentrace evropského exportu 2022',
    'Komplexita výrobku 2022',
    'CAGR 2022-2030 Předpověď',
]

# Columns that should show as percentages
percentage = [
    'EU Světový Podíl 2022 %',
    'CZ Světový Podíl 2022 %',
    'CZ-EU Podíl 2022 %',
]

texthover = [
    'Skupina',
    'Podskupina',
    'Název',
    'EU Největší Exportér 2022'
]

# Iterate over the columns in hover_info
for col in hover_info:
    # If the column is in no_decimal, format with no decimals and thousands separator
    if col in no_decimal:
        hover_data[col] = ':,.0f'  # No decimals, thousands separator
    # If the column is in three_sigfig, format with 3 decimal places
    elif col in two_sigfig:
        hover_data[col] = ':.2f'
    elif col in percentage:
        hover_data[col] = ':.1f'  # Three decimal places, with percentage symbol
    elif col in texthover:
        hover_data[col] = True
    else:
        hover_data[col] = False  # No formatting needed, just show the column
    
# Ensure x_axis, y_axis, and markersize default to False if not explicitly provided in hover_info
hover_data.setdefault(markersize, False)
hover_data.setdefault(x_axis, False)
hover_data.setdefault(y_axis, False)
hover_data.setdefault('Skupina', False)
hover_data.setdefault('Podskupina', False)
hover_data.setdefault('Název', True)


if HS_select == []:
    fig = px.scatter(filtered_df,
                     x=x_axis,
                     y=y_axis,
                     color=color,
                     color_discrete_map=color_discrete_map,  # Hard-code the colors
                     labels={x_axis: x_axis, y_axis: y_axis},
                     hover_data=hover_data,
                     opacity=0.7,
                     size=markersize,
                     size_max=40)
    

else:
    fig = px.scatter(filtered_df[filtered_df['HS_Lookup'].isin(HS_select)],
                     x=x_axis,
                     y=y_axis,
                     color=color,
                     color_discrete_map=color_discrete_map,  # Hard-code the colors
                     labels={x_axis: x_axis, y_axis: y_axis},
                     hover_data=hover_data,
                     opacity=0.7,
                     size=markersize,
                     size_max=40
                     )
# Update each trace to have the hover background color match the trace's color
for trace in fig.data:
    trace.hoverlabel.bgcolor = trace.marker.color  # Match hover background color with the marker color
fontsize = col1.number_input("Velikost fontu",5,20,12,step=1)
# Update layout with font settings and existing configurations
fig.update_layout(
    font=dict(
        family="Montserrat, sans-serif",  # Specify the font family
        size=fontsize,                          # Font size
        color="black"                     # Font color
    ),
    hoverlabel=dict(
        font=dict(
            family="Montserrat, sans-serif",  # Hover label font family
            color="#FFFFFF"   ,
            size=fontsize                # Hover label font color
        )
    ),
    legend=dict(
        orientation="h",          # Horizontal legend
        yanchor="top",            # Align the legend's top with the graph's bottom
        y=-0.3,                   # Push the legend further below
        xanchor="center",         # Center the legend horizontally
        x=0.5,                  # Position it at the center of the graph
        font=dict(
            family="Montserrat, sans-serif",  # Hover label font family
            color="#000000"   ,
            size=fontsize                # Hover label font color
        )
    ),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        color='black',             # Set axis color to black
        showline=True,             # Show axis line
        linecolor='black',         # Line color
        ticks='outside',           # Show ticks outside the axis line
        tickcolor='black',         # Color of the ticks
        tickwidth=2,               # Width of the ticks
        ticklen=5,                 # Length of the ticks
        tickfont=dict(color='black', size=fontsize),  # Set tick text color to black and size
        title=dict(
            font=dict(color='black', size=fontsize)  # Set x-axis label color and size
        )

    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        color='black',             # Set axis color to black
        showline=True,             # Show axis line
        linecolor='black',         # Line color
        ticks='outside',           # Show ticks outside the axis line
        tickcolor='black',         # Color of the ticks
        tickwidth=2,               # Width of the ticks
        ticklen=5,                 # Length of the ticks
        tickfont=dict(color='black', size=fontsize),  # Set tick text color to black and size
        title=dict(
            font=dict(color='black', size=fontsize)  # Set y-axis label color and size
        )
    ),
    plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent plot background
    paper_bgcolor='rgba(0, 0, 0, 0)'  # Transparent overall background
)



col1.plotly_chart(fig)
mcol1, mcol2, mcol3 = col1.columns(3)
if HS_select == []:
    mcol1.metric("Vybraný český export za rok 2022", "{:,.0f}".format(sum(filtered_df['CZ Export 2022 CZK'])/1000000000),'miliard CZK' )
    mcol2.metric("Vybraný český export 2025 až 2030", "{:,.0f}".format(sum(filtered_df['CZ Celkový Export 25-30 CZK'])/1000000000), "miliard CZK")
    mcol3.metric("Vybraný evropský export 2025 až 2030", "{:,.0f}".format(sum(filtered_df['EU Celkový Export 25-30 CZK'])/1000000000), "miliard CZK")
else:
    mcol1.metric("Vybraný český export za rok 2022", "{:,.0f}".format(sum(filtered_df[filtered_df['HS_Lookup'].isin(HS_select)]['CZ Export 2022 CZK'])/1000000),'milionů CZK' )
    mcol2.metric("Vybraný český export 2025 až 2030", "{:,.0f}".format(sum(filtered_df[filtered_df['HS_Lookup'].isin(HS_select)]['CZ Celkový Export 25-30 CZK'])/1000000), "milionů CZK")
    mcol3.metric("Vybraný evropský export 2025 až 2030", "{:,.0f}".format(sum(filtered_df[filtered_df['HS_Lookup'].isin(HS_select)]['EU Celkový Export 25-30 CZK'])/1000000), "milionů CZK")


mybuff = StringIO()
fig.write_html(mybuff, include_plotlyjs='cdn')
html_bytes = mybuff.getvalue().encode()
subcol3.download_button(
    label = "Stáhnout HTML",
    data = html_bytes,
    file_name = "plot.html",
    mime="text/html"
)


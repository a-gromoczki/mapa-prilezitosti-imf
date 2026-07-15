import streamlit as st
from visualsetup import load_visual_identity

st.set_page_config(
    page_title="Mapa Příležitostí",
    page_icon="favicon.ico",
    layout="wide"
)
load_visual_identity("header.jpg")

st.logo('logo_notext.svg',size='large',icon_image='logo_notext.svg')
st.title("")
st.title("")

# Title
st.title("Analýza Ekonomické Komplexity")

# 1. Import knihoven a definování konstant
st.subheader("1. Import knihoven a definování konstant")
st.write("""
Tato část importuje potřebné knihovny pro analýzu ekonomické komplexity a definuje seznam kódů zemí EU, který bude použit pro filtrování relevantních dat v průběhu analýzy.
""")
with st.expander("Code"):
    st.code("""
from ecomplexity import ecomplexity
from ecomplexity import proximity
import pandas as pd
EU_iso3  = ["AUT","BEL","BGR","HRV","CYP","CZE","DNK","EST","FIN","FRA","DEU","GRC","HUN","IRL","ITA","LVA","LTU","LUX","MLT","NLD","POL","PRT","ROU","SVK","SVN","ESP","SWE"]
    """, language="python")

# 2. Načtení a agregace dat
st.subheader("2. Načtení a agregace dat BACI")
st.write("""
Tento krok načte obchodní dataset BACI pro rok 2022 a agreguje hodnoty exportů podle roku (`t`), země (`i`) a produktu (`k`). Pro snadnější identifikaci jsou pak přidány ISO3 kódy zemí.
""")
with st.expander("Code"):
    st.code("""
BACI_2022 = pd.read_csv('BACI/H22/BACI_HS22_Y2022_V202401b.csv')
BACI_2022_agg = BACI_2022.groupby(['t', 'i', 'k'], as_index=False).agg({'v': 'sum', 'q': 'sum'})
country_codes = pd.read_csv('BACI/H22/country_codes_V202401b.csv')
BACI_2022_agg = BACI_2022_agg.merge(country_codes, left_on='i', right_on='country_code')
data = pd.DataFrame({
    'time': BACI_2022_agg['t'],
    'loc': BACI_2022_agg['country_iso3'],
    'prod': BACI_2022_agg['k'],
    'val': BACI_2022_agg['v'] * 1000  # Převod na dolary
})
    """, language="python")

# 3. Výpočet komplexity a matice blízkosti
st.subheader("3. Výpočet komplexity a matice blízkosti")
st.write("""
S využitím balíčku `ecomplexity` tato sekce vypočítá hodnoty ekonomické komplexity a matici blízkosti pro každý produkt.
""")
with st.expander("Code"):
    st.code("""
trade_cols = {'time': 'time', 'loc': 'loc', 'prod': 'prod', 'val': 'val'}
cdata = ecomplexity(data, trade_cols)
prox_df = proximity(data, trade_cols)
    """, language="python")

# 4. Přidání českých názvů produktů
st.subheader("4. Přidání českých názvů produktů")
st.write("""
Zde se české názvy produktů (HS6 kódy) spojují s anglickými názvy z databáze BACI a doplňují se chybějící hodnoty.
""")
with st.expander("Code"):
    st.code("""
CzechNames = pd.read_csv('database_addons/CZ_HS6_codes.csv')
EnglishNames = pd.read_csv('BACI/H22/product_codes_HS22_V202401b.csv')
EnglishNames['code'] = pd.to_numeric(EnglishNames['code'], errors="coerce")
classed_cdata = cdata.merge(CzechNames[['HS6','POPIS']], left_on='prod', right_on='HS6', how='left').drop('HS6', axis=1)
classed_cdata = classed_cdata.merge(EnglishNames, left_on='prod', right_on='code', how='left').drop('code', axis=1)
classed_cdata['POPIS'].fillna(classed_cdata['description'], inplace=True)
    """, language="python")

# 5. Výpočet hodnot prostoru produktů
st.subheader("5. Výpočet hodnot prostoru produktů")
st.write("""
Tato sekce vypočítá tržní koncentraci (HHI) produktů na globálním a evropském trhu, celkové hodnoty exportů a identifikuje největší evropské exportéry pro každý produkt.
""")
with st.expander("Code"):
    st.code("""
def calculate_hhi(group):
    market_share = group["val"] / group["val"].sum()
    hhi = (market_share ** 2).sum()
    return hhi

def get_product_space(cdata):
    EU_data = cdata[cdata['loc'].isin(EU_iso3)]
    hhi = cdata.groupby("prod").apply(calculate_hhi).reset_index()
    euhhi = EU_data.groupby("prod").apply(calculate_hhi).reset_index()
    hhi.rename(columns={0: 'hhi'}, inplace=True)
    euhhi.rename(columns={0: 'euhhi'}, inplace=True)
    WorldExport = cdata[['prod', 'val']].groupby('prod').agg(sum).reset_index().rename(columns={'val': 'WorldExport'})
    EUExport = EU_data[['prod', 'val']].groupby('prod').agg(sum).reset_index().rename(columns={'val': 'EUExport'})
    EUTopExporter = EU_data.loc[EU_data.groupby('prod')['val'].idxmax(), ['prod', 'loc']].reset_index(drop=True).rename(columns={'loc': 'EUTopExporter'})
    ProductSpace = WorldExport.merge(EUExport, on='prod').merge(EUTopExporter, on='prod').merge(hhi, on='prod').merge(euhhi, on='prod')
    ProductSpace['EUWorldMarketShare'] = ProductSpace['EUExport'] / ProductSpace['WorldExport']
    return ProductSpace
    """, language="python")

# 6. Výpočet příbuznosti
st.subheader("6. Výpočet příbuznosti")
st.write("""
Metrika příbuznosti pomáhá identifikovat produkty, které jsou si podobné na základě obchodních vzorců, s použitím metodologie OEC.
""")
with st.expander("Code"):
    st.code("""
def get_relatedness(country_iso3, year, prox_df, cdata):
    prox_filtered = prox_df[prox_df['time'] == year]
    cdata_filtered = cdata[(cdata['time'] == year) & (cdata['loc'] == country_iso3)]
    merged_df = pd.merge(cdata_filtered, prox_filtered, left_on='prod', right_on='prod_2')
    relatedness_results = merged_df.groupby('prod_1').apply(lambda group: (group['mcp'] * group['proximity']).sum() / group['proximity'].sum())
    return relatedness_results.reset_index().rename(columns={'prod_1': 'prod', 0: 'relatedness'})
    """, language="python")

# 7. Kombinace všech dat pro přehled o zemi
st.subheader("7. Kombinace všech dat pro přehled o zemi")
st.write("""
Tato funkce načítá hodnoty ekonomické komplexity, tržního podílu, příbuznosti a hodnoty prostoru produktů pro specifickou zemi a rok, aby poskytla celkový přehled.
""")
with st.expander("Code"):
    st.code("""
def get_country_data(country_iso3, year, prox_df, cdata):
    output = cdata[(cdata['time'] == year) & (cdata['loc'] == country_iso3)]
    relatedness = get_relatedness(country_iso3, year, prox_df, cdata)
    output = output.merge(relatedness, on='prod')
    ProductSpaceInfo = get_product_space(cdata)
    output = output.merge(ProductSpaceInfo, on='prod').rename(columns={'val': 'ExportValue'})
    output[country_iso3 + '_WorldMarketShare'] = output['ExportValue'] / output['WorldExport']
    
    if country_iso3 in EU_iso3:
        output[country_iso3 + '_EUMarketShare'] = output['ExportValue'] / output['EUExport']
    return output
    """, language="python")

# 8. Výpočet dat pro specifickou zemi
st.subheader("8. Výpočet dat pro specifickou zemi")
st.write("""
V tomto příkladu je funkce `get_country_data` použita pro načtení dat pro Českou republiku (ISO3 kód: 'CZE') za rok 2022. Dále jsou přidány výpočty pro hodnocení tržní konkurence v EU a příbuznost produktů.
""")
with st.expander("Code"):
    st.code("""
CZE = get_country_data('CZE', 2022, prox_df, classed_cdata)
CZE['PCI_Rank'] = CZE['pci'].rank(ascending=True)
CZE['PCI_Percentile'] = CZE['pci'].rank(ascending=True, pct=True) * 100
CZE['relatedness_Rank'] = CZE['relatedness'].rank(ascending=True)
CZE['relatedness_Percentile'] = CZE['relatedness'].rank(ascending=True, pct=True) * 100
    """, language="python")
# 9. Vytvoření přehledu klíčových metrik
st.subheader("9. Vytvoření přehledu klíčových metrik")
st.write("""
Tato část sumarizuje klíčové metriky ekonomické komplexity a tržní koncentrace. Hodnoty exportů, tržních podílů a příbuznosti produktů lze graficky vizualizovat pomocí `Streamlit`, což poskytne uživatelům přehled o ekonomické pozici zvolené země.
""")
with st.expander("Code"):
    st.code("""
st.write("Celkový export za rok 2022 pro ČR: ", Country_Data['ExportValue'].sum())
st.write("Průměrná příbuznost produktů pro ČR: ", Country_Data['relatedness'].mean())
st.write("Průměrný podíl ČR na světovém trhu pro exportované produkty: ", Country_Data['CZE_WorldMarketShare'].mean())
    """, language="python")

# 10. Vytvoření grafů a vizualizace
st.subheader("10. Vytvoření grafů a vizualizace")
st.write("""
Vizualizace umožňuje analyzovat rozložení hodnot exportů a identifikovat klíčové produkty s největším exportem, příbuzností nebo podílem na trhu. K tomu slouží například grafy rozdělení nebo bublinové grafy.
""")
with st.expander("Code"):
    st.code("""
import matplotlib.pyplot as plt

def plot_top_exports(data, n=10):
    top_exports = data.sort_values(by="ExportValue", ascending=False).head(n)
    fig, ax = plt.subplots()
    ax.barh(top_exports['POPIS'], top_exports['ExportValue'], color='skyblue')
    ax.set_xlabel("Hodnota exportu (USD)")
    ax.set_title("Top {} exportované produkty ČR v roce 2022".format(n))
    st.pyplot(fig)

plot_top_exports(Country_Data)
    """, language="python")

# 11. Filtrace a interaktivní analýza
st.subheader("11. Filtrace a interaktivní analýza")
st.write("""
Aplikace může obsahovat interaktivní filtry, které uživatelům umožňují dynamicky měnit zobrazené informace, např. podle hodnot exportu, příbuznosti produktů nebo podílů na trhu. Filtry mohou být implementovány přímo ve Streamlit prostředí, např. použitím `st.slider` nebo `st.selectbox`.
""")
with st.expander("Code"):
    st.code("""
min_export = st.slider("Minimální hodnota exportu", min_value=0, max_value=int(Country_Data['ExportValue'].max()), step=1000000)
filtered_data = Country_Data[Country_Data['ExportValue'] >= min_export]
st.write("Počet produktů s hodnotou exportu nad zvolenou hodnotu:", filtered_data.shape[0])
    """, language="python")

# 12. Závěrečná doporučení pro exportní strategii
st.subheader("12. Závěrečná doporučení pro exportní strategii")
st.write("""
Na základě analýzy dat lze identifikovat potenciální exportní příležitosti a strategická doporučení. Tato část může být automatizována tak, aby se doporučovaly produkty s vysokou příbuzností a nízkým tržním podílem, což ukazuje na potenciální příležitosti pro růst exportu.
""")
with st.expander("Code"):
    st.code("""
def recommend_products(data, threshold_relatedness=0.5, threshold_market_share=0.01):
    recommended = data[(data['relatedness'] > threshold_relatedness) & (data['CZE_WorldMarketShare'] < threshold_market_share)]
    st.write("Doporučené produkty k expanzi na základě příbuznosti a nízkého podílu na trhu:")
    st.write(recommended[['POPIS', 'relatedness', 'CZE_WorldMarketShare']])

recommend_products(Country_Data)
    """, language="python")

# 13. Export výsledků
st.subheader("13. Export výsledků")
st.write("""
Konečné výsledky lze exportovat do CSV nebo jiného formátu, aby byly dostupné i mimo aplikaci. Tento krok umožňuje uživatelům analyzovat a sdílet výsledky mimo rozhraní Streamlit.
""")
with st.expander("Code"):
    st.code("""
Country_Data.to_csv("CZE_Economic_Complexity_2022.csv", index=False)
st.write("Data byla exportována jako CSV soubor.")
    """, language="python")

# Závěr
st.subheader("Závěr")
st.write("""
Tento postup poskytuje ucelenou metodu pro analýzu ekonomické komplexity a exportní strategie. Díky přehledu klíčových ukazatelů a interaktivním nástrojům může aplikace pomoci identifikovat nové exportní příležitosti a podpořit růst konkurenceschopnosti na světových trzích.
""")
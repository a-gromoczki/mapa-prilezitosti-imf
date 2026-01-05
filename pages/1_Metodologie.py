import streamlit as st
from mapatools.visualsetup import load_visual_identity
import os
# Page config
st.set_page_config(
    page_title="Mapa Příležitostí",
    page_icon="resources/favicon.ico",
    layout="wide"
)
# Load custom branding
load_visual_identity("resources/header.jpg")
st.logo('resources/logo_notext.svg', size='large', icon_image='resources/logo_notext.svg')

col1,col2,col3 = st.columns([1,5,1])
col2.subheader("")
col2.subheader("")

# Main Section Title
# --- Introduction and Data Sources ---
col2.markdown("""
## Odkud jsme čerpali data ohledně velikosti vývozu v jednotlivých výrobkových kategoriích
Celá datová základna je založena na harmonizovaném datasetu světového obchodu **BACI**, který je každoročně publikován organizací **CEPII**. CEPII harmonizuje data z databáze **UN Comtrade** tak, aby každý export z jedné země odpovídal importu v zemi druhé a nedocházelo k dvojímu započítání obchodních toků.  
Databáze **UN Comtrade** je oficiální globální databáze OSN, která obsahuje detailní statistiky o mezinárodním obchodu se zbožím mezi státy.
""")

col2.link_button("Více o BACI datasetu", "https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37")

col2.divider()
# --- Product Classification ---
col2.markdown("""
## Klasifikace výrobků
Pro účely Mapy příležitostí využíváme klasifikaci **Harmonized System (HS)** ve verzi **HS 2022**.  
Analýza je prováděna na úrovni **šesticiferného členění výrobků (HS6)**, kde je celkem 5 606 typů výrobků.  
Data jsou k dispozici za rok **2022 a 2023**.
""")

# --- Green Products ---
col2.markdown("""
### Jak jsme vybírali tzv. „zelené výrobky“
Za „zelené“ či „clean-tech“ označujeme produkty klíčové pro přechod na čistou, nízkouhlíkovou ekonomiku.
              A to včetně produktů, které jsou důležité v přechodové fázi transformace. Mezi „zelené“ či „clean-tech“ tak nezahrnujeme pouze výrobky, které samy přímo přispívají ke snižování emisí nebo mají nízkoemisní provoz. Označujeme tak i takové produkty a komponenty, do nichž bude v souvislosti se zelenou transformací nutné investovat, a u nichž se v souvislosti s tlakem na přechod na šetrné technologie a s adaptací na složitější klima očekává významný růst globální poptávky.

Do kategorie zelených výrobků jsme nezahrnuli produkty, u nichž se očekává sice změna materiálu či výrobního postupu ve prospěch vyšší energetické či výrobní šetrnosti, avšak bez dopadu na celkový objem trhu.
Výběr vychází z:
- rešerší globálních akademických studií,
- materiálů veřejného sektoru,
- konzultací s experty z ČR.

Zahrnujeme i komponenty důležité pro zelenou transformaci.
              
Jsme si vědomi, že zelená transformace povede také k růstu poptávky po nových typech služeb, například v oblasti digitálních či energetických řešení. Mapa příležitostí však aktuálně pracuje pouze s daty o vývozu výrobků, protože využívaný datový zdroj služby nepokrývá. Z důvodu zachování jednotné metodiky jsme analýzu služeb nezahrnovali.
""")

col2.markdown("""
### Využívání termínu „zelená“ vs. „clean-tech“
Termíny **zelené výrobky**, **clean-tech** a **čisté technologie** používáme rovnocenně.  
Zahrnujeme široké spektrum změn – od energetiky přes průmyslové technologie až po hospodaření s vodou, půdou a surovinami.
""")
col2.divider()

# --- Cleantech Taxonomy Tree Placeholder ---
col2.markdown("## Třídění zelených výrobků")
col2.markdown("""
Zelené výrobky třídíme do **6 Taxonomických grup**, **17 Skupin**, **40 Podskupin** a **58 Kategorií**.  
Některé kategorie zatím nejsou obsazené, ale počítáme s jejich doplněním.
""")

col2.graphviz_chart("""
digraph G {
    rankdir=LR;
    bgcolor=transparent;
    splines=ortho;

    node [
        shape=box,
        style=filled,
        fillcolor=white,
        fontname="Arial, sans-serif",
        fontcolor="#002651",
        color="#666666",
        style=bold,
        fontsize=14,
        fontstyle=bold,
        fixedsize=true,
        width=4,
        height=0.3,
        margin=0.2,
        labelloc=c,
        justify=center
    ];

    edge [arrowhead=none];

    // Top-level categories
    "Snížení emisní náročnosti";
    "Snižení materiálové náročnosti";
    "Ochrana životního prostředí";
    "Adaptace na složitější klima";
    "Měřící a diagnostické přístroje";
    "Materiály a komponenty";

    // Subcategories
    "Snížení emisní náročnosti" -> "Výroba, nízkoemisní výrobní postupy";
    "Snížení emisní náročnosti" -> "Doprava";
    "Snížení emisní náročnosti" -> "Budovy";
    "Snížení emisní náročnosti" -> "Výroba nízkoemisní elektřiny a paliv";
    "Snížení emisní náročnosti" -> "Ukládání energie";
    "Snížení emisní náročnosti" -> "Energetické sítě";
    "Snížení emisní náročnosti" -> "Zadržování uhlíku";
    "Snížení emisní náročnosti" -> "Zachytávání a ukládání uhlíku";

    "Snižení materiálové náročnosti" -> "Materiálová efektivita, šetrné materiály";
    "Snižení materiálové náročnosti" -> "Cirkularita";
    "Snižení materiálové náročnosti" -> "Zacházení s odpady";

    "Ochrana životního prostředí" -> "Voda a ovzduší";
    "Ochrana životního prostředí" -> "Půda";
    "Ochrana životního prostředí" -> "Biodiverzita";

    "Adaptace na složitější klima" -> "Adaptace na dlouhodobé změny a živelné pohromy";

    "Měřící a diagnostické přístroje" -> "Měřící a diagnostické přístroje; Monitoring";

    "Materiály a komponenty" -> "Výroba surovin, komponent a zařízení pro nízkouhlíkové technologie";
}
""")
col2.divider()

# --- Key Indicators ---
col2.markdown("## Na jaké ukazatele se zaměřujeme")
col2.markdown("""
**Příbuznost**  
Produkty „příbuzné“ těm, které ČR už exportuje. Metrika je založená na metodologii OEC.

**Komplexita**  
Vyjadřuje unikátnost výrobku – čím vyšší, tím méně zemí jej umí vyvézt. Počítáno pomocí modulu **py-ecomplexity** (Harvard CID).
              
U obou těchto ukazatelů jsme zároveň spočítali percentilové rozložení jednotlivých výrobků podle Komplexity a Příbuznosti mezi nulu a stovku a ukazujeme je tak na osách, kde jsou údaje za Příbuznost a Komplexitu normalizovány na osu 0-100.
""")
kurzcol1, kurzcol2,kurzcol3 = col2.columns(3)
kurzcol1.markdown("""
**Exportní objem**  
Měříme v USD. Pro CZK převod:  """)

kurzcol2.metric("Kurz v roce 2022",23.36)
kurzcol3.metric("Kurz v roce 2023",22.21)
col2.markdown(
"""
**Růst**  
Výpočet růstu vývozu za 2022–23 v USD (neočištěno o inflaci).

**Podíl a pořadí na světovém trhu**  
V procentech a absolutní hodnotě vývozu ČR ve srovnání se světem.

**Koncentrace světového trhu**  
Vypočítaná jako Herfindahl–Hirschmanův index (HHI):
""",
unsafe_allow_html=True,
)
hhicol1,hhicol2 = col2.columns(2)
hhicol1.latex(r"\text{HHI} = \sum_{i=1}^N s_i^2")
hhicol2.markdown(
"""
 - $s_i$ je tržní podíl země $i$ v procentech.
 - HHI = 1 znamená, že produkt vyváží pouze jedna země.
""",
unsafe_allow_html=True,)
col2.markdown(
"""
**Koncentrace evropského exportu**  
Opět HHI index, ale tentokrát přepočítaný pouze s Evropským exportem.
"""
)
col2.divider()
# --- Detailed Data Methodology Section ---
col2.markdown("## Datová metodologie")

col2.markdown("""
### Výpočet komplexity produktu
Používáme Python modul **py-ecomplexity** od **Centre for International Development (Harvard)**.
""")
col2.link_button("Více o modulu py-ecomplexity", "https://github.com/cid-harvard/py-ecomplexity")

# --- RCA Condition ---
col2.markdown("""
### Podmínka aktivity v dané zemi
Používáme kritérium **RCA > 1** jako důkaz komparativní výhody, podobně jako v **OEC**.
""")
col2.link_button("Metodika OEC", "https://oec.world/en/resources/methods")


# --- Relatedness Formula ---
col2.markdown("### Výpočet příbuznosti produktů")

latexcol1,latexcol2 = col2.columns(2)

latexcol1.latex(r"""
\text{příbuznost}_{cp} = \frac{\sum_{p'} M_{cp'} \, \phi_{pp'}}{\sum_{p'} \phi_{pp'}}
""")

latexcol2.markdown("""
- **$$M_{cp'}$$**: 1 pokud má produkt $$p'$$ v zemi $$c$$ RCA > 1, jinak 0.  
- **$$\phi_{pp'}$$**: Míra příbuznosti mezi produkty.  

""", unsafe_allow_html=True)
col2.markdown("""
Výpočet je **normalizovaný** a ukazuje příbuznost produktu $$p$$ k aktivním produktům v zemi $$c$$.

Hlavním úskalím metodik ekonomické komplexity je, že absolutní hodnoty příbuznosti a komplexity nenesou nutně žádný význam. Jejich síla totiž spočívá v porovnávání komplexity mezi jednotlivými produkty a příbuznosti mezi zeměmi.
""", unsafe_allow_html=True)
col2.link_button("Doporučujeme přečíst tento kritický článek", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7335174/")

col2.divider()
col2.markdown(
    """

## Data-sharing

Kategorizovaná data, vytvořená na základě vlastní metodologie Mapy příležitostí Česka a příslušný open-source kód, jsou k dispozici výhradně pro nekomerční využití za podmínky správného citování a uvedení zdroje 'Mapa příležitostí Česka' . V případě zájmu o kategorizovaná data využijte kontaktní formulář na webu [Mapa příležitostí Česka](https://mapaprilezitosticeska.cz/) 
"""
)
col2.link_button("Open-source kód na GitHub", "https://github.com/omaxim/MapaPrilezitosti")


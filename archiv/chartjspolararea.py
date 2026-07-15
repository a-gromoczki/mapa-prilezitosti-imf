import json
import itertools
from MapaPrilezitosti.mapatools.variable_names import get_color_discrete_map

def chart_chartjs_variable_pie(filtered_df_2022, filtered_df_2023, total_export_22, total_export_23,
                                green_total_22, green_total_23, group_field,
                                chart_title="Export růst mezi lety 2022 a 2023",
                                bottom_text="Data: UN COMTRADE, CEPII, a další"):

    green_total_22_filtered = filtered_df_2022['CZ Export 2022 CZK'].sum()
    green_total_23_filtered = filtered_df_2023['CZ Export 2023 CZK'].sum()

    non_green_22 = total_export_22 - green_total_22
    non_green_23 = total_export_23 - green_total_23

    other_green_22 = green_total_22 - green_total_22_filtered
    other_green_23 = green_total_23 - green_total_23_filtered

    def safe_growth(a, b):
        return (b - a) / a * 100 if a > 0 else 0

    labels = []
    data_2023 = []
    export22 = []
    export23 = []
    growthAbs = []
    growthPct = []
    backgroundColor = []

    color_map = get_color_discrete_map()
    fallback_colors = ["#E63946", "#F4A261", "#2A9D8F", "#264653", "#8A5AAB", "#D67D3E", "#1D3557"]
    fallback_cycle = itertools.cycle(fallback_colors)

    # Non-green
    labels.append("Nezelené produkty")
    export22.append(non_green_22 / 1e9)
    export23.append(non_green_23 / 1e9)
    data_2023.append(non_green_23 / 1e9)
    growthAbs.append((non_green_23 - non_green_22) / 1e9)
    growthPct.append(safe_growth(non_green_22, non_green_23))
    backgroundColor.append("#CCCCCC")

    # Other green
    if other_green_22 > 0:
        labels.append("Ostatní zelené produkty")
        export22.append(other_green_22 / 1e9)
        export23.append(other_green_23 / 1e9)
        data_2023.append(other_green_23 / 1e9)
        growthAbs.append((other_green_23 - other_green_22) / 1e9)
        growthPct.append(safe_growth(other_green_22, other_green_23))
        backgroundColor.append("#B2BEB5")

    green_cats = sorted(list(set(filtered_df_2022[group_field].unique()).union(
                              set(filtered_df_2023[group_field].unique()))))

    for cat in green_cats:
        exp22 = filtered_df_2022[filtered_df_2022[group_field] == cat]['CZ Export 2022 CZK'].sum()
        exp23 = filtered_df_2023[filtered_df_2023[group_field] == cat]['CZ Export 2023 CZK'].sum()

        labels.append(cat)
        export22.append(exp22 / 1e9)
        export23.append(exp23 / 1e9)
        data_2023.append(exp23 / 1e9)
        growthAbs.append((exp23 - exp22) / 1e9)
        growthPct.append(safe_growth(exp22, exp23))
        backgroundColor.append(color_map.get(cat, next(fallback_cycle)))

    # Calculate radius offsets based on 2023 export size
    max_radius_offset = 40
    max_value = max(data_2023)
    radiusOffset = [(val / max_value) * max_radius_offset for val in data_2023]

    chart_data = {
        "labels": labels,
        "datasets": [{
            "data": data_2023,
            "backgroundColor": backgroundColor,
            "export22": export22,
            "export23": export23,
            "growthAbs": growthAbs,
            "growthPct": growthPct,
            "radiusOffset": radiusOffset
        }]
    }

    chart_config = {
        "type": "doughnut",
        "data": chart_data,
        "options": {
            "responsive": True,
            "cutout": "30%",
            "layout": {
                "padding": {
                    "top": 50,
                    "bottom": 50,
                    "left": 50,
                    "right": 50
                }
            },
            "plugins": {
                "tooltip": {
                    "callbacks": {
                        "label": {
                            "function": """function(context) {
                                const i = context.dataIndex;
                                const d = context.dataset;
                                const l = context.label || '';
                                return [
                                    `${l}`,
                                    `2022: ${d.export22[i].toFixed(1)} miliard CZK`,
                                    `2023: ${d.export23[i].toFixed(1)} miliard CZK`,
                                    `Růst: ${d.growthAbs[i].toFixed(1)} miliard CZK (${d.growthPct[i].toFixed(1)}%)`
                                ];
                            }"""
                        }
                    }
                },
                "title": {
                    "display": True,
                    "text": chart_title
                }
            }
        },
        "plugins": ["ChartDataLabels", "variableRadius"]
    }

    html = f'''
    <div style="width: 100%; max-width: 800px; margin: auto; padding: 40px;">
    <canvas id="exportGrowthChart" style="max-height: 600px;"></canvas>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels"></script>
    <script>
      const variableRadius = {{
        id: "variableRadius",
        beforeDraw(chart) {{
          const dataset = chart.data.datasets[0];
          const meta = chart.getDatasetMeta(0);
          meta.data.forEach((arc, i) => {{
            const offset = dataset.radiusOffset?.[i] || 0;
            arc.outerRadius = arc.outerRadius + offset;
          }});
        }}
      }};
      Chart.register(variableRadius);

      const ctx = document.getElementById('exportGrowthChart').getContext('2d');
      const chartConfig = {json.dumps(chart_config)};
      chartConfig.options.plugins.tooltip.callbacks.label = eval('(' + chartConfig.options.plugins.tooltip.callbacks.label.function + ')');
      new Chart(ctx, chartConfig);
    </script>
    <div style="text-align:center; font-size: 0.8em; color: #666">{bottom_text}</div>
    '''

    return html

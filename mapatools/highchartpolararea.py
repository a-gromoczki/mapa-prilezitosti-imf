import json


def chart_highcharts_variable_pie(
    filtered_df_2022,
    filtered_df_2023,
    total_export_22,
    total_export_23,
    green_total_22,
    green_total_23,
    group_field,
    usd_to_eur_22=0.95,
    usd_to_eur_23=0.93,
    chart_title="Rast exportu medzi rokmi 2022 a 2023",
    bottom_text="Data: UN COMTRADE, CEPII, a ďalšie",
    relative_to_green_only=False,
    year_22="2022",
    year_23="2023",
):
    """
    Creates a Highcharts variable pie chart showing green export growth.
    Includes both filtered green categories and (optionally) non-green and unclassified green.

    If `relative_to_green_only` is True or total_export_22/23 are None, then
    slice angles (y) are calculated as share of green exports only.
    """

    # Base green export totals from filtered subset and convert to USD
    total_export_22 = total_export_22 / usd_to_eur_22
    total_export_23 = total_export_23 / usd_to_eur_23
    green_total_22 = green_total_22 / usd_to_eur_22
    green_total_23 = green_total_23 / usd_to_eur_23
    green_total_22_filtered = (
        filtered_df_2022[f"Slovenský export {year_22} EUR"].sum() / usd_to_eur_22
    )
    green_total_23_filtered = (
        filtered_df_2023[f"Slovenský export {year_23} EUR"].sum() / usd_to_eur_23
    )

    # Compute unfiltered other-green portion
    other_green_22 = green_total_22 - green_total_22_filtered
    other_green_23 = green_total_23 - green_total_23_filtered
    growth_other_green = (other_green_23 - other_green_22) / other_green_22 if other_green_22 > 0 else 0

    # Decide what denominator to use for slice angles (y)
    use_green_only = relative_to_green_only or total_export_22 is None or total_export_23 is None
    denominator = green_total_23 if use_green_only else total_export_23

    data_series = []

    # Add non-green slice if using total exports as denominator
    if not use_green_only:
        non_green_22 = total_export_22 - green_total_22
        non_green_23 = total_export_23 - green_total_23
        growth_non_green = (non_green_23 - non_green_22) / non_green_22 if non_green_22 > 0 else 0

        data_series.append({
            "name": "Nezelené produkty",
            "y": non_green_23 / denominator,
            "z": growth_non_green,
            "color": "#CCCCCC",
            "export22": non_green_22 / 1e9,
            "export23": non_green_23 / 1e9,
            "growth_abs": (non_green_23 - non_green_22) / 1e9,
            "growth_frac": 100 * growth_non_green
        })

    # Add other-green slice if it exists
    if other_green_22 > 0 or other_green_23 > 0: 
        data_series.append({
            "name": "Ostatné zelené produkty",
            "y": other_green_23 / denominator,
            "z": growth_other_green,
            "color": "#B2BEB5",
            "export22": other_green_22 / 1e9,
            "export23": other_green_23 / 1e9,
            "growth_abs": (other_green_23 - other_green_22) / 1e9,
            "growth_frac": 100 * growth_other_green
        })

    # Add each filtered green category
    green_cats = sorted(
        set(filtered_df_2022[group_field]) | set(filtered_df_2023[group_field])
    )

    for cat in green_cats:
        export_22 = (
            filtered_df_2022.loc[
                filtered_df_2022[group_field] == cat,
                f"Slovenský export {year_22} EUR",
            ].sum()
            / usd_to_eur_22
        )
        export_23 = (
            filtered_df_2023.loc[
                filtered_df_2023[group_field] == cat,
                f"Slovenský export {year_23} EUR",
            ].sum()
            / usd_to_eur_23
        )
        growth = (export_23 - export_22) / export_22 if export_22 > 0 else 0

        # Get color from either dataset (prefer 2023, fallback to 2022)
        color_2023 = filtered_df_2023.loc[filtered_df_2023[group_field] == cat, "Barva " + group_field]
        color_2022 = filtered_df_2022.loc[filtered_df_2022[group_field] == cat, "Barva " + group_field]
        color = color_2023.iloc[0] if not color_2023.empty else (color_2022.iloc[0] if not color_2022.empty else "#000000")

        data_series.append(
            {
                "name": cat,
                "y": export_23 / denominator,
                "z": growth,
                "color": color,
                "export22": export_22 / 1e9,
                "export23": export_23 / 1e9,
                "growth_abs": (export_23 - export_22) / 1e9,
                "growth_frac": 100 * growth,
            }
        )
    sorted_data_series = sorted(
        data_series, key=lambda item: float(item["z"]), reverse=True
    )


    # Highcharts config
    chart_config = {
        "chart": {
            "type": "variablepie",
            "height": "700px"
        },
        "credits": {
            "enabled": False
        },
        "title": {
            "text": chart_title,
            "style": {
                "fontSize": "25px",
                "fontFamily": "Arial, sans-serif",
                "color": "#002651"
            }
        },
        "subtitle": {
            "text": bottom_text,
            "align": "center",
            "style": {
                "fontSize": "14px",
                "fontFamily": "Arial, sans-serif",
                "color": "#002651"
            }
        },
        "tooltip": {
            "headerFormat": "",
            "pointFormat": (
                '<span style="color:{point.color}">\u25CF</span> <b>{point.name}</b><br/>'
                f"Export {year_22}: {{point.export22:,.1f}} miliárd USD<br/>"
                f"Export {year_23}: {{point.export23:,.1f}} miliárd USD<br/>"
                "Rast: {point.growth_abs:,.1f} miliárd USD ({point.growth_frac:.2f}%)"
            ),
            "style": {
                "fontFamily": "Arial, sans-serif",
                "color": "#002651",
            },
        },
        "legend": {
            "itemStyle": {
                "fontFamily": "Arial, sans-serif",
                "color": "#002651"
            }
        },
        "series": [{
            "minPointSize": 10,
            "innerSize": "35%",
            "slicedOffset": 20,
            "zMax": 1,
            "zMin": 0,
            "name": "Export",
            "crisp": "false",
            "data": sorted_data_series
        }]
    }

    config_json = json.dumps(chart_config)

    chart_html = f"""
    <div id="container" style="width: 100%; height: 700px;"></div>
    <script src="https://cdn.jsdelivr.net/npm/highcharts@11/highcharts.js"></script>
    <script>
      var chartConfig = {config_json};
      function initVariablePieChart() {{
        Highcharts.chart('container', chartConfig);
      }}
    </script>
    <script src="https://cdn.jsdelivr.net/npm/highcharts@11/modules/variable-pie.js" onload="initVariablePieChart()"></script>
    """

    return chart_html

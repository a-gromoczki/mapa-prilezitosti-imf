import pandas as pd
import json
import itertools
import numpy as np
from mapatools.variable_names import get_hover_formatting

def chartjs_plot(filtered_df, markersize, hover_data, color, x_axis, y_axis, year,chart_title="Chart Title",bottom_text="Bottom Text"):
    # Define the consistent color palette
    color_palette = [
        "#1CC08F",  # green/teal
        "#33D3E9",  # cyan
        "#205CF7",  # blue
        "#A379FD",  # purple
        "#ED4FDD",  # pink/magenta
        "#FF976A",  # orange
        "#FEC04C"   # yellow
    ]
    
    # Create a consistent color mapping for categories
    unique_categories = sorted(filtered_df[color].unique())
    color_map = {}
    for idx, category in enumerate(unique_categories):
        color_map[category] = color_palette[idx % len(color_palette)]
    
    # Min-Max scaling for markersize (normalize to range like 2-32)
    min_size = filtered_df[markersize].min()
    max_size = filtered_df[markersize].max()


    # Avoid division by zero in case all values are the same
    if max_size == min_size:
        filtered_df["scaled_size"] = 10  # Assign a medium default size
    else:
        # Apply log scaling: map input range to output range [2, 32]
        # Use np.log to apply log scaling
        log_min = np.sqrt(min_size + 1)  # Adding 1 to avoid 10(0) if min_size is 0
        log_max = np.sqrt(max_size + 1)

        # Scale the size based on the log of the values
        filtered_df["scaled_size"] = ((np.sqrt(filtered_df[markersize] + 1) - log_min) / (log_max - log_min)) * 30 + 2

    # --- Assume get_hover_formatting returns dictionaries like before ---
    no_decimal, two_sigfig, percentage, texthover = get_hover_formatting(year)

    # --- Assume format_hover_data function is defined as before ---

    def format_hover_data(key, value):

        if key in no_decimal:
            return "{:,.0f}".format(value) # No decimals, thousands separator
        elif key in two_sigfig:
            return "{:.2f}".format(value) # 2 decimal places
        elif key in percentage:
            return "{:.1f}%".format(value) # Convert to percentage
        elif key in texthover:
            return str(value)
        else:
            return value # No special formatting
    
    grouped_data = {}
    for _, row in filtered_df.iterrows():
        color_category = row[color]
        # Use the consistent color mapping instead of the dataframe color
        assigned_color = color_map.get(color_category, color_palette[0])

        # Create the basic data point structure
        data_point = {
             "x": row[x_axis],
             "y": row[y_axis],
             "r": row["scaled_size"],
             "meta": {} # Initialize meta dictionary here
        }
        # Populate meta dictionary - *** MODIFIED LOGIC ***
        for key in hover_data:
             # Check if the key should be included (value is not False)
            if hover_data.get(key) is not False:
                # Format the value using your existing function
                value = format_hover_data(key, row[key])
                 # Store the value directly, preserving any <br> tags. NO MORE SPLITTING.
                data_point["meta"][key] = str(value) # Ensure it's a string
        # Sort meta dictionary alphabetically (optional, but good for consistency below title)
        # We will handle Názov separately in JS, sorting affects the rest
        data_point["meta"] = dict(sorted(data_point["meta"].items()))
        # Add the complete data point to the correct group
        if color_category not in grouped_data:
            grouped_data[color_category] = {"data": [], "color": assigned_color, "_originalBackgroundColor": assigned_color} # Add original color store here too if not already done
        grouped_data[color_category]["data"].append(data_point)

    # --- Create datasets with default transparency ---
    default_alpha_hex = 'CC' # Set desired default alpha (~80% opaque)

    datasets = [
        {
            "label": category,
            "data": group_info["data"],
            "backgroundColor": group_info["color"] + default_alpha_hex, # Default appearance
            "borderColor": group_info["color"] + default_alpha_hex, # Default appearance
            "_originalBackgroundColor": group_info["_originalBackgroundColor"], # OPAQUE color
            # *** ADD DEFAULT TRANSPARENT COLOR FOR RESETTING ***
            "_defaultBackgroundColor": group_info["color"] + default_alpha_hex,
            "borderWidth": 1,
            "hoverRadius": 5, # May be overridden by JS element options
            # "clip": 100
        }for category, group_info in grouped_data.items()]

    # Convert datasets to JSON
    # Use a custom encoder if you have non-standard types (like lambdas, though they won't serialize)


    datasets_json = json.dumps(datasets)
    x_label = json.dumps(x_axis)
    y_label = json.dumps(y_axis)

    # Generate the JavaScript chart code
    chart_js = f"""
    <div style="width:100%; height:700px; position: relative; margin: 0; padding: 0; box-sizing: border-box;">
        <canvas id="myBubbleChart" style="width: 100% !important; height: 100% !important; display: block;"></canvas>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        var ctx = document.getElementById('myBubbleChart').getContext('2d');
        var datasets = {datasets_json}; // Load datasets from Python

        // --- Optional: Add original color back if needed post-JSON parsing ---
        // Not strictly necessary if we use the _originalBackgroundColor added above
        Chart.defaults.font.family = 'Montserrat, sans-serif';
        var myBubbleChart = new Chart(ctx, {{
            type: 'bubble',
            data: {{
                datasets: datasets // Use the datasets variable
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                resizeDelay: 0,
                layout: {{
                    padding: 0
                }},
                scales: {{
                    x: {{ title: {{ display: true, text: {x_label} }} }},
                    y: {{ title: {{ display: true, text: {y_label} }} }}
                }},
                animation: {{ duration: 500 }}, // Disable default animations if hover is jerky
                transitions: {{
                    active: {{ animation: {{ duration: 500 }} }} // Faster response on hover
                }},

                onHover: (event, elements, chart) => {{
                // 1. Reset ALL datasets to the DEFAULT transparent state first
                chart.data.datasets.forEach(dataset => {{
                    // Use the stored default color with transparency
                    const defaultColor = dataset._defaultBackgroundColor || dataset.backgroundColor; // Fallback
                    dataset.backgroundColor = defaultColor;
                    dataset.borderColor = defaultColor; // Assuming border matches fill
                }});

                // 2. If hovering over an element, apply specific styles
                if (elements.length > 0) {{
                    const hoveredDatasetIndex = elements[0].datasetIndex;

                    chart.data.datasets.forEach((dataset, index) => {{
                        if (index === hoveredDatasetIndex) {{
                            // Make the HOVERED dataset OPAQUE
                            dataset.backgroundColor = dataset._originalBackgroundColor;
                            dataset.borderColor = dataset._originalBackgroundColor;
                        }} else {{
                            // Make INACTIVE datasets HIGHLY transparent ('0D' alpha)
                            // Add '0D' to the OPAQUE original color
                            dataset.backgroundColor = dataset._originalBackgroundColor + '0D';
                            dataset.borderColor = dataset._originalBackgroundColor + '0D';
                        }}
                    }});
                }}
                // 3. Update the chart (No 'else' needed, step 1 handles reset)
                chart.update(); // Use 'none' for smoother updates without animation flicker
            }},

                plugins: {{
                    title: {{
                        display: true,
                        text: {json.dumps(chart_title)},
                        font: {{
                        size: 25
                        }}
                    }},
                    subtitle: {{
                        display: true,
                        text: {json.dumps(bottom_text)},
                        position: 'bottom',
                        padding: {{
                            top: 10
                        }},
                        font: {{
                            size: 14
                        }}
                    }},
                    legend: {{
                        // --- Your existing legend onClick logic ---
                        onClick: (event, item, legend) => {{
                            const datasetIndex = item.datasetIndex;
                            const chart = legend.chart;
                            if (chart._isolatedDatasetIndex === undefined) {{
                                chart._isolatedDatasetIndex = null;
                            }}
                            if (chart._isolatedDatasetIndex === datasetIndex) {{
                                chart.data.datasets.forEach((ds, index) => {{
                                    chart.setDatasetVisibility(index, true);
                                     // Restore original colors when un-isolating
                                    if(ds._defaultBackgroundColor) {{
                                        ds.backgroundColor = ds._defaultBackgroundColor;
                                        ds.borderColor = ds._defaultBackgroundColor;
                                    }}
                                }});
                                chart._isolatedDatasetIndex = null;
                            }} else {{
                                chart.data.datasets.forEach((ds, index) => {{
                                    chart.setDatasetVisibility(index, index === datasetIndex);
                                     // Restore original colors before hiding/showing
                                     if(ds._defaultBackgroundColor) {{
                                        ds.backgroundColor = ds._defaultBackgroundColor;
                                        ds.borderColor = ds._defaultBackgroundColor;
                                    }}
                                }});
                                chart._isolatedDatasetIndex = datasetIndex;
                            }}
                            chart.update();
                        }},
                        labels: {{ usePointStyle: true, padding: 10 }}
                    }},
                    tooltip: {{
                        // Use callbacks for custom tooltip content
                        callbacks: {{
                            // ** Use the 'title' callback for 'Názov' **
                            // It's typically bold by default.
                            title: function(tooltipItems) {{
                                // tooltipItems is an array, we usually use the first item
                                if (!tooltipItems.length) {{
                                    return '';
                                }}
                                const context = tooltipItems[0];
                                const data = context.dataset.data[context.dataIndex];

                                // Check if 'Názov' exists in our meta data
                                if (data.meta && data.meta.hasOwnProperty('Názov')) {{
                                    // Split the 'Názov' string by '<br>' to create multiple lines
                                    // Chart.js handles an array return as multiple title lines
                                    return data.meta['Názov'].split('<br>');
                                }}
                                return ''; // Return empty string if no 'Názov'
                            }},

                            // ** Optional: Add space after title if Názov existed **
                            afterTitle: function(tooltipItems) {{
                                const context = tooltipItems[0];
                                const data = context.dataset.data[context.dataIndex];
                                // Add space only if Názov was shown and there are other items
                                if (data.meta && data.meta.hasOwnProperty('Názov') && Object.keys(data.meta).length > 1) {{
                                     // Return an empty string or one with just space to force a line
                                    return ' '; // Creates visual separation
                                }}
                                return '';
                            }},


                            // ** Use 'beforeBody' to generate the Key: Value lines for other items **
                            // Returns an array of strings, each becoming a line in the tooltip body.
                            beforeBody: function(tooltipItems) {{
                                const context = tooltipItems[0];
                                const data = context.dataset.data[context.dataIndex];
                                const bodyLines = []; // Array to hold our custom body lines

                                if (data.meta) {{
                                    // Iterate through the keys (already sorted in Python)
                                    for (const key in data.meta) {{
                                        // Make sure the key is not 'Názov' (already handled in title)
                                        if (key !== 'Názov' && data.meta.hasOwnProperty(key)) {{
                                            // Format as "Key: Value"
                                            bodyLines.push(`${{key}}: ${{data.meta[key]}}`);
                                        }}
                                    }}
                                }}
                                return bodyLines; // Return the array of lines
                            }},

                            // ** Disable the default label **
                            // Since we are generating the body content in beforeBody,
                            // we don't need the default label (which usually shows dataset label & y-value).
                            label: function(context) {{
                                return null; // Returning null prevents the default label line
                            }},

                            // ** Optional: Hide the color swatch next to the label **
                            // Since we disabled the default label, you might not want the color box either.
                            labelColor: function(context) {{
                                return null; // Returning null hides the color box
                                // Alternative: return {{ borderColor: 'transparent', backgroundColor: 'transparent' }};
                            }}

                        }} // end callbacks
                    }} // end tooltip
                }}
            }}
        }});

        // Optional: Add logic to reset hover state if mouse leaves canvas
        ctx.canvas.addEventListener('mouseout', () => {{
             myBubbleChart.data.datasets.forEach(dataset => {{
                const originalColor = dataset._defaultBackgroundColor || dataset.backgroundColor;
                 dataset.backgroundColor = originalColor;
                 dataset.borderColor = originalColor;
            }});
            myBubbleChart.update('none');
        }});

    </script>
    """
    return chart_js

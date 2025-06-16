from shiny import App, ui, render, reactive           # Import PyShiny components
from htmltools import HTML                            # For injecting raw HTML into the UI
from shiny.ui import modal_show, modal, modal_button
from htmltools import tags
import json                                           # To load and inject the GeoJSON
import pandas as pd
import matplotlib.pyplot as plt                       # For the graphic

# Load raw GeoJSON
with open("UCD_DeltaT.geojson", encoding="utf-8") as f:
    original_geojson = json.load(f)

# Load ΔT values for each country and season
delta_df = pd.read_csv("UCD_DeltaT.csv")
available_countries = sorted(delta_df["UC_NM_MN"].dropna().unique())

# Dropdown variables
variable_labels = {
    "DeltaT_Winter_Day_mean": "Winter (Day)",
    "DeltaT_Winter_Night_mean": "Winter (Night)",
    "DeltaT_Spring_Day_mean": "Spring (Day)",
    "DeltaT_Spring_Night_mean": "Spring (Night)",
    "DeltaT_Summer_Day_mean": "Summer (Day)",
    "DeltaT_Summer_Night_mean": "Summer (Night)",
    "DeltaT_Fall_Day_mean": "Fall (Day)",
    "DeltaT_Fall_Night_mean": "Fall (Night)",
}

# Coloring function
def get_color(value):
    if value is None:
        return "#cccccc"
    elif value > 9:
        return "#b35806"
    elif value > 6:
        return "#e08214"
    elif value > 3:
        return "#fdb863"
    elif value > 0:
        return "#fee0b6"
    elif value == 0:
        return "#f7f7f7"
    elif value > -3:
        return "#d8daeb"
    elif value > -6:
        return "#b2abd2"
    elif value > -9:
        return "#8073ac"
    else:
        return "#542788"

# UI layout
app_ui = ui.page_navbar(
    ui.nav_spacer(),
    ui.nav_panel(
        "🗺️ Urban Heatmap",
        ui.card(
            ui.card_header(
                ui.input_select("selected_variable", "Choose certain season to show the map:", variable_labels, selected="DeltaT_Summer_Night_mean"),
                class_="d-flex align-items-center gap-3"
            ),
            ui.output_ui("mymap"),
            ui.card_footer(
                ui.markdown("📖 Reference Study: https://doi.org/10.1088/1748-9326/ac0661 | 📧 Contact: [Susanne A Benz](mailto:susanne.benz@kit.edu), [Rania A Desenaldo](mailto:raniadesenaldo@gmail.com)")
            ),
            full_screen=True,
        ),
    ),
    ui.nav_panel(
        "📊 ΔT Scatter Plot",
        ui.card(
            ui.card_header("Average ΔT: Day vs Night by Season"),
            ui.input_select("country", "Select a country/urban area:", available_countries, selected="Karlsruhe [DEU]"),
            ui.output_plot("scatterchart"),
            ),
    ),
    fillable="Urban Heatmap",
    id="navbar",
    title="🌍 Urban Heatmap Application",
    window_title="Urban Heatmap App"
)

# Text in the Beginning
def info_modal():
    modal_show(
        modal(
            tags.strong(tags.h3("🌍 Urban Heatmap Application")),
            tags.p(
                "Exploring the Difference of Surface Temperature Anomalies (ΔT) in Every Country!"
            ),
            tags.hr(),
            tags.strong(tags.h4("📖 About The Application")),
            tags.p(
                """
            This application provides information about the variety of Surface
            Temperature Anomalies (ΔT) for every season (winter, spring, summer,
            fall) seen in day and night for every country around the world.
            """,
            style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),
            tags.p(
                """
            The first tab (🗺️ Urban Heatmap) will provide you with the heatmap and the heat value when
            you click the polygon for each country.
            """,
            style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),
            tags.p(
                """
            The second tab (📊 ΔT Scatter Plot) will provide you the graphic for seasonal and diurnal
            variations for every country based on its annual mean temperature
            anomalies from each season in night (x-value) and day (y-value) conditions.
            """,  
            style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),
            tags.hr(),
            tags.strong(tags.h4("📖 Reference Study")),
            tags.p(
            """
            Susanne A Benz et al 2021 Environ. Res. Lett. 16 064093
            """,
            style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),
            tags.a(
                "https://doi.org/10.1088/1748-9326/ac0661",
                href=("https://doi.org/10.1088/1748-9326/ac0661"
            ),
            style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ), 
            tags.hr(),
            tags.strong(tags.h4("📧 Contact")),
            tags.a(
                "Susanne A Benz", href=("mailto:susanne.benz@kit.edu"),
            style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),
            tags.p(
            """
            """,
            style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),
            tags.a(
                "Rania A Desenaldo", href=("mailto:raniadesenaldo@gmail.com"),
            style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),            
            size="l",
            easy_close=True,
            footer=modal_button("Close"),
        )
    )

# SERVER
def server(input, output, session):

    info_modal()

    @reactive.Effect
    @reactive.event(input.info_icon)
    def _():
        info_modal()

    @reactive.calc
    def geojson_colored():
        geojson = json.loads(json.dumps(original_geojson))
        selected_var = input.selected_variable()

        values = [
            f["properties"].get(selected_var, 0)
            for f in geojson["features"]
            if f["properties"].get(selected_var) is not None
        ]

        if not values:
            min_val, max_val = 0, 1
        else:
            min_val, max_val = min(values), max(values)

        for feature in geojson["features"]:
            val = feature["properties"].get(selected_var, 0)
            color = get_color(val if val is not None else 0)
            feature["properties"]["color"] = color

        return json.dumps(geojson)

    @output
    @render.ui
    def mymap():
        # Return HTML and JavaScript as raw HTML to the frontend
        return HTML(f"""
        <!-- Load Leaflet CSS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                         
        <!-- Custom styles for legend -->
        <style>
        .legend {{
            background: white;
            padding: 10px;
            line-height: 18px;
            color: #555;
            font-family: sans-serif;
            border-radius: 5px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }}
        .legend i {{
            display: inline-block;
            width: 18px;
            height: 18px;
            float: left;
            margin-right: 8px;
            opacity: 0.8;
        }}
        </style>            

        <!-- Info box style -->
        <style>
          .info-box {{
            position: absolute;
            top: 60px;
            right: 20px;
            background: white;
            padding: 10px;
            border-radius: 6px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            z-index: 1000;
            font-family: sans-serif;
          }}
        </style>

        <!-- Map container (required for Leaflet) -->
        <div id="map" style="height: 600px; position: relative;"></div>
            
        <!-- Info panel overlay -->
        <div class="info-box">
          <b>Please click on the polygons to see the ΔT value!</b><br>
        </div>                    

        <!-- Load Leaflet JS -->
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        
        <!-- JavaScript for initializing the map -->
        <script>
            setTimeout(function() {{
                // Create the Leaflet map and center it
                var map = L.map('map').setView([49.3, 8.45], 9);

                // Add OpenStreetMap tile layer
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '&copy; OpenStreetMap contributors'
                }}).addTo(map);

                // Use the Python-injected GeoJSON
                var geojson = {geojson_colored()};

                // POPUP
                function myClick(feature, layer) {{
                    layer.on('click', function(e) {{
                        var props = feature.properties;
                        var val = props["{input.selected_variable()}"];
                        var formattedVal = (val !== null && val !== undefined) ? val.toFixed(3) : "N/A";
                        var popup = "<b>Region:</b> " + props.UC_NM_MN + "<br>" +
                            "<b>ΔT Value:</b> " + formattedVal + "°C";
                        layer.bindPopup(popup).openPopup();
                    }});
                }}

                L.geoJSON(geojson, {{
                    onEachFeature: myClick,
                    style: function(feature) {{
                        return {{
                            color: feature.properties.color,
                            weight: 2,
                            fillOpacity: 0.7
                        }};
                    }}
                }}).addTo(map);

        // Add legend
        var legend = L.control({{ position: "bottomleft" }});
        legend.onAdd = function(map) {{
            var div = L.DomUtil.create("div", "info legend");
            var grades = ["> 9", "> 6", "> 3", "> 0", "= 0", "< 0", "< -3", "< -6", "< -9"];
            var colors = [
                "#b35806", "#e08214", "#fdb863", "#fee0b6",
                "#f7f7f7", "#d8daeb", "#b2abd2", "#8073ac", "#542788"
            ];

            div.innerHTML = "<b>Temp. Anomalies (°C)</b><br>";
            for (var i = 0; i < grades.length; i++) {{
                div.innerHTML +=
                    '<i style="background:' + colors[i] + ';"></i> ' +
                    grades[i] + '<br>';
            }}
            return div;
        }};
        legend.addTo(map);    
            
            }}, 100);

        </script>
        """)

    @reactive.calc
    def selected_country_data():
        selected_country = input.country()
        country_data = delta_df[delta_df["UC_NM_MN"] == selected_country]
        return country_data

    @output
    @render.plot
    def scatterchart():
        df = selected_country_data()
        seasons = ["Winter", "Spring", "Summer", "Fall"]
        day_cols = [f"DeltaT_{s}_Day_mean" for s in seasons]
        night_cols = [f"DeltaT_{s}_Night_mean" for s in seasons]

        day_values = df[day_cols].values.flatten()
        night_values = df[night_cols].values.flatten()

        fig, ax = plt.subplots()
        ax.scatter(day_values, night_values, color="darkorange", s=80)

        for i, season in enumerate(seasons):
            ax.text(day_values[i] + 0.1, night_values[i], season, fontsize=10)

        ax.set_xlabel("ΔT (Day) °C")
        ax.set_ylabel("ΔT (Night) °C")
        ax.set_title(f"ΔT: Day vs Night ({input.country()})")
        ax.grid(True)
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.7)
        ax.axvline(0, color="gray", linestyle="--", linewidth=0.7)
        return fig

# Start the app
app = App(app_ui, server)
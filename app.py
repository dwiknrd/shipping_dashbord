# 1. Import Dash
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px

paxel_palette = ['#ffc107', '#fd7e14', '#dc3545', '#e83e8c', '#6f42c1']
import json

## --- DAHSBOARD ELEMENTS ---

### DATASET
with open('data_cache/Indonesia_provinces.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)

shipping = pd.read_pickle('data_input/shipping_clean')
gpp=pd.read_csv('power_plant.csv')

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
    ],
    brand="Dashboard Pengiriman COD",
    brand_href="#",
    color='#5f4fa0',
    dark=True,
    sticky='top',
)

##### CARDS

# Menghitung Total Pesanan
total_pesanan = shipping['order_id'].count()

# Menghitung Completed rate
completed_rate = (shipping[shipping['status'] == 'Completed']['order_id'].count() / total_pesanan) * 100

# Menghitung Rata-rata Waktu Pengiriman
delivery_time = shipping['day_to_arv'].mean()

card_pesanan = [
    dbc.CardHeader('Total Pengiriman'),
    dbc.CardBody(
        [
            html.H1(f"{total_pesanan:,.0f}", style={'color': '#5f4fa0'})
        ]
    )
]

card_completed_rate = [
    dbc.CardHeader('Pengiriman Selesai'),
    dbc.CardBody(
        [
            html.H1(f"{completed_rate:.2f}%", style={'color': '#5f4fa0'})
        ]
    )
]

card_delivery_time = [
    dbc.CardHeader('Rata-rata Waktu Pengiriman'),
    dbc.CardBody(
        [
            html.H1(f"{delivery_time:.0f} hari", style={'color': '#5f4fa0'})
        ]
    )
]


##### GRAPH

########## Analisis Geografis: Choroplet

province_data = shipping.pivot_table(
    index='province',
    values='order_id',
    aggfunc='count'
).reset_index()

choroplet = px.choropleth(province_data,
                   geojson=geojson_data,
                   locations='province',
                   color='order_id',
                   color_continuous_scale=paxel_palette,
                   featureidkey='properties.NAME_1',
                   title='Peta Pengiriman Paket Ke Seluruh Provinsi di Indonesia',
                   hover_name='province',
                   template='plotly_white',
                   projection='equirectangular',
                   labels={'order_id': 'Jumlah Pesanan',
                           'province': 'Provinsi'}
                   )

choroplet = choroplet.update_geos(fitbounds='locations', visible=False)
choroplet = choroplet.update_layout(title={'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'color': '#5e50a1', 'size': 24}})



########## Donut Chart

# data aggregation
ship_mode = shipping.pivot_table(
    index = 'ship_mode',
    values = 'order_id',
    aggfunc = 'count'
).reset_index()


# data visualization
donut = px.pie(
        ship_mode,
        values='order_id',
        names='ship_mode',
        color_discrete_sequence=['#6f42c1', '#e83e8c', '#ffc107'],
        template='plotly_white',
        hole=0.4,
        labels={
            'primary_fuel': 'Type of Fuel'
        }
    )

# 2. Create a Dash app instance
app = dash.Dash(
    name='Dashboard - Pengiriman COD',
    external_stylesheets=[dbc.themes.PULSE]
)
app.title = 'Dashboard - Pengiriman COD'

## --- DASHBOARD LAYOUT

app.layout = html.Div(children=[
    navbar,
    html.Br(),
    # Main page
    html.Div(
        [
            # ----- ROW 1
            dbc.Row(
                [
                    # --- COLUMN 1
                    dbc.Col(
                        [
                        dbc.Card(
                            card_pesanan, color='f8f9fa',
                        
                        ),
                        html.Br(),
                        dbc.Card(
                            card_completed_rate, color='f8f9fa', 
                        ),
                        html.Br(),
                        dbc.Card(
                            card_delivery_time, color='f8f9fa', 
                        ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [dcc.Graph(
                            id='map',
                            figure=choroplet,
                            style={
                                    # 'width': '800px',            # Mengatur lebar grafik
                                    # 'height': '600px',           # Mengatur tinggi grafik
                                    # 'margin': '10px',            # Mengatur margin
                                    'padding': '10px',           # Mengatur padding
                                    'border': '1px solid gray',  # Mengatur bingkai dengan garis hitam tebal 1px
                                    'background-color': '#f0f0f0',  # Mengatur warna latar belakang
                                }

                        )],
                        width=9,
                    ),
                ]
            ),

            html.Hr(),

            # ----- ROW 2
            dbc.Row([
                html.H1(
                    'Analisis Mode Pengiriman',
                    style={
                            'color': '#5e50a1',      # Warna teks
                            'font-size': '24px',     # Ukuran font
                            'font-family': 'Arial',  # Jenis font
                            'font-weight': 'bold',   # Ketebalan font
                            'text-align': 'center',  # Tata letak teks
                            'text-decoration': 'underline',  # Dekorasi teks
                            'line-height': '1.5',   # Jarak antara baris
                            'letter-spacing': '2px', # Jarak antar huruf
                            'text-transform': 'uppercase'  # Gaya teks

                    }
                ),

                html.Br(),


                ## ------------ Column 1
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Pilih Mode Pengiriman'),
                        dbc.CardBody(dcc.Dropdown(
                            id='list_ship_mode',
                            options=shipping['ship_mode'].unique(),
                            value='STANDARD',
                        )),
                    ]),
                    html.Br(),
                    dcc.Graph(
                        id='donut',
                        figure=donut,
                        style={
                            'width': '400px',
                            'height': '400px'}),
                ],
                width=3),

                ## ------------ Column 2
                dbc.Col([
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                dcc.Graph(
                                    id='lineplot',
                                ),
                                label='Pergerakan Harian'
                            ),
                            dbc.Tab(
                                dcc.Graph(
                                    id='heatmap',
                                ),
                                label='Jumlah Pengiriman Harian'
                            ),
                        ]
                    ),


                ],
                width=9),
            ]
            ),
            html.Br(),
            html.Hr(),
            html.Br(),

            # ----- ROW 3
            dbc.Row(
                [
                html.H1(
                    'Analisis Wilayah',
                    style={
                            'color': '#5e50a1',      # Warna teks
                            'font-size': '24px',     # Ukuran font
                            'font-family': 'Arial',  # Jenis font
                            'font-weight': 'bold',   # Ketebalan font
                            'text-align': 'center',  # Tata letak teks
                            'text-decoration': 'underline',  # Dekorasi teks
                            'line-height': '1.5',   # Jarak antara baris
                            'letter-spacing': '2px', # Jarak antar huruf
                            'text-transform': 'uppercase'  # Gaya teks

                    }
                ), html.Br(),

                ## ------------ Column 1
                dbc.Col(
                    dcc.Graph(id='bar_count')
                ),


                ## ------------ Column 2
                dbc.Col(
                    dcc.Graph(id='bar_sum')
                ),




                ]
            ),




        ],
        style={
            'padding-right':'30px',
            'padding-left':'30px'
        }
    )
    

],
style={
    'backgroundColor':'#fff',
    },
)

# ---- CALLBACK TO 

@app.callback(
    [
        Output('lineplot', 'figure'),
        Output('heatmap', 'figure'),
        Output('bar_count', 'figure'),
        Output('bar_sum', 'figure'),
        Input('list_ship_mode', 'value'),
    ]
)

def update_plots(shipping_mode):
    mode = shipping[shipping['ship_mode'] == shipping_mode]

    ### ---- Visualisasi Line Plot
    # Data aggregation
    line_agg = mode.pivot_table(
        index='creation_date',
        values='order_id',
        aggfunc='count'
    ).reset_index()

    fig_line = px.line(line_agg,
        x='creation_date',
        y='order_id',
        labels={
            'order_id': 'Jumlah Pengiriman',
            'creation_date': 'Tanggal'
        },
        template='plotly_white',
        color_discrete_sequence=['#6f42c1']
    )
    # Mengubah skala visualisasi
    fig_line = fig_line.update_yaxes(range=[0, 110], dtick=10)

    ### ---- Visualisasi Heatmap
    data_agg1 = mode.pivot_table(
    values='day_to_arv',
    index='order_day',
    columns='order_hour',
    aggfunc='count',
    )


    fig_heatmap = px.imshow(
        data_agg1,
        color_continuous_scale=paxel_palette,
        template='plotly_white',
    )
    fig_heatmap = fig_heatmap.update_xaxes(title_text='Hour', dtick=1)
    fig_heatmap = fig_heatmap.update_yaxes(title_text='')


    ### ---- Visualisasi Jumlah Pesanan
    # data aggregation
    region_agg = mode.pivot_table(
        index = 'origin_region',
        aggfunc = 'count',
        values = 'order_id'
    ).sort_values('order_id').reset_index()

    # data visualization
    fig_pesanan = px.bar(region_agg,
        x = 'order_id',
        y = 'origin_region',
        template='plotly_white',
        title = 'Jumlah Pesanan Pengiriman Disetiap Wilayah',
        labels={
            'origin_region' : 'Wilayah',
            'value': 'Jumlah Pesanan',
            'order_id':'Jumlah Pesanan'
        },
        color='order_id',
        color_continuous_scale=paxel_palette)


    ### ---- Visualisasi Jumlah Pendapatan
    # data aggregation
    region_agg2 = mode.pivot_table(
        index = 'origin_region',
        aggfunc = 'sum',
        values = 'delivery_fee'
    ).sort_values('delivery_fee').reset_index()

    # data visualization
    fig_pendapatan = px.bar(region_agg2,
        x = 'delivery_fee',
        y = 'origin_region',
        template='plotly_white',
        title = 'Total Pendapatan Disetiap Wilayah',
        labels={
            'origin_region' : 'Wilayah',
            'delivery_fee': 'Total Pendapatan',
        },
        color='delivery_fee',
        color_continuous_scale=paxel_palette)


    return fig_line, fig_heatmap, fig_pesanan, fig_pendapatan




# 3. Start the Dash server
if __name__ == "__main__":
    app.run_server()
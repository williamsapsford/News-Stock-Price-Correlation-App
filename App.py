import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
from nytimesarticle import articleAPI
from datetime import datetime
from dateutil.relativedelta import *
import json
from dash.dependencies import Output, Input, State


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H2("Stock and News comparison App"),
        html.Img(src="/assets/Stocks-icon.png")
    ], className='banner'),

    html.Label("Enter a stock Ticker Symbol and News Keyword: "),
    html.Div(dcc.Input(id='stock-input', value='', type='text', placeholder='Ticker Symbol...')),
    html.Br(),
    html.Div(dcc.Input(id='news-input', value='', type='text', placeholder='News Keyword...')),
    html.Br(),
    html.Div(html.Button('Create', id='submit-entry', n_clicks=0)),


    html.Div(id='output-graph')
])





app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


@app.callback(
    Output(component_id='output-graph', component_property='children'),


    [Input('submit-entry', 'n_clicks')],
    [State('stock-input', 'value'), State('news-input', 'value')]
)


def update_graph(n_clicks, input_stock, input_news):
    TOKEN = 'Tpk_3f380b854a4642f785ef5afe44beb6a9'
    TICKER = input_stock
    TIMEFRAME = '1m'

    if n_clicks>0:
        URL = 'https://sandbox.iexapis.com/stable/stock/{}/chart/{}?token={}'.format(TICKER, TIMEFRAME, TOKEN)

        req = requests.get(URL)
        json_price_data = json.loads(req.content)

        # creating a list of prices and dates
        price_dates = []
        price_values = []
        for i in json_price_data:
            price_dates.append(i['date'])
            price_values.append(i['close'])
        END = datetime.today().strftime('%Y%m%d')  # YYYYMMDD format

        # getting the start date
        START = str(datetime.today() - relativedelta(months=1))

        # searching for keyword
        api = articleAPI('uAN64MV0oUktaYdZFi7ILbiEWyAS0W0g')

        KEYWORD = input_news

        URL = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q={}&begin_date={}&fq=business&fq=financial&end_date={}&api-key=uAN64MV0oUktaYdZFi7ILbiEWyAS0W0g'.format(
            KEYWORD, START, END)

        r = requests.get(URL)
        json_news_data = r.json()

        # creating a list of all headlines, artice links, and dates
        news_data = []
        for i in range(len(json_news_data['response']['docs'])):
            news_data.append(
                [json_news_data['response']['docs'][i]['headline']['main'],
                 json_news_data['response']['docs'][i]['web_url'],
                 json_news_data['response']['docs'][i]['pub_date'][0:10]])

        news_data.sort(key=lambda x: x[2])

        news_data = [x for x in news_data if x[2] >= price_dates[0] and x[2] <= price_dates[-1]]
        shapes = []
        for i in news_data:
            shapes.append(dict(x0=i[2], x1=i[2], y0=0, y1=1, xref='x', yref='paper'))

        annotations = []
        number = 0.09
        for i in range(len(news_data)):
            annotations.append(dict(x=news_data[i][2], y=number, xref='x', yref='paper', showarrow=False, bgcolor="#FAA500",
                                    xanchor='left', text=news_data[i][0]))
            number += 0.1

        return html.Div(dcc.Graph(
            id='Stock Graph',
            figure={
                'data': [
                    {'x': price_dates, 'y': price_values, 'type': 'line', 'name': TICKER.upper()},
                ],
                'layout': {
                    'title': TICKER.upper() + ' price variation and ' + input_news.upper() + ' headlines over the last month',
                    'shapes': shapes,
                    'annotations': annotations,
                    'autosize': False,
                    'width': 1800,
                    'height': 800
                }
            }
        ))


if __name__ == "__main__":
    app.run_server(debug=True)
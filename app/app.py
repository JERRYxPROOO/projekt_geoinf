from flask import Flask, render_template, request
from modules.queries import get_daily_avg_with_stats, get_available_cities, get_pollutants
import plotly.graph_objs as go
import plotly
import json

app = Flask(__name__)


@app.route('/')
def index():
    pollutants = get_pollutants()
    cities = get_available_cities()
    return render_template('index.html', pollutants=pollutants, cities=cities)


@app.route('/plot', methods=['POST'])
def plot():
    pollutant = request.form['pollutant']
    selected_cities = request.form.getlist('cities')

    pollutants = get_pollutants()
    cities = get_available_cities()

    stats_table = []
    traces = []

    for city in selected_cities:
        df = get_daily_avg_with_stats(city, pollutant)
        if df.empty:
            continue

        traces.append(go.Scatter(
            x=df['date'],
            y=df['mean'],
            mode='lines+markers',
            name=city
        ))

        stats_table.append({
            'city': city,
            'min': round(df['min'].min(), 1),
            'max': round(df['max'].max(), 1),
            'mean': round(df['mean'].mean(), 1),
            'count': len(df)
        })

    layout = go.Layout(title='Średnie dobowe stężeń',
                       xaxis=dict(title='Data'),
                       yaxis=dict(title=f'{pollutant} (µg/m³)'))

    fig = go.Figure(data=traces, layout=layout)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html',
                           plot=graphJSON,
                           pollutants=pollutants,
                           cities=cities,
                           selected_pollutant=pollutant,
                           selected_cities=selected_cities,
                           stats_table=stats_table)


if __name__ == '__main__':
    app.run(debug=True)

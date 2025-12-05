import sqlite3
import pandas as pd


def get_connection():
    return sqlite3.connect('app/db/air.db')


def get_pollutants():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT pollutant FROM measurements ORDER BY pollutant")
        return [row[0] for row in cur.fetchall()]


def get_available_cities():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT city FROM measurements ORDER BY city")
        return [row[0] for row in cur.fetchall()]


def get_daily_avg_with_stats(city, pollutant):
    with get_connection() as conn:
        query = """
            SELECT date(timestamp) as date,
                   MIN(value) as min,
                   MAX(value) as max,
                   AVG(value) as mean
            FROM measurements
            WHERE city = ? AND pollutant = ?
            GROUP BY date
            ORDER BY date
        """
        df = pd.read_sql_query(query, conn, params=(city, pollutant))
        return df

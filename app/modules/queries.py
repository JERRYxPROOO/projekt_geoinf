import sqlite3
import os
from modules.station_names import station_to_city, CITY_DEFS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "air.db")

def query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_available_pollutants():
    return query("SELECT DISTINCT pollutant FROM measurements ORDER BY pollutant;")


def get_available_cities():
    rows = query("SELECT DISTINCT station_code FROM measurements;")
    cities = set()

    for st, in rows:
        cities.add(station_to_city(st))

    return sorted(list(cities))


def get_daily_city_avg(city, pollutant):
    station_patterns = CITY_DEFS[city]
    like_filters = " OR ".join([f"station_code LIKE ?" for _ in station_patterns])
    params = [f"%{k}%" for k in station_patterns] + [pollutant]

    sql = f"""
        SELECT date, AVG(value)
        FROM measurements
        WHERE ({like_filters})
        AND pollutant=?
        GROUP BY date
        ORDER BY date;
    """

    return query(sql, params)


def get_multi_city_daily_avg(cities, pollutant):
    result = []

    for city in cities:
        rows = get_daily_city_avg(city, pollutant)
        for date, avg in rows:
            result.append((city, date, avg))

    return result


def get_city_stats(city, pollutant):
    station_patterns = CITY_DEFS[city]
    like_filters = " OR ".join([f"station_code LIKE ?" for _ in station_patterns])
    params = [f"%{k}%" for k in station_patterns] + [pollutant]

    sql = f"""
        SELECT MIN(value), MAX(value), AVG(value), COUNT(DISTINCT date)
        FROM measurements
        WHERE ({like_filters})
        AND pollutant=?;
    """

    row = query(sql, params)[0]
    return {
        "city": city,
        "min": row[0],
        "max": row[1],
        "avg": row[2],
        "days": row[3]
    }

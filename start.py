import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time


def scrape_load_data(date):
    url = f"https://www.delhisldc.org/Loaddata.aspx?mode={date.strftime('%d/%m/%Y')}"
    print(f"Requesting URL: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return {}

    print(f"Response status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'ContentPlaceHolder3_DGGridAv'})

    if table is None:
        print("Table not found. Printing page content for debugging:")
        print(soup.prettify())
        return {}

    data = {}
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 7:
            time = cols[0].text.strip()
            if time in ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00',
                        '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
                        '20:00', '21:00', '22:00', '23:00']:
                try:
                    load = sum(float(col.text.strip()) for col in cols[1:7])
                    data[time] = load
                except ValueError as e:
                    print(f"Error parsing data for time {time}: {e}")

    return data


def get_weather_data(date):
    # This is a placeholder. Replace with actual API call.
    return {'temperature': 25, 'humidity': 60}


def main():
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)

    all_data = {
        'TIMESLOT': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                     '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00',
                     '22:00', '23:00']
    }

    current_date = start_date
    while current_date <= end_date:
        print(f"Processing date: {current_date}")

        # Scrape load data
        load_data = scrape_load_data(current_date)

        if not load_data:
            print(f"No data found for {current_date}. Skipping...")
            current_date += timedelta(days=1)
            continue

        # Get weather data
        weather = get_weather_data(current_date)

        # Add data to all_data dictionary
        date_str = current_date.strftime('%d/%m/%Y')
        all_data[f"{date_str}(load)"] = [load_data.get(time, '') for time in all_data['TIMESLOT']]
        all_data[f"{date_str}(temperature)"] = [weather['temperature']] * 24
        all_data[f"{date_str}(humidity)"] = [weather['humidity']] * 24

        current_date += timedelta(days=1)
        time.sleep(1)  # Add a delay to avoid overwhelming the server

    # Create DataFrame and save to Excel
    df = pd.DataFrame(all_data)
    df.to_excel('load_and_weather_data.xlsx', index=False)
    print("Data saved to load_and_weather_data.xlsx")


if __name__ == "__main__":
    main()
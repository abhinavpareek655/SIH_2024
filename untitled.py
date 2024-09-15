import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import holidays


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

weather_dataframe = pd.read_csv('3800613.csv')
def get_weather_data(date):
    year = date.strftime('%y')
    month = date.strftime('%m')
    day = date.strftime('%d')
    date_str = '20'+year+'-'+month+'-'+day
    print(date_str)
    temp_df = weather_dataframe[weather_dataframe['DATE']==date_str][['PRCP','TAVG']]
    return {'t': temp_df.iloc[0]['TAVG'],'p':temp_df.iloc[0]['PRCP']}


India_holidays_list = set()
for p,s in holidays.India(years = [2021,2022,2023,2024]).items():
    India_holidays_list.add(p)
def is_holiday(date):
    # Return 1 for holidays, 0 for non-holidays.
    # A holiday is either a sunday or one of the dates in the India_holidays_list
    if date.weekday() == 6 or date.date() in India_holidays_list :
        return 1
    return 0
    


def is_public_event(date):
    # Placeholder logic for public events. Return 1 for public events, 0 for none.
    # Replace this with actual logic if required.
    return 1 if date == datetime(2024, 12, 21).date() else 0  # Example: Event on Dec 21, 2024


def get_real_estate_growth(date):
    # Placeholder for real estate growth rate. Replace with dynamic data if available.
    return 2.5  # Example static growth rate


def main():
    #End date is kept as 8 September 2024 because we only have data till that date only
    end_date = datetime(2024,9,8)
    start_date = end_date - timedelta(days=1)

    

    all_data = {
        'Date': [],
        'Time': [],
        'Temperature (°C)': [],
        'Precipitation (%)': [],
        'Holiday (0/1)': [],
        'Day of the Week (1-7)': [],
        'Load Demand (MW)': [],
        'Real Estate Development (Growth Rate %)': [],
        'Public Event (0/1)': []
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

        # Get additional data
        holiday = is_holiday(current_date)
        public_event = is_public_event(current_date)
        real_estate_growth = get_real_estate_growth(current_date)
        day_of_week = current_date.weekday() + 1  # Convert to 1-7 (Monday=1, Sunday=7)

        # Add data for each time slot
        for time_slot, load in load_data.items():
            all_data['Date'].append(current_date.strftime('%d/%m/%Y'))
            all_data['Time'].append(time_slot)
            all_data['Temperature (°C)'].append(weather['t'])
            all_data['Precipitation (%)'].append(weather['p'])
            all_data['Holiday (0/1)'].append(holiday)
            all_data['Day of the Week (1-7)'].append(day_of_week)
            all_data['Load Demand (MW)'].append(load)
            all_data['Real Estate Development (Growth Rate %)'].append(real_estate_growth)
            all_data['Public Event (0/1)'].append(public_event)

        current_date += timedelta(days=1)
        time.sleep(1)  # Add a delay to avoid overwhelming the server

    # Create DataFrame and save to Excel
    df = pd.DataFrame(all_data)
    df.to_excel('load_and_weather_data.xlsx', index=False)
    print("Data saved to load_and_weather_data.xlsx")


if __name__ == "__main__":
    main()
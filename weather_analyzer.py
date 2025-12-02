import argparse
import requests
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Configuration
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OUTPUT_DIR = "/app/output"

# Отримуємо ключі з налаштувань (змінні середовища)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_coordinates(city_name: str):
    try:
        params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
        response = requests.get(GEOCODING_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            print(f"Error: City '{city_name}' not found.")
            sys.exit(1)
            
        location = data["results"][0]
        return location["latitude"], location["longitude"], location["name"], location.get("timezone", "UTC")
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        sys.exit(1)

def fetch_weather_data(lat, lon, timezone):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "precipitation"],
        "timezone": timezone
    }
    
    try:
        response = requests.get(ARCHIVE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        sys.exit(1)

def analyze_data(json_data):
    hourly = json_data.get("hourly", {})
    
    df = pd.DataFrame({
        "time": pd.to_datetime(hourly["time"]),
        "temperature": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "wind_speed": hourly["wind_speed_10m"],
        "precipitation": hourly["precipitation"]
    })
    
    df["date"] = df["time"].dt.date
    
    daily_stats = df.groupby("date").agg({
        "temperature": "mean",
        "humidity": "mean",
        "wind_speed": "mean",
        "precipitation": "sum"
    }).round(2)
    
    daily_stats["temp_trend"] = daily_stats["temperature"].diff().round(2)
    daily_stats["temp_trend_str"] = daily_stats["temp_trend"].apply(
        lambda x: f"+{x}" if x > 0 else (f"{x}" if pd.notnull(x) else "N/A")
    )
    
    return daily_stats.reset_index()

def visualize_data(df, city_name):
    """Generates a combo chart and returns the filepath."""
    plt.figure(figsize=(10, 6))
    
    ax1 = plt.gca()
    bars = ax1.bar(df['date'], df['precipitation'], color='#4a90e2', alpha=0.6, label='Rain (mm)')
    ax1.set_ylabel('Precipitation (mm)', color='#4a90e2', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#4a90e2')
    
    ax2 = ax1.twinx()
    line = ax2.plot(df['date'], df['temperature'], color='#e74c3c', marker='o', linewidth=3, label='Temp (°C)')
    ax2.set_ylabel('Temperature (°C)', color='#e74c3c', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    
    plt.title(f'Weather Analysis: {city_name} (Last 7 Days)', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(handles1 + handles2, labels1 + labels2, loc='upper left')

    filename = f"{OUTPUT_DIR}/{city_name}_weather_chart.png"
    plt.savefig(filename)
    plt.close()
    return filename

def send_to_telegram(text, image_path):
    """Sends the report and image to Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n[INFO] Telegram keys not found. Skipping Telegram notification.")
        return

    print(f"\nSending report to Telegram (Chat ID: {TELEGRAM_CHAT_ID})...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'photo': img_file}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': text}
            response = requests.post(url, files=files, data=data)
            
        if response.status_code == 200:
            print("[SUCCESS] Telegram message sent!")
        else:
            print(f"[ERROR] Telegram failed: {response.text}")
    except Exception as e:
        print(f"[ERROR] Could not send to Telegram: {e}")

def main():
    parser = argparse.ArgumentParser(description="Analyze weather data for a city.")
    parser.add_argument("--city", type=str, required=True, help="Name of the city")
    args = parser.parse_args()

    print(f"--- Weather Analysis for {args.city} ---")
    
    lat, lon, city_name, timezone = get_coordinates(args.city)
    print(f"Location: {city_name} (Lat: {lat}, Lon: {lon})")
    
    weather_data = fetch_weather_data(lat, lon, timezone)
    df_result = analyze_data(weather_data)
    
    # Generate text report
    print("\n--- Daily Summary ---")
    header = f"{'Date':<12} | {'Avg Temp':<10} | {'Trend':<8} | {'Wind (km/h)':<12} | {'Rain (mm)'}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    
    report_text = f"🌤 **Weather Report for {city_name}**\n\n"
    
    for _, row in df_result.iterrows():
        line = f"{str(row['date']):<12} | {row['temperature']:<10} | {row['temp_trend_str']:<8} | {row['wind_speed']:<12} | {row['precipitation']}"
        print(line)
        report_text += f"📅 {row['date']}: {row['temperature']}°C ({row['temp_trend_str']}), 💧 {row['precipitation']}mm\n"

    # Export CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_filename = f"{OUTPUT_DIR}/{city_name}_weather_report.csv"
    export_df = df_result.drop(columns=["temp_trend_str"])
    export_df.to_csv(csv_filename, index=False)
    print(f"\n[SUCCESS] CSV saved to: {csv_filename}")
    
    # Generate Chart
    chart_filename = visualize_data(df_result, city_name)
    print(f"[SUCCESS] Chart saved to: {chart_filename}")
    
    # Send to Telegram
    send_to_telegram(report_text, chart_filename)

if __name__ == "__main__":
    main()
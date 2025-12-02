# Weather Data Analyzer Service 🌤️

A robust Python-based microservice designed to fetch, analyze, and visualize historical weather data for any city. The application runs in a Docker container and sends detailed reports (charts + summary) directly to Telegram.

## 📌 Project Description
This tool automates the process of weather data analysis. It performs the following steps:
1.  Fetches historical weather data (last 7 days) using the **Open-Meteo API**.
2.  Aggregates hourly data into daily summaries using **Pandas**.
3.  Calculates daily trends (temperature changes compared to the previous day).
4.  Generates a dual-axis visualization (Temperature line + Precipitation bars) using **Matplotlib**.
5.  Exports data to a CSV file.
6.  Sends the chart and a text summary to a specified Telegram Chat via **Telegram Bot API**.

## 🛠️ Technology Stack
* **Python 3.9**
* **Pandas & NumPy** (Data processing)
* **Matplotlib** (Visualization)
* **Docker & Docker Compose** (Containerization)
* **Open-Meteo API** (Data Source)

## 🚀 How to Run via Docker (Recommended)

**Prerequisites:** Docker Desktop installed.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/BeemasterHome/Weather.git](https://github.com/BeemasterHome/Weather.git)
    cd Weather
    ```

2.  **Configure Environment Variables:**
    Open `docker-compose.yml` and insert your Telegram credentials:
    * `TELEGRAM_TOKEN`: Your Bot Token.
    * `TELEGRAM_CHAT_ID`: Your Chat ID (or Channel ID).

3.  **Build the image:**
    ```bash
    docker-compose build --no-cache
    ```

4.  **Run the application:**
    Replace `Kyiv` with any city name.
    ```bash
    docker-compose run --rm weather-app --city Kyiv
    ```

   *The container will automatically remove itself after execution.*

## 💻 How to Run Locally (Without Docker)

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables (Optional - for Telegram):**
    * Linux/Mac: `export TELEGRAM_TOKEN=your_token`
    * Windows (CMD): `set TELEGRAM_TOKEN=your_token`

3.  **Run the script:**
    ```bash
    python weather_analyzer.py --city Lviv
    ```

## 📊 Example CLI Commands

Analyze weather for London:
```bash
docker-compose run --rm weather-app --city London

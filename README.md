# Akasa-Air-Assignment
Overview : 
This project analyzes flight data to derive insights about delays, airline performance, and scheduling patterns. It includes data cleaning, normalization, analysis, and visualization components.

Requirements:
Python 3.7+
pandas
sqlite3
seaborn
matplotlib

Install the required packages:
pip install pandas sqlite3 seaborn matplotlib

Instructions :
1.Place your flight data CSV file in the project directory and name it flights.csv.
2.Run the main script: python main.py
3.Follow the prompts to handle duplicate and inconsistent entries.
4.The script will generate:
    *A cleaned and normalized CSV file: transformed_dataset.csv
    *An SQLite database: flights.db
    *Several visualizations of the data
    *A summary of insights in the console output

File Descriptions:
main.py: The main script that orchestrates the data processing and analysis pipeline.
flights.csv: The input data file.
transformed_dataset.csv: The cleaned and normalized output data file.
flights.db: SQLite database containing the processed data.

Functions:
load_and_preprocess_data(): Loads and initially processes the data.
handle_missing_values(): Deals with NaN values in the dataset.
remove_duplicates(): Identifies and removes duplicate entries.
handle_inconsistent_entries(): Identifies and handles inconsistent time entries.
plot_delay_histogram(data) : Generates Histogram for Delay Distribution
plot_delay_by_airline(): Visualizes delays by airline over time.
calculate_average_delay_per_airline(): Computes average delays for each airline.
analyze_delay_by_departure_time(): Analyzes the relationship between departure time and delays.
plot_delay_distribution_by_airline(): Visualizes the distribution of delays by airline.
save_to_sqlite(): Saves the processed data to an SQLite database.

Visualizations:
The script generates several visualizations:
Histogram for Delay Distribution
Flight Delay Minutes by Airline over time
Average Flight Delay by Departure Time
Flight Delays by Airline (box plot)

import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_and_preprocess_data(file_path):
    try:
        # Reading data from a CSV file into a Pandas DataFrame
        data = pd.read_csv(file_path)
        # Storing a copy of the dataframe as backup
        backup = data.copy()
        # Sorting the entries by FlightNumber to ensure they are grouped logically.
        data.sort_values(by='FlightNumber', inplace=True)
        
        # Converting dates and times to DateTime objects
        data['DepartureDate'] = pd.to_datetime(data['DepartureDate'], errors='coerce')
        data['ArrivalDate'] = pd.to_datetime(data['ArrivalDate'], errors='coerce')
        data['DepartureTime'] = pd.to_datetime(data['DepartureTime'], format='%I:%M %p', errors='coerce')
        data['ArrivalTime'] = pd.to_datetime(data['ArrivalTime'], format='%I:%M %p', errors='coerce')
        
        # Calculating FlightDuration
        data['FlightDuration'] = (
            (data['ArrivalDate'] + (data['ArrivalTime'] - pd.Timestamp('1970-01-01'))) -
            (data['DepartureDate'] + (data['DepartureTime'] - pd.Timestamp('1970-01-01')))
        )
        data['FlightDuration (Minutes)'] = data['FlightDuration'].dt.total_seconds() / 60
        data['FlightDuration'] = data['FlightDuration'].apply(
            lambda x: f"{x.components.hours:02}:{x.components.minutes:02}" if pd.notnull(x) else '00:00'
        )
        
        # Converting times to 24-hour format
        data['DepartureTime'] = data['DepartureTime'].dt.strftime('%H:%M')
        data['ArrivalTime'] = data['ArrivalTime'].dt.strftime('%H:%M')
        
        return data
    except Exception as e:
        print(f"Error loading and preprocessing data: {e}")
        return pd.DataFrame()

def handle_missing_values(data):
    try:
        # Grouping Airlines, Calculating median value of DelayMinutes of each group and Replacing NAN values with the respective group's median
        data['DelayMinutes'] = data.groupby('Airline')['DelayMinutes'].transform(lambda x: x.fillna(x.median()))
        return data
    except Exception as e:
        print(f"Error handling missing values: {e}")
        return data

def remove_duplicates(data):
    try:
        # Identifying Duplicates based on combination of the FlightNumber, DepartureDate, and DepartureTime columns
        duplicates = data.duplicated(subset=['FlightNumber', 'DepartureDate', 'DepartureTime'], keep=False)
        if duplicates.any():
            print("Duplicates found in the following entries:")
            duplicate_entries = data[duplicates]
            print(duplicate_entries)

            while True:
                # Prompt to confirm if user wishes to remove the duplicates found
                user_input = input("\nDo you want to remove duplicates? (yes/no): ").strip().lower()
                if user_input in ['yes', 'no']:
                    break
                else:
                    print("Please enter 'yes' or 'no'.")

            if user_input == 'yes':
                entries_to_keep = []
                # Prompt to select the duplicate entries to be removed
                for index, row in duplicate_entries.iterrows():
                    print(f"\nDuplicate Entry: {row.to_dict()}")
                    keep_input = input("Do you want to keep this entry? (yes/no): ").strip().lower()
                    if keep_input == 'yes':
                        entries_to_keep.append(index)
                # Storing the clean dataframe with duplicates removed
                data_cleaned = data.drop_duplicates(subset=['FlightNumber', 'DepartureDate', 'DepartureTime'], keep=False)
                data_cleaned = pd.concat([data_cleaned, data.loc[entries_to_keep]]).drop_duplicates()
                return data_cleaned

        return data
    except Exception as e:
        print(f"Error removing duplicates: {e}")
        return data

def handle_inconsistent_entries(data):
    try:
        inconsistent_entries = []
        added_indices = set()
        
        for index, row in data.iterrows():
            departure_time = row['DepartureTime']
            arrival_time = row['ArrivalTime']
            flight_duration = row['FlightDuration (Minutes)']
            # Identifying Inconsistent Entries entries where the ArrivalTime was recorded as being earlier than the DepartureTime on the same day, as well as for instances where the FlightDuration exceeded a reasonable threshold (e.g., 480 minutes)
            if arrival_time < departure_time or flight_duration > 480:
                if index not in added_indices:
                    inconsistent_entries.append(row)
                    added_indices.add(index)
        # These entries were stored in another dataframe
        inconsistent_df = pd.DataFrame(inconsistent_entries)
        
        if not inconsistent_df.empty:
            print("\nInconsistent entries found:")
            print(inconsistent_df)
            # Prompt to confirm if user wishes to remove the incosistent entries found
            while True:
                user_input = input("Do you want to remove inconsistent entries? (yes/no): ").strip().lower()
                if user_input in ['yes', 'no']:
                    break
                else:
                    print("Please enter 'yes' or 'no'.")
            
            if user_input == 'yes':
                entries_to_keep = []
                for index, row in inconsistent_df.iterrows():
                    print(f"\nInconsistent Entry: {row.to_dict()}")
                    # Prompt to select the inconsistent entries to be removed
                    keep_input = input("Do you want to keep this entry? (yes/no): ").strip().lower()
                    if keep_input == 'yes':
                        entries_to_keep.append(index)
                # Storing the dataframe with marked entries removed
                cleaned_data = data.drop(index=added_indices).reset_index(drop=True)
                retained_entries = data.loc[entries_to_keep]
                cleaned_data = pd.concat([cleaned_data, retained_entries]).drop_duplicates().reset_index(drop=True)

                return cleaned_data, inconsistent_df

        return data, inconsistent_df
    except Exception as e:
        print(f"Error handling inconsistent entries: {e}")
        return data, pd.DataFrame()

def plot_delay_by_airline(data):
    # Plotting Line Chart of Flight Delay Minutes by Airlines
    try:
        plt.figure(figsize=(12, 6))
        for airline, group in data.groupby('Airline'):
            group_sorted = group.sort_values(by='DepartureDate')
            plt.plot(group_sorted['DepartureDate'], group_sorted['DelayMinutes'], marker='o', label=airline)
        plt.title('Flight Delay Minutes by Airline')
        plt.xlabel('Departure Date')
        plt.ylabel('Delay Minutes')
        plt.xticks(rotation=45)
        plt.legend(title='Airline')
        plt.grid(True)
        # Correcting the format of the dates displayed in the X-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error plotting delay by airline: {e}")

def plot_delay_histogram(data, column='DelayMinutes', bins=15):
    # Plotting Histogram of Flight Delays for Delay Distribution
    try:
        plt.figure(figsize=(10, 6))
        plt.hist(data[column].dropna(), bins=bins, color='blue', alpha=0.7, edgecolor='black')
        plt.title('Distribution of Delay Minutes')
        plt.xlabel('Delay Minutes')
        plt.ylabel('Frequency')
        plt.grid(axis='y', alpha=0.75)
        plt.xticks(range(0, int(data[column].max()) + 10, 10))  
        plt.show()
    except Exception as e:
        print(f"Error plotting histogram for delay distribution: {e}")

def calculate_average_delay_per_airline(data):
    # Calculating the Average Delay observed for each Airline
    try:
        average_delay_per_airline = data.groupby('Airline')['DelayMinutes'].mean().reset_index()
        average_delay_per_airline.rename(columns={'DelayMinutes': 'AverageDelay (in Minutes)'}, inplace=True)
        return average_delay_per_airline
    except Exception as e:
        print(f"Error calculating average delay per airline: {e}")
        return pd.DataFrame()

def analyze_delay_by_departure_time(data):
    # Calculating the Average Delay observed for each Airline
    try:
        # Convert 'DepartureDate' and 'DepartureTime' to a datetime object
        data['DepartureDatetime'] = pd.to_datetime(data['DepartureDate'].astype(str) + ' ' + data['DepartureTime'])
        data['DepartureTimeOnly'] = data['DepartureDatetime'].dt.time
        # Calculate average delay per departure time
        avg_delay_per_time = data.groupby('DepartureTimeOnly')['DelayMinutes'].mean().reset_index()
        avg_delay_per_time.columns = ['Departure Time', 'Average Delay (Minutes)']
        
        # Plot the average delay by departure time
        plt.figure(figsize=(12, 6))
        avg_delay_per_time.sort_values(by='Departure Time', inplace=True)  
        plt.plot(avg_delay_per_time['Departure Time'].astype(str), avg_delay_per_time['Average Delay (Minutes)'], marker='o')
        plt.title('Average Flight Delay by Departure Time')
        plt.xlabel('Departure Time')
        plt.ylabel('Average Delay (Minutes)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
        return avg_delay_per_time
    except Exception as e:
        print(f"Error analyzing delay by departure time: {e}")
        return pd.DataFrame()

def plot_delay_distribution_by_airline(data):
    try:
        # Create boxplot for delay distribution by airline
        sns.set(style="whitegrid")
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='Airline', y='DelayMinutes', data=data)
        plt.title('Flight Delays by Airline')
        plt.xlabel('Airline')
        plt.ylabel('Delay Minutes')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error plotting delay distribution by airline: {e}")

def save_to_sqlite(data, db_name='flights.db'):
    # Save dataframe to SQLite database
    try:
        conn = sqlite3.connect(db_name)
        data.to_sql('flights', conn, if_exists='replace', index=False)
        conn.close()
    except Exception as e:
        print(f"Error saving data to SQLite: {e}")

def main():
    try:
        # Load and preprocess data
        data = load_and_preprocess_data('flights.csv')
        
        # Handle missing values
        data = handle_missing_values(data)
        
        # Remove duplicates
        data = remove_duplicates(data)
        
        # Handle inconsistent entries
        data, inconsistent_entries = handle_inconsistent_entries(data)
        data.sort_values(by='FlightNumber', inplace=True)

        # Export cleaned DataFrame to CSV
        data.to_csv('transformed_dataset.csv', index=False)

        # Save processed data to SQLite
        save_to_sqlite(data)

        print("\nData : ")
        print(data)
        
        # Perform analysis and generate visualizations
        plot_delay_histogram(data) 
        plot_delay_by_airline(data)
        avg_delay_per_airline = calculate_average_delay_per_airline(data)
        print("\nAverage Delay per Airline:")
        print(avg_delay_per_airline)
        
        avg_delay_per_time = analyze_delay_by_departure_time(data)
        print("\nAverage Delay by Departure Time:")
        print(avg_delay_per_time)
        
        plot_delay_distribution_by_airline(data)
        
        # Generate insights and recommendations
        print("\nInsights:")
        if not avg_delay_per_airline.empty:
            most_delayed_airline = avg_delay_per_airline.loc[avg_delay_per_airline['AverageDelay (in Minutes)'].idxmax(), 'Airline']
            print(f"The airline with the most delays on average is {most_delayed_airline}.")
        if not avg_delay_per_time.empty:
            print("Flights departing between", avg_delay_per_time.iloc[avg_delay_per_time['Average Delay (Minutes)'].idxmax()]['Departure Time'], "tend to have the highest delays.")
        if not inconsistent_entries.empty:
            print("\nConsider reviewing inconsistent entries for potential corrections.")
    
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
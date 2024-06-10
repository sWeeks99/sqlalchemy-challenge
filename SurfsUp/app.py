# Import the dependencies.
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from datetime import datetime, timedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Read CSV files into DataFrames
precipitation_df = pd.read_csv('../SurfsUp/Resources/Precipitation_data_12_months.csv')
tobs_df = pd.read_csv('../SurfsUp/Resources/Most_active_station.csv')

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-24<br/>"
        f"/api/v1.0/2016-08-24/2017-07-11;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Read the CSV file into a DataFrame
    precipitation_df = pd.read_csv('../SurfsUp/Resources/Precipitation_data_12_months.csv')

    # Convert the 'Date' column to datetime format
    precipitation_df['Date'] = pd.to_datetime(precipitation_df['Date'])

    # Calculate the date one year ago from the last date in the dataset
    max_date = precipitation_df['Date'].max()
    one_year_ago = max_date - timedelta(days=365)

    # Filter the DataFrame to include only data for the last year
    last_year_data = precipitation_df[precipitation_df['Date'] >= one_year_ago]

    # Convert the filtered DataFrame to a dictionary with string keys
    precipitation_dict = last_year_data.set_index('Date')['Precipitation'].to_dict()
    precipitation_dict = {str(key): value for key, value in precipitation_dict.items()}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Get a list of stations from the dataset
    station_list = session.query(Station.station).all()
    stations = list(np.ravel(station_list))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Read the CSV file into a DataFrame
    tobs_df = pd.read_csv('../SurfsUp/Resources/Most_active_station.csv')

    # Convert the DataFrame to a dictionary
    tobs_dict = tobs_df.set_index('Date')['tobs'].to_dict()
    
    return jsonify(tobs_dict)

@app.route("/api/v1.0/temp/2016-08-24")
def start():
    start_date = '2016-08-24'
    end_date = '2017-07-11'
    
    # Query the database to calculate TMIN, TAVG, and TMAX for dates between the start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert the results to a list of dictionaries
    temp_data = []
    for result in results:
        temp_data.append({
            "TMIN": result[0],
            "TAVG": result[1],
            "TMAX": result[2]
        })

    return jsonify(temp_data)

@app.route("/api/v1.0/2016-08-24/2017-07-11")
def temp_start_end():
    start_date = '2016-08-24'
    end_date = '2017-07-11'
    
    # Query the database to calculate TMIN, TAVG, and TMAX for dates between the start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert the results to a list of dictionaries
    temp_data = []
    for result in results:
        temp_data.append({
            "TMIN": result[0],
            "TAVG": result[1],
            "TMAX": result[2]
        })

    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)
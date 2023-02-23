#################################################
# Dependencies
#################################################

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


# Save reference to the table
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


################################################
# Create an instance for the flask ID
################################################

app = Flask(__name__)

#################################################
# Define the homepage route
#################################################


@app.route("/")
def welcome():
    #List all available routes
        return (
            f"Welcome to the Hawaii Weather API!:<br/>"
            f"Avaiable Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"Available Routes with Variable Input:<br/>"
            f"/api/v1.0/start<br/>"
            f"/api/v1.0/start/end"
        )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year."""
     # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    prcp_data = {date: prcp for date, prcp in results}

    # Return the JSON representation of the dictionary
    return jsonify(prcp_data)



@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()
    print("test")
    print(results)
    # Convert list of tuples into normal list
    Stations = list(np.ravel(results))

    # Return the list as a JSON object
    return jsonify(Stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the last year."""
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query the most active station
    station_query = session.query(Measurement.station, func.count(Measurement.tobs))\
                           .group_by(Measurement.station)\
                           .order_by(func.count(Measurement.tobs).desc())\
                           .first()
    most_active_station = station_query[0]

    # Query the last 12 months of temperature observation data for the most active station
    results = session.query(Measurement.date, Measurement.tobs)\
                     .filter(Measurement.station == most_active_station)\
                     .filter(Measurement.date >= year_ago)\
                     .all()

    # Create a list of temperature observations from the query results
    temps = list(np.ravel(results))
    
    # Return the list as a JSON object
    return jsonify({"Minimum Temperature": temps[0],
                    "Average Temperature": temps[1],
                    "Maximum Temperature": temps[2]})


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
     # Define the list of select statements
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Calculate TMIN, TAVG, TMAX for dates greater than or equal to the start date
        results = session.query(*sel).filter(Measurement.date >= start).all()

        # Convert the query results to a list
        temps = list(np.ravel(results))

        # Return the JSON representation of the list
        return jsonify(temps)

    # Calculate TMIN, TAVG, TMAX for dates between start and end dates
    results = session.query(*sel).filter(Measurement.date >= start)






if __name__ == '__main__':
    app.run(debug=True)
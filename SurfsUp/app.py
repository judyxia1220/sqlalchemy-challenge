# Import the dependencies.
from flask import Flask, jsonify
import numpy as np

import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask_cors import CORS


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return(
        f"Available Routes:<br/>----------------<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"/api/v1.0/<start>/<end><br/><br/>"
        f"date format: yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    
    # Query the most recent date in the data set.
    mostRecentDate = session.query(func.max(measurement.date)).scalar()

    # Calculate the date one year from the last date in data set.
    oneYearAgo = dt.datetime.strptime(mostRecentDate, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= oneYearAgo).all()

    # Store results in dictionary
    precDict = dict((key, value) for key, value in results)

    #Return the JSON representation of your dictionary
    return jsonify(precDict)


@app.route("/api/v1.0/stations")
def stations():

    # Query stations
    stations = session.query(station.id, station.name, station.latitude, station.longitude, station.longitude, station.elevation).all()

    # Return a JSON list of stations from the dataset.
    stationList = list(np.ravel(stations))
    return jsonify(stationList)


@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    mostActiveStation = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()
    
    mostActiveStationID = mostActiveStation[0]
    
    # Query the most recent date in the data set.
    mostRecentDate = session.query(func.max(measurement.date)).scalar()
    
    # Calculate the date one year from the last date in data set.
    oneYearAgo = dt.datetime.strptime(mostRecentDate, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most-active station for the previous year of data.
    tempObsData = session.query(measurement.tobs).\
        filter(measurement.station == mostActiveStationID).\
        filter(measurement.date >= oneYearAgo).all()

    # Return a JSON list of temperature observations for the previous year.
    tobs_list = list(np.ravel(tempObsData))
    return jsonify(tobs_list)

    
@app.route("/api/v1.0/<start>")
def startTime(start):
    # convert date to datetime objects
    startDate = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

    results = session.query(func.min(measurement.tobs), 
                            func.max(measurement.tobs), 
                            func.avg(measurement.tobs)).\
                            filter(measurement.date >= startDate).all()
    

    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    tempList = [{"Start Date": startDate, 
                 "Min temp": tempList[0],
                  "Max temp": tempList[1],
                  "Avg temp": tempList[2]} for tempList in results]
    
    return jsonify(tempList)


@app.route("/api/v1.0/<start>/<end>")
def endTime(start,end):
    # convert date to datetime objects
    startDate = dt.datetime.strptime(start, '%Y-%m-%d').date()
    endDate = dt.datetime.strptime(end, '%Y-%m-%d').date()

    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    results = session.query(func.min(measurement.tobs),
                                func.max(measurement.tobs),
                                func.avg(measurement.tobs)).\
                                filter(measurement.date>=startDate, measurement.date<=endDate).all()

    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    tempList = [{"Start Date": startDate,
                "End Date": endDate,
                 "Min temp": tempList[0],
                  "Max temp": tempList[1],
                  "Avg temp": tempList[2]} for tempList in results]
    
    return jsonify(tempList)

# Close Session
session.close()


if __name__ == "__main__":
    app.run(debug=True)
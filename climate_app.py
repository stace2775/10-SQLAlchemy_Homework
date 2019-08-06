#Description:  010-SQLAlchemy_Homework
#
#
#   Modification Summary:
#   DD-MMM-YYYY    Author          Description
#   05-Aug-2019    Stacey Smith     Initial Creation
#
#


import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import numpy as np
import pandas as pd

import datetime as dt
from datetime import timedelta


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
station = Base.classes.station
measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"----Returns precipitation data.<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"----Returns station names.<br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"----Returns temp observations for one year from the last recorded date.<br/><br/>"
        f"/api/v1.0/start<br/>"
        f"----Returns the minimum temperature, average temperature, and max temperature calculated for the date range beginning with the given start date " \
        f"and for all dates greater than and equal to the start date.<br/>" \
        f"Replace 'start' with the date in yyyy-mm-dd format to return data.<br/><br/> "
        f"/api/v1.0/start/end<br/>"
        f"----Returns the minimum temperature, average temperature, and max temperature calculated for the date range beginning with the given start-end range " \
        f"and for dates between the start and end date inclusive.<br/>" \
        f"Replace 'start' and 'end' with the date in yyyy-mm-dd format to return data.<br/><br/> "
    )

#################################################
# /api/v1.0/precipitation
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    """Return all precipitation data"""
    session = Session(engine)
    prcp = session.query(measurement.date, measurement.prcp).all()

    session.close()

# Convert the query results to a Dictionary using date as the key and prcp as the value.
    prcp_data =[]

    for i in prcp:
        prcp_dict = {}
        prcp_dict["date"] = i.date
        prcp_dict["prcp"] = i.prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)



#################################################
# /api/v1.0/stations
#################################################
@app.route("/api/v1.0/stations")
def stations():

    """Return all stations data"""
    session = Session(engine)
    station_name = session.query(station.name).all()

    session.close()

    stations_data = []
    for i in station_name:
        stations_dict = {}
        stations_dict["station name"] = i.name
        stations_data.append(stations_dict)

    return jsonify(stations_data)



#################################################
# /api/v1.0/tobs
#################################################
@app.route("/api/v1.0/tobs")
def tobs():

    """Return all temperature data"""
    session = Session(engine)
    
    max_date = session.query(func.max(measurement.date))
    for row in max_date:
        last_date = dt.datetime.strptime((str(row)).strip("('',)"), '%Y-%m-%d')
   
    one_year = last_date - dt.timedelta(days=365)

    tobs_year = session.query(measurement.id, measurement.station, measurement.date, measurement.prcp, measurement.tobs).\
    filter(measurement.date < max_date).\
    filter(measurement.date > one_year)
   
    session.close()

    tobs_data = []
    
    for i in tobs_year:
        tobs_dict = {}
        tobs_dict["id"] = i.id
        tobs_dict["station name"] = i.station
        tobs_dict["date"] = i.date
        tobs_dict["prcp"] = i.prcp
        tobs_dict["tobs"] = i.tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)



#################################################
# /api/v1.0/start
#################################################
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    
    """Returns temperature data based on a specific start date"""
    session = Session(engine)

    start_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= start_date).all()
   
    session.close()
    
    start_data =[]

    for i in start_temps:
        start_dict = {}
        start_dict["min"] = i[0]
        start_dict["avg"] = i[1]
        start_dict["max"] = i[2]
        start_data.append(start_dict)

    return jsonify(start_data)

    
#################################################
# /api/v1.0/start/end
#################################################
@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date, end_date):
    
    """Returns temperature data based on a specific start and end date"""
    session = Session(engine)
    
    start_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close()

    startend_data =[]

    for i in start_temps:
        startend_dict = {}
        startend_dict["min"] = i[0]
        startend_dict["avg"] = i[1]
        startend_dict["max"] = i[2]
        startend_data.append(startend_dict)

    return jsonify(startend_data)

if __name__ == '__main__':
    app.run(debug=True)

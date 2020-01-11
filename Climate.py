from datetime import datetime
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the measurement and station tables
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def welcome():
    """List all available api routes."""
    return  """Available Routes:<br>
        <br/>
        Dates and precipitation observations for last year of the measurement table<br/>
        /api/v1.0/precipitation<br/>
        
        <br/>
        List of stations from the Hawaii data<br/>
        /api/v1.0/stations<br/>
        
        <br/>
        List of Temperature Observations for the previous year of the measurement table<br/>
        //api/v1.0/tobs<br/>

        <br/>
        list of `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date<br/>
        /api/v1.0/calc_temps/<start><br/>
        
        <br/>
        List of `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive<br/>
        //api/v1.0/calc_temps/<start>/<end><br/>"""

    


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    """Return a list of dates and precipitation observations"""
    # Query all dates and precipitation observations last year from the measurement table
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                   filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()
    session.close()

    return jsonify(precipitation_data)



@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    # Query all stations from the station table
    station_results = session.query(Station.station, Station.name).group_by(Station.station).all()

    station_list = list(np.ravel(station_results))
    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    temp_results = session.query(Measurement.station, Measurement.tobs).filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()

    session.close()
    

    return jsonify(temp_results)



@app.route("/api/v1.0/calc_temps/<start>")
def calc_temps(start='start_date'):

    session = Session(engine)

    start_date = datetime.strptime('2016-08-23', '%Y-%m-%d').date()
    c_results = session.query(func.max(Measurement.tobs), \
                            func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date) 
                      
    
    temp_Obs = []
    for tobs in c_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])

        session.close()  
        
        temp_Obs.append(tobs_dict)

    session.close()  

    return jsonify(temp_Obs)


@app.route("/api/v1.0/calc_temps/<start>/<end>")
   
def calc_temps_2(start='start_date', end='end_date'):  

    session = Session(engine)

    start_date = datetime.strptime('2016-08-23', '%Y-%m-%d').date()
    end_date = datetime.strptime('2017-08-23', '%Y-%m-%d').date()

    start_end_results=session.query(func.max(Measurement.tobs).label("max_tobs"), \
                      func.min(Measurement.tobs).label("min_tobs"),\
                      func.avg(Measurement.tobs).label("avg_tobs")).\
                      filter(Measurement.date.between(start_date , end_date)) 


    start_end_tempObs = []
    for tobs in start_end_results:
        tobs_dict = {}
        tobs_dict["TAVG"] = float(tobs[2])
        tobs_dict["TMAX"] = float(tobs[0])
        tobs_dict["TMIN"] = float(tobs[1])

        start_end_tempObs.append(tobs_dict)

        session.close()  
    
    return jsonify(start_end_tempObs)


if __name__ == '__main__':
    app.run(debug=True)
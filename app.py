from flask import Flask, jsonify
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def welcome():
    return(
        f"Weclome <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate/<start><br/>"
        f"/api/v1.0/enddate/<start>/<end></br>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    
    session = Session(engine)
    date_prcp = session.query(measurement.date, measurement.prcp).all()

    session.close()
    
    x = []
    for date, prcp in date_prcp:
        date_dict = {}
        date_dict[date] = prcp
        x.append(date_dict)
    return jsonify(x)


@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    station = session.query(station.station).all()

    session.close()

    station_list = list(np.ravel(station))

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine) 
    latest_date = dt.date(2017,8, 23)
    year =  latest_date - dt.timedelta(days = 365)

    months = session.query(measurement.date, measurement.tobs).filter_by(station = "USC00519281").\
    filter(measurement.date >= year).all()

    session.close()

    last_months_list = []
    for date, tobs in months:
        tobs_dict = {}
        tobs_dict[date] = tobs
        last_months_list.append(tobs_dict) 
    return jsonify(last_months_list)     

@app.route('/api/v1.0/start/<start>')
def start_date(start):
    session = Session(engine)

    station_id = [func.min(measurement.tobs),
           func.avg(measurement.tobs),
           func.max(measurement.tobs)
    ]
    
    start_filter = session.query(*station_id).filter(measurement.date >= start).all()
    start_list = [
        {"Min": start_filter[0][0]},
        {"avg": start_filter[0][1]},
        {"max": start_filter[0][2]}
    ]
    if start <= '2017-08-23':
        return jsonify(start_list)
    else:
        return jsonify("Error")

    session.close()

@app.route('/api/v1.0/start/<start>/end/<end>')
def start_end(start, end):
    session = Session(engine)

    station_id = [func.min(measurement.tobs),
           func.avg(measurement.tobs),
           func.max(measurement.tobs)
    ]
    
    
    start_end_filter = session.query(*station_id).\
        filter(measurement.date.between(start,end)).all()
    start_end_list = [
        {"TMIN": start_end_filter[0][0]},
        {"TAVG": start_end_filter[0][1]},
        {"TMAX": start_end_filter[0][2]}
    ]
    if (start <= '2017-08-23') and (end >='2010-01-01') :
        return jsonify(start_end_list)
    else:
        return jsonify("Error")
    
    session.close()
if __name__ == '__main__':
    app.run(debug=True)
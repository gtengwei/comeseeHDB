## Everything related to the HDBFlat
from flask import Blueprint, render_template, request, flash, redirect, url_for

from website.models import HDBFlat

from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
import json,csv
import sqlite3, os, sys


flat = Blueprint('hdb-flat', __name__)

## Route for FlatDetails Page
@flat.route('/hdb-flat')
def updateHDBFlat():

    return render_template("Flat_details.html", user=current_user)
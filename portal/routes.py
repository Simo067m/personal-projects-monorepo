import psutil
from flask import Blueprint, render_template, jsonify, url_for

# Define the Blueprint
portal_bp = Blueprint('portal', __name__)

@portal_bp.route("/")
def home():
    return render_template("portal_home.html")

@portal_bp.route('/api/system_status')
def system_status():
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    # Memory
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Temp
    cpu_temp = "N/A"
    try:
        temps = psutil.sensors_temperatures()
        if 'cpu_thermal' in temps:
            cpu_temp = round(temps['cpu_thermal'][0].current, 1)
        elif 'coretemp' in temps: 
            cpu_temp = round(temps['coretemp'][0].current, 1)
    except Exception:
        pass 

    return jsonify({
        "cpu_usage": cpu_percent,
        "memory_usage": memory_percent,
        "cpu_temp": cpu_temp
    })
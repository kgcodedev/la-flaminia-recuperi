from datetime import datetime
from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configurazione del database SQLite locale per la memorizzazione dei consensi privacy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///privacy_log.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Modello per la "scatola nera" della Privacy (conservazione IP, data e ora)
class PrivacyConsent(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  ip_address = db.Column(db.String(50), nullable=False)
  timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  user_agent = db.Column(db.String(255), nullable=True)


# Crea le tabelle del database all'avvio
with app.app_context():
  db.create_all()


@app.route('/')
def home():
  return render_template('HOME.html')


@app.route('/api/consenso-privacy', methods=['POST'])
def salva_consenso():
  if request.headers.get('X-Forwarded-For'):
    ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
  else:
    ip = request.remote_addr

  user_agent = request.headers.get('User-Agent', '')

  nuovo_consenso = PrivacyConsent(ip_address=ip, user_agent=user_agent)
  db.session.add(nuovo_consenso)
  db.session.commit()

  return jsonify({
      'status': 'success',
      'message': 'Consenso registrato correttamente.',
  })


if __name__ == '__main__':
  app.run(debug=True)
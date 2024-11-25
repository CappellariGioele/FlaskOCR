from models.conn import db
from flask_bcrypt import Bcrypt
from flask_login import UserMixin


bcrypt = Bcrypt()


# Classe che rappresenta l'utente nel DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    api_keys = db.relationship('ApiKey', backref='user', lazy='dynamic')
    ocr_results = db.relationship('OCRResult', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def set_api_key(self, key_value):
        """Imposta una chiave API personalizzata."""
        new_key = ApiKey(user=self, value=key_value)
        db.session.add(new_key)
        db.session.commit()

    def get_api_keys(self):
        """Restituisce le chiavi API personalizzate dell'utente."""
        return self.api_keys
    
    def __repr__(self):
        return f'<User username:{self.username}, email:{self.email}>'


# Classe che rappresenta l'immagine che gli si manda tramite la richiesta.
class OCRResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ocr_text = db.Column(db.Text, nullable=False)  # Testo estratto
    image_path = db.Column(db.String(255), nullable=False)  # Percorso immagine salvata
    processed_image_path = db.Column(db.String(255)) # percorso immagine processata
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<OCRResult:{self.id}>'


# Classe che rappresenta la api key nel DB
class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    value = db.Column(db.String(36), unique=True, nullable=False)

# FlaskOCR
Progetto laboratorio di approfondimento Flask


Mancanze da inserire:
- Ruoli per flask admin
- Finire dei controlli per api key


Per far funzionare il progetto bisogna installare tesseract e impostare le seguenti variabili con il .env:
- SECRET_KEY="secret"
- SQLALCHEMY_DATABASE_URI="sqlite:///storage.db"
- TESSERACT_CMD_PATH="path"
- UPLOAD_IMAGES_PATH="./uploads/originals"
- UPLOAD_PROCESSED_IMAGES_PATH="./uploads/processed"


Per far funzionare il progetto, bisogna creare il db con: flask db upgrade

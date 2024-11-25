import os
import pytesseract
import PIL.Image
import cv2
import uuid
from flask import Blueprint, request, jsonify, url_for, send_file
from pytesseract import Output
from models.models import OCRResult, ApiKey
from models.conn import db


ocr = Blueprint('ocr', __name__)


# estensioni permesse dall'applicativo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp', 'gif', 'pnm'}


# configurazioni tesseract per fare ocr
BLOCK_TEXT_CONFIG = r"--psm 6 --oem 3"
SPARSE_TEXT_CONFIG = r"--psm 11 --oem 3"


# configurazione tesseract
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD_PATH")


def allowed_file(filename):
    """
    Helper per controllare se l'estensione è supportata
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image_file(image_file, upload_path = os.getenv("UPLOAD_IMAGES_PATH")):
    """
    Helper per salvare l'immagine caricata dall'utente.
    Ritorna il percorso del file e il nome del file.
    """

    if not allowed_file(image_file.filename):
        raise ValueError("Formato immagine non supportato.")
    
    file_extension = os.path.splitext(image_file.filename)[1].lower() # include il punto, es: .png
    filename = f"{uuid.uuid4()}{file_extension}"
    filepath = os.path.join(upload_path, filename)
    image_file.save(filepath)

    return filepath, filename


def handle_tesseract_configuration(method):
    """
    Helper per ottenere la configurazione di tesseract corretta
    in base al metodo scelto
    """

    if method == 'sparse':
        return SPARSE_TEXT_CONFIG
    return BLOCK_TEXT_CONFIG


@ocr.route('/text', methods=['POST'])
def get_text():
    """
    Ottieni il testo rilevato dall'immagine e il link per la GUI.
    """

    # verifico la api key
    api_key = ApiKey.query.filter_by(value=request.headers.get('X-API-KEY')).first()

    if api_key:
        if 'image' not in request.files:
            return jsonify({'error': 'Nessuna immagine caricata'}), 400
        
        # riceve la configurazione con la quale elaborare l'immagine
        method = request.args.get('method', 'sparse')

        try:
            # salva il file
            image_file = request.files['image']
            filepath, filename = save_image_file(image_file)

            # prende il testo dal file
            text = pytesseract.image_to_string(PIL.Image.open(filepath), config=handle_tesseract_configuration(method))

            result = OCRResult(user_id=api_key.user.id, image_path=filepath, ocr_text=text)
            db.session.add(result)
            db.session.commit()

            return jsonify({
                'result_url': url_for('base.show_result', result_id=result.id),
                'get_image_url': url_for('.get_image', result_id=result.id),
                'text': result.ocr_text
                })
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Errore interno del server'}), 500
    else:
        return jsonify({'error': 'API key non valida'}), 401


@ocr.route('/image', methods=['POST'])
def get_processed_image():
    """
    Processa l'immagine, evidenziando il testo presente in essa.
    Poi ritorna un json contenente il link per la GUI, il testo e il link
    per ottenere l'immagine processata.
    """

    # verifico la api key
    api_key = ApiKey.query.filter_by(value=request.headers.get('X-API-KEY')).first()

    if api_key:
        if 'image' not in request.files:
            return jsonify({'error': 'Nessuna immagine caricata'}), 400

        # riceve la configurazione con la quale elaborare l'immagine
        method = request.args.get('method', 'sparse')

        try:
            # salva il file
            image_file = request.files['image']
            filepath, filename = save_image_file(image_file)

            # legge immagine e inizia a processarla
            img = cv2.imread(filepath)
            height, width, _ = img.shape

            data = pytesseract.image_to_data(img, config=handle_tesseract_configuration(method), output_type=Output.DICT)

            len_data = len(data['text'])
            for i in range(len_data):
                # controlla che ci sia una "confidenza" del 50% min
                if float(data['conf'][i]) > 50:
                    (x, y, width, height) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    # img, punto1, punto2, coloreBGR, spessore
                    img = cv2.rectangle(img, (x, y), (x+width, y+height), (0, 255, 0), 2)
                    # img, testo, punto dove iniziare a scrivere, font, font scale, coloreBGR, spessore, line type
                    img = cv2.putText(img, data['text'][i], (x, y+height+20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            # salva l'immagine processata
            processed_filename = f"processed-{filename}"
            processed_filepath = os.path.join(os.getenv("UPLOAD_PROCESSED_IMAGES_PATH"), processed_filename)
            text = " ".join(data['text'])

            cv2.imwrite(processed_filepath, img)

            result = OCRResult(user_id=api_key.user.id, ocr_text=text, image_path=filepath, processed_image_path=processed_filepath)
            db.session.add(result)
            db.session.commit()

            return jsonify({
                'result_url': url_for('base.show_result', result_id=result.id),
                'text': result.ocr_text,
                'get_image_url': url_for('.get_image', result_id=result.id),
                'get_processed_image_url': f"{url_for('.get_image', result_id=result.id)}?type=processed"
                })
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Errore interno del server'}), 500
    else:
        return jsonify({'error': 'API key non valida'}), 401


@ocr.route('/image/<int:result_id>')
def get_image(result_id):
    """
    Ritorna l'immagine in base al id passato.
    """

    image_type = request.args.get("type")

    stmt = db.select(OCRResult).filter_by(id=result_id)
    ocr_result = db.session.execute(stmt).scalar_one_or_none()

    # TODO: aggiungere il controllo del proprietario del file (con api key)
    image_path = ocr_result.processed_image_path if image_type == "processed" else ocr_result.image_path
    try:
        return send_file(image_path)
    except Exception as e:
        return jsonify({'error': 'Errore interno del server'}), 500

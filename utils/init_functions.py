import os


def init_structure():
    """
    La funzione inizializza la struttura di cartelle necessarie per il funzionamento.
    Crea le cartelle per l'upload e il processo delle immagini se non sono presenti.
    """

    upload_path = os.getenv("UPLOAD_IMAGES_PATH")
    processed_img_path = os.getenv("UPLOAD_PROCESSED_IMAGES_PATH")

    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    if not os.path.exists(processed_img_path):
        os.makedirs(processed_img_path)

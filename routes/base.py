from flask import Blueprint, url_for, abort
from flask import render_template
from flask_login import login_required, current_user


base = Blueprint('base', __name__)


@base.route('/')
@login_required
def home():
    return render_template("ocr/home.html")


@base.route('/result/<int:result_id>')
@login_required
def show_result(result_id):
    ocr_result = current_user.ocr_results.filter_by(id=result_id).first()

    if ocr_result:
        return render_template("ocr/ocr_result.html", ocr_result=ocr_result)
    else:
        abort(404)



@base.route('/history')
@login_required
def history():
    ocr_values = []
    for ocr_res in current_user.ocr_results:
        formatted_date = ocr_res.created_at.strftime('%d.%m.%Y %H:%M:%S')
        ocr_values.append({
            'date': formatted_date,
            'url': url_for(".show_result", result_id=ocr_res.id)
        })
    return render_template("ocr/history.html", ocr_values=ocr_values)

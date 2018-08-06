from flask import request, redirect, url_for, render_template
from flask import Flask

from coreengine.converter import converter


app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('transliterator'))

@app.route('/transliterator/', methods=['GET', 'POST'])
def transliterator():
    query = None
    result = None
    text_result = None
    unicode_cp = None
    scrivener_option = None
    
    if request.method == "POST":
        query = request.form["text_input"]
        scrivener_option = request.form.get("scrivener_checkbox", "off")
        
        if scrivener_option == 'on':
            result = converter(query, True)
        else:
            result = converter(query)
        text_result = result[0]
        unicode_cp = result[1]
    
    else:
        pass
    
    return render_template('index.html', query=query, text_result=text_result, unicode_cp=unicode_cp)
#!flask/bin/python
import os, sys, commands
import traceback
import logging
import time
from crontab import CronTab
from PIL import Image
from flask import Flask, jsonify, request, redirect, url_for, send_from_directory, flash, render_template
from werkzeug import secure_filename

SIZE = (128, 128)
IMAGE_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(APP_ROOT, "upload_files")
commands.getoutput("mkdir -p " + UPLOAD_DIR)

#cron job creation
cron = CronTab(user='krishna',tab='True')
cmd = "/bin/rm " + UPLOAD_DIR + "/*"
job  = cron.new(cmd, comment='To clear the uploaded files')
job.minute.every(10)

#Starting the APP
my_app = Flask(__name__)
my_app.secret_key = 'krishna'
my_app.config['UPLOAD_DIR'] = UPLOAD_DIR

# create logging
logging.basicConfig(filename='app.log',
                    formate='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)


@my_app.errorhandler(410)
def not_found(error):
    return make_response(jsonify({'Error': 'File Not found'}), 404)


@my_app.errorhandler(400)
def wrong_formate(error):
    return make_response(jsonify({'Error': 'Wrong input data formate'}), 400)


def allowed_file(f_name):
    return '.' in f_name and \
           f_name.rsplit('.', 1)[1] in IMAGE_ALLOWED_EXTENSIONS


@my_app.route('/', methods=['GET', 'POST'])
def index():
    err_msg = ""
    if request.method == 'POST':
        if request.form['button'] == "Convert to Thumbnail":
            _file = request.files['image_file']
        elif request.form['button'] == "Convert to PDF":
            _file = request.files['text_file']
        if not _file:
            err_msg = "No file selected"
            flash(err_msg)
            return render_template('startup.html', error="error")
        f_name = secure_filename(_file.filename)
        _file.save(os.path.join(my_app.config['UPLOAD_DIR'], f_name))
        if request.form['button'] == "Convert to Thumbnail":
            if allowed_file(_file.filename):
                return redirect(url_for('convert', file_name=f_name,
                                conv_type="image"))
            else:
                err_msg = "File type should be an Image"
        elif request.form['button'] == "Convert to PDF":
            if ".pdf" not in _file.filename:
                return redirect(url_for('convert', file_name=f_name,
                                conv_type="pdf"))
            else:
                err_msg = "File type should not be PDF"
        flash(err_msg)
    return render_template('startup.html', error="error")


@my_app.route('/convert/<file_name>/<conv_type>')
def convert(file_name, conv_type):
    infile = os.path.join(UPLOAD_DIR, file_name)
    extension = os.path.splitext(infile)[1].strip(".")
    try:
        if conv_type == "image":
            outfile = os.path.splitext(infile)[0] +\
                      "_thumbnail"+ time.strftime("%y%m%d%H%M%S") +\
                      "."  + extension
            image = Image.open(infile)
            image.thumbnail(SIZE, Image.ANTIALIAS)
            if not extension or extension.lower() in "jpg":
                extension = "JPEG"
            image.save(outfile, extension.upper())
        elif conv_type == "pdf":
            outfile = os.path.splitext(infile)[0] +\
                      time.strftime("%y%m%d%H%M%S") +\
                      ".pdf"
            command = "wkhtmltopdf file://" + infile + " " + outfile 
            logging.info(command)
            status, output = commands.getstatusoutput(command)
            logging.info(output)
        return redirect(url_for('download',
                        file_name=os.path.basename(outfile)))
    except IOError:
        if conv_type == "image":
            err_msg = "cannot create thumbnail for '%s'\n" % infile
        elif conv_type == "pdf":
            err_msg = "cannot convert to PDF from '%s'\n" % infile
        logging.error(err_msg)
        logging.debug(traceback.format_exc())


@my_app.route('/download/<file_name>')
def download(file_name):
    return send_from_directory(my_app.config['UPLOAD_DIR'], 
                               file_name, as_attachment=True)


if __name__ == '__main__':
    my_app.run(host='0.0.0.0', debug=True)



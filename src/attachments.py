import os
import os.path
from flask import current_app

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getext(filename):
    return filename.rsplit(".", 1)[1].lower()

def handlefiles(files, resource, pkey):
    """ Save the files out of a request to a static file directory and returns a dict with a mapping of the files to
        their location on disk. """
    filepaths_dict = {}
    static_file_path = current_app.config['STATICFILEPATH']
    basedir = os.path.join(static_file_path, resource)
    if not os.path.isdir(basedir):
        os.mkdir(basedir)
    for column, file in files.items():
        ext = getext(file.filename)
        filepath = os.path.join(basedir, "{pkey}_{column}.{ext}".format(pkey=pkey,column=column,ext=ext))
        #Call to the requests file object save() method to save file to disk
        file.save(filepath)
        filepaths_dict[column] = filepath
    return filepaths_dict

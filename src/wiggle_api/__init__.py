import datetime
import glob
import os
import io
from pathlib import Path
import zipfile
from flask import Flask, Response, jsonify
from werkzeug.wsgi import FileWrapper

BASE_FOLDER = Path.home() / 'WiggleR'
IMG_FOLDER = f"{BASE_FOLDER}/Pictures"
VID_FOLDER = f"{BASE_FOLDER}/Videos"
ZIP_FOLDER = f"{BASE_FOLDER}/Zip"

def list_files(folder, path, extension):
    out = []
    for fileName in sorted(os.listdir(folder)):
        name, ext = os.path.splitext(fileName)
        if ext == extension:
            out.append({
                "name": name,
                "path": path + fileName
            })
    return out

def zipfiles(filenames, name):
    zip_subdir = "./"
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
        for fpath in filenames:
            _, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            temp_zip.write(fpath, zip_path)

    return Response(
        FileWrapper(zip_io),
        mimetype="application/x-zip-compressed",
        direct_passthrough=True,
        headers={"Content-Disposition": f"attachment; filename={name}.zip"}
    )

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/')
    def hello():
        return jsonify({"worm": 'Hello!'})
    
    # a simple page that says hello
    @app.route('/images')
    def images():
        files = list_files(IMG_FOLDER, '/image/', '.jpg')
        return jsonify(files)

    @app.route("/images/<string:date>", methods=['DELETE'])
    def delete_images(date):
        filePath = f"{IMG_FOLDER}/{date}*.jpg"
        os.system(f"rm {filePath}")
        return {"message": f"successfully deleted {filePath}"}

    @app.route("/videos", methods=['GET'])
    def videos():
        return list_files(VID_FOLDER, '/video/', '.mp4')

    @app.route("/videos/<string:date>", methods=['DELETE'])
    def delete_videos(date):
        filePath = f"{VID_FOLDER}/{date}*.jpg"
        os.system(f"rm {filePath}")
        return jsonify({"message": f"successfully deleted {filePath}"})

    @app.route("/zips", methods=['GET'])
    def zips():
        return list_files(ZIP_FOLDER, '/zip/', '.zip')

    @app.route("/zips/<string:date>", methods=['DELETE'])
    def delete_zip(date):
        filePath = f"{ZIP_FOLDER}/{date}*.jpg"
        os.system(f"rm {filePath}")
        return jsonify({"message": f"successfully deleted {filePath}"})
    
    @app.route("/images/zip/stream/<string:date>", methods=['GET'])
    def zip_stream(date):
        filenames = glob.glob(
            str(Path(__file__).parent / f"{IMG_FOLDER}/{date}*.jpg"))
        return zipfiles(filenames, date)

    @app.route("/images/zip/yesterday", methods=['GET'])
    def zip_yesterday():
        yesterday = (datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        os.system(
            f'zip -j {ZIP_FOLDER}/{yesterday} {IMG_FOLDER}/{yesterday}*.jpg')
        return {
            "name": yesterday,
            "path": f'/zip/{yesterday}.zip'
        }
    
    @app.route("/images/zip/<string:date>", methods=['GET'])
    def zip_based_on_date(date):
        os.system(f'zip -j {ZIP_FOLDER}/{date} {IMG_FOLDER}/{date}*.jpg')
        return {
            "name": date,
            "path": f'/zip/{date}.zip'
        }

    @app.route("/camera/picture", methods=['GET'])
    def take_picture():
        now = datetime.now()
        fileName = now.strftime("%Y-%m-%d-%H-%M")
        filePath = f"{IMG_FOLDER}/{fileName}.jpg"
        os.system(
            f"libcamera-jpeg --width 1024 --height 768 --nopreview -t 1 -o {filePath}")
        return {"picture": f"image/{fileName}.jpg"}

    @app.route("/light/on/<float:intensity>", methods=['GET'])
    def light(intensity=1):
        ...

    @app.route("/light/off", methods=['GET'])
    def lightOff():
        ...

    @app.route("/timelapse/yesterday", methods=['GET'])
    def timelapse_yesterday():
        yesterday = (datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        os.system(
            f'ffmpeg -framerate 30 -pattern_type glob -i "{IMG_FOLDER}/{yesterday}*.jpg" -s:v 1440x1080 -c:v libx264 -crf 17 -pix_fmt yuv420p {VID_FOLDER}/{yesterday}.mp4')
        return jsonify({
            "name": yesterday,
            "path": f'/video/{yesterday}.mp4'
        })

    @app.route("/timelapse/date/<string:date>", methods=['GET'])
    def timelapse_date(date):
        os.system(
            f'ffmpeg -framerate 30 -pattern_type glob -i "{IMG_FOLDER}/{date}*.jpg" -s:v 1440x1080 -c:v libx264 -crf 17 -pix_fmt yuv420p {VID_FOLDER}/{date}.mp4')
        return jsonify({
            "name": date,
            "path": f'/video/{date}.mp4'
        })

    return app
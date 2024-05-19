from datetime import datetime, timedelta
import glob
import os
import io
from pathlib import Path
import zipfile
from flask import Flask, Response, jsonify, Response, send_from_directory
import csv

BASE_FOLDER = Path.home() / "WiggleBin"
IMG_FOLDER = f"{BASE_FOLDER}/pictures"
VID_FOLDER = f"{BASE_FOLDER}/Videos"
ZIP_FOLDER = f"{BASE_FOLDER}/Zip"
DATA_FOLDER = BASE_FOLDER / "sensor-data"
BME_FILE = DATA_FOLDER / "bme680.csv"
SOIL_TEMPERATURE_FILE = DATA_FOLDER / "soil-temperature.csv"
WIGGLE_GATE_FILE = DATA_FOLDER / "wiggle-gate.csv"


def list_files(folder, path, extension):
    out = []
    for fileName in sorted(os.listdir(folder)):
        name, ext = os.path.splitext(fileName)
        if ext == extension:
            out.append({"name": name, "path": path + fileName})
    return out

def get_latest_file(dir):
    files = os.listdir(dir)
    files.sort()
    return os.path.join(dir, files[-1])


def zipfiles(filenames, name):
    zip_subdir = "./"
    zip_io = io.BytesIO()

    with zipfile.ZipFile(
        zip_io, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as temp_zip:
        for fpath in filenames:
            _, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            temp_zip.write(fpath, zip_path)

    zip_io.seek(0)

    response = Response(zip_io, mimetype="application/x-zip-compressed")
    response.headers["Content-Disposition"] = f"attachment; filename={name}.zip"
    return response


def read_last_row(file_path):
    try:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            last_row = None
            for row in reader:
                last_row = row
        return last_row
    except FileNotFoundError:
        return {"error": "File not found"}


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/latest-image')
    def latest_image():
        latest_img = get_latest_file(IMG_FOLDER)
        return send_from_directory(IMG_FOLDER, os.path.basename(latest_img))

    @app.route('/download-zip/<filename>')
    def download_zip(filename):
        return send_from_directory(ZIP_FOLDER, filename, as_attachment=True)

    # a simple page that says hello
    @app.route("/")
    def hello():
        return jsonify({"worm": "Hello!"})

    # Latest data from sensors
    @app.route("/sensors/")
    def sensors():
        data = {
            "bme": read_last_row(BME_FILE),
            "wiggle_gate": read_last_row(WIGGLE_GATE_FILE),
        }
        return jsonify(data)

    # BME sensor environment data
    @app.route("/sensors/bme")
    def environment():
        data = []
        try:
            with open(BME_FILE, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            return jsonify({"error": "File not found"})
        return jsonify(data)

    # Soil temperature sensor environment data
    @app.route("/sensors/soil-temperature")
    def soil_temperature():
        data = []
        try:
            with open(SOIL_TEMPERATURE_FILE, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            return jsonify({"error": "File not found"})
        return jsonify(data)

    # WiggleGate sensor
    @app.route("/sensors/wiggle-gate")
    def gate():
        data = []
        try:
            with open(WIGGLE_GATE_FILE, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            return jsonify({"error": "File not found"})
        return jsonify(data)

    # a simple page that says hello
    @app.route("/images")
    def images():
        files = list_files(IMG_FOLDER, "/image/", ".jpg")
        return jsonify(files)

    @app.route("/images/<string:date>", methods=["DELETE"])
    def delete_images(date):
        filePath = f"{IMG_FOLDER}/{date}*.jpg"
        os.system(f"rm {filePath}")
        return {"message": f"successfully deleted {filePath}"}

    @app.route("/videos", methods=["GET"])
    def videos():
        return list_files(VID_FOLDER, "/video/", ".mp4")

    @app.route("/videos/<string:date>", methods=["DELETE"])
    def delete_videos(date):
        filePath = f"{VID_FOLDER}/{date}*.jpg"
        os.system(f"rm {filePath}")
        return jsonify({"message": f"successfully deleted {filePath}"})

    @app.route("/zips", methods=["GET"])
    def zips():
        return list_files(ZIP_FOLDER, "/zip/", ".zip")

    @app.route("/zips/<string:date>", methods=["DELETE"])
    def delete_zip(date):
        filePath = f"{ZIP_FOLDER}/{date}*.jpg"
        os.system(f"rm {filePath}")
        return jsonify({"message": f"successfully deleted {filePath}"})

    @app.route("/images/zip/stream/<string:date>", methods=["GET"])
    def zip_stream(date):
        filenames = glob.glob(str(Path(__file__).parent / f"{IMG_FOLDER}/{date}*.jpg"))
        print(filenames)
        return zipfiles(filenames, date)

    @app.route("/images/zip/yesterday", methods=["GET"])
    def zip_yesterday():
        yesterday = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
        os.system(f"zip -j {ZIP_FOLDER}/{yesterday} {IMG_FOLDER}/{yesterday}*.jpg")
        return {"name": yesterday, "path": f"/zip/{yesterday}.zip"}

    @app.route("/images/zip/<string:date>", methods=["GET"])
    def zip_based_on_date(date):
        os.system(f"zip -j {ZIP_FOLDER}/{date} {IMG_FOLDER}/{date}*.jpg")
        return {"name": date, "path": f"/zip/{date}.zip"}

    @app.route("/camera/picture", methods=["GET"])
    def take_picture():
        now = datetime.now()
        fileName = now.strftime("%Y-%m-%d-%H-%M")
        filePath = f"{IMG_FOLDER}/{fileName}.jpg"
        os.system(
            f"libcamera-jpeg --width 1024 --height 768 --nopreview -t 1 -o {filePath}"
        )
        return {"picture": f"image/{fileName}.jpg"}

    @app.route("/light/on/<float:intensity>", methods=["GET"])
    def light(intensity=1): ...

    @app.route("/light/off", methods=["GET"])
    def lightOff(): ...

    @app.route("/timelapse/yesterday", methods=["GET"])
    def timelapse_yesterday():
        yesterday = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
        os.system(
            f'ffmpeg -framerate 30 -pattern_type glob -i "{IMG_FOLDER}/{yesterday}*.jpg" -s:v 1440x1080 -c:v libx264 -crf 17 -pix_fmt yuv420p {VID_FOLDER}/{yesterday}.mp4'
        )
        return jsonify({"name": yesterday, "path": f"/video/{yesterday}.mp4"})

    @app.route("/timelapse/date/<string:date>", methods=["GET"])
    def timelapse_date(date):
        os.system(
            f'ffmpeg -framerate 30 -pattern_type glob -i "{IMG_FOLDER}/{date}*.jpg" -s:v 1440x1080 -c:v libx264 -crf 17 -pix_fmt yuv420p {VID_FOLDER}/{date}.mp4'
        )
        return jsonify({"name": date, "path": f"/video/{date}.mp4"})

    return app

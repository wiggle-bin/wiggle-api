from . import create_app

app = create_app()


def run():
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    app.run(host="0.0.0.0")

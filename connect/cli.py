import importlib.resources
import subprocess


def main() -> None:
    app_path = importlib.resources.files('connect').joinpath('app.connect')
    subprocess.run(['connect', str(app_path)], check=True)


if __name__ == '__main__':
    main()

from src.app import create_app
import sys

def main():
    app = create_app()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

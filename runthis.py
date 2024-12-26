import os
import subprocess
import sys
import django
from django.core.management import call_command

def run_command(command, *args):
    try:
        subprocess.check_call([command] + list(args))
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command} {' '.join(args)}")
        sys.exit(1)

def create_virtualenv():
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        run_command("python", "-m", "venv", "venv")
    else:
        print("Virtual environment already exists.")

def install_requirements():
    if not os.path.exists("venv/lib/python3.8/site-packages"): 
        print("Installing requirements...")
        run_command("pip", "install", "-r", "requirements.txt")
    else:
        print("Dependencies are already installed.")

def run_migrations():
    if not os.path.exists("db.sqlite3"):
        print("Running migrations...")
        run_command("python", "manage.py", "migrate")
    else:
        print("Migrations already applied.")

def populate_data():
    if not os.path.exists("fake_data_populated.txt"):  # 
        print("Populating fake data...")
        run_command("python", "manage.py", "populate_data")  
        with open("fake_data_populated.txt", "w") as f:
            f.write("Data has been populated.")
    else:
        print("Fake data already populated.")

def start_server():
    print("Starting the server...")
    run_command("python", "manage.py", "runserver")

def main():
    """Main script to handle setup and run the project."""
    if not django.conf.settings.configured:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "falsecaller.settings")

    create_virtualenv()
    install_requirements()
    run_migrations()
    populate_data()
    start_server()

if __name__ == "__main__":
    main()

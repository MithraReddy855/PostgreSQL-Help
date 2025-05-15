PostgreSQL Help
This repository provides a lightweight Flask web application along with useful PostgreSQL command references and examples. It’s designed for developers, students, and anyone looking to learn or experiment with PostgreSQL through an interactive interface.

📚 Features
🧠 PostgreSQL command and query reference

🌐 Flask-based web interface
PostgreSQL Help
This repository provides a lightweight Flask web application along with useful PostgreSQL command references and examples. It’s designed for developers, students, and anyone looking to learn or experiment with PostgreSQL through an interactive interface.

📚 Features
🧠 PostgreSQL command and query reference

🌐 Flask-based web interface

⚙️ SQLAlchemy for database interaction

🧹 Web scraping utilities using BeautifulSoup

💾 Auto fallback to SQLite when PostgreSQL is not configured

🔁 Clone the Repository
Open your terminal and run:


git clone https://github.com/MithraReddy855/PostgreSQL-Help.git
cd PostgreSQL-Help
📦 Install Dependencies
Make sure you have Python 3.7+ installed.

(Optional) Create and activate a virtual environment
Linux/macOS:


python -m venv venv
source venv/bin/activate
Windows:


python -m venv venv
venv\Scripts\activate
Install required Python packages

pip install -r requirements.txt
requirements.txt


flask==3.1.1
flask_sqlalchemy==3.1.1
requests==2.32.3
bs4==0.0.2
beautifulsoup4==4.13.4

🏗️ Database Configuration
The app uses the following logic to configure the database:

python

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///postgresql_agent.db")
This means:

If the DATABASE_URL environment variable is set → it connects to PostgreSQL.

If not → it uses a local SQLite database (postgresql_agent.db).

🔧 To Use PostgreSQL:
Ensure your PostgreSQL server is running.

Create a database (e.g., mydb).

Set the environment variable before running the app:

Linux/macOS:


export DATABASE_URL=postgresql://username:password@localhost/mydb
Windows (Command Prompt):


set DATABASE_URL=postgresql://username:password@localhost/mydb
Replace username, password, and mydb with your actual PostgreSQL credentials.

🧪 To Use SQLite (Default Fallback):
If DATABASE_URL is not set, the app will automatically create and use a local SQLite file named postgresql_agent.db.

▶️ Run the Flask App
Set the Flask app environment variable:
Linux/macOS:


export FLASK_APP=app.py
Windows:


set FLASK_APP=app.py
Start the Flask server:

flask run
Visit the app in your browser at: http://127.0.0.1:5000

📁 Project Structure

.
├── app.py                   # Flask application
├── requirements.txt         # Python dependencies
├── templates/               # Jinja2 HTML templates
├── static/                  # Static assets (CSS/JS)
├── queries/                 # Optional SQL snippets or resources
└── README.md
🤝 Contributing
Have improvements, new examples, or bug fixes?
We welcome contributions! Just:

Fork the repo

Create a new branch

Make your changes

Submit a Pull Request ✅
⚙️ SQLAlchemy for database interaction

🧹 Web scraping utilities using BeautifulSoup

💾 Auto fallback to SQLite when PostgreSQL is not configured

🔁 Clone the Repository
Open your terminal and run:

git clone https://github.com/MithraReddy855/PostgreSQL-Help.git
cd PostgreSQL-Help

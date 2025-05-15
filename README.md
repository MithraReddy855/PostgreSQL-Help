<br/> <div align="center"> <a href="https://github.com/MithraReddy855/PostgreSQL-Help"> <img src="https://picsum.photos/400" alt="Logo" width="80" height="80"> </a> <h3 align="center">PostgreSQL Help</h3> <p align="center"> A lightweight Flask app to explore PostgreSQL commands with examples and built-in web interface. <br/> <br/> <a href="https://github.com/MithraReddy855/PostgreSQL-Help"><strong>Explore the docs »</strong></a> <br/> <br/> <a href="https://github.com/MithraReddy855/PostgreSQL-Help">View Demo</a> . <a href="https://github.com/MithraReddy855/PostgreSQL-Help/issues/new?labels=bug">Report Bug</a> . <a href="https://github.com/MithraReddy855/PostgreSQL-Help/issues/new?labels=enhancement">Request Feature</a> </p> </div>
📘 About The Project


PostgreSQL Help is a simple Flask-based web application that allows users to:

View and learn PostgreSQL commands and examples.

Use an interactive interface built with Flask.

Store queries and resources using SQLAlchemy ORM.

Run with PostgreSQL or fall back to SQLite with zero config.

Whether you're a beginner learning SQL or a dev needing a quick command reference — this app helps you get started fast.

🛠️ Built With
Flask

SQLAlchemy

BeautifulSoup

HTML/CSS (Jinja Templates)

PostgreSQL

🧑‍💻 Getting Started
Prerequisites
Python 3.7+
pip

📂 Clone the Repository

git clone https://github.com/MithraReddy855/PostgreSQL-Help.git
cd PostgreSQL-Help
📦 Install Dependencies
(Optional) create and activate a virtual environment:

Linux/macOS:


python -m venv venv
source venv/bin/activate
Windows:


python -m venv venv
venv\Scripts\activate
Then install the required packages:


pip install -r requirements.txt
⚙️ Configure the Database
By default, the app uses SQLite:


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///postgresql_agent.db")
If you want to use PostgreSQL:

Create a PostgreSQL database (e.g., mydb)

Export the database URL as an environment variable:

Linux/macOS:


export DATABASE_URL=postgresql://username:password@localhost/mydb
Windows (CMD):


set DATABASE_URL=postgresql://username:password@localhost/mydb
🚀 Run the Flask App
Set the Flask entry point:

Linux/macOS:


export FLASK_APP=app.py
Windows:


set FLASK_APP=app.py
Run the app:


flask run
Visit http://127.0.0.1:5000 in your browser.

💡 Usage
Use this app as a PostgreSQL learning guide and quick reference for:

DDL/DML commands

Query syntax examples

Copying tested commands quickly

You can also extend the app with your own query modules or interface.

🗺️ Roadmap
 Add SQLite fallback

 PostgreSQL dynamic connection

 Add command categorization by topic

 Enable query execution for sandbox DB

 User login for saving favorites

See the issues page for more.

🤝 Contributing
Contributions are welcome! 🎉

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

Star the repo ⭐ if it helped you — it motivates more updates!

📬 Contact
Mithra Reddy
GitHub
Email: your.email@example.com (replace with your real one)

Project Link: https://github.com/MithraReddy855/PostgreSQL-Help

🙏 Acknowledgments
ShaanCoding ReadME Generator

Best-README-Template by othneildrew

Flask Docs

PostgreSQL Docs

BeautifulSoup Docs

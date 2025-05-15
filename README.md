<br/>
<div align="center">
<a href="https://github.com/MithraReddy855/PostgreSQL-Help">
<img src="https://picsum.photos/400" alt="Logo" width="80" height="80">
</a>

<h3 align="center">PostgreSQL Help</h3>

<p align="center">
A lightweight Flask app to explore PostgreSQL commands with examples and built-in web interface.
<br/>
<br/>
<a href="https://github.com/MithraReddy855/PostgreSQL-Help"><strong>Explore the docs »</strong></a>
<br/>
<br/>
<a href="https://github.com/MithraReddy855/PostgreSQL-Help">View Demo</a>
.
<a href="https://github.com/MithraReddy855/PostgreSQL-Help/issues/new?labels=bug">Report Bug</a>
.
<a href="https://github.com/MithraReddy855/PostgreSQL-Help/issues/new?labels=enhancement">Request Feature</a>
</p>
</div>

---

## 📘 About The Project

![Screenshot](https://picsum.photos/1920/1080)

PostgreSQL Help is a simple Flask-based web application that allows users to:

- View and learn PostgreSQL commands and examples.
- Use an interactive interface built with Flask.
- Store queries and resources using SQLAlchemy ORM.
- Run with PostgreSQL or fall back to SQLite with zero config.

Whether you're a beginner learning SQL or a dev needing a quick command reference — this app helps you get started fast.

---

## 🛠️ Built With

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [HTML/CSS (Jinja Templates)](https://jinja.palletsprojects.com/)
- [PostgreSQL](https://www.postgresql.org/)

---

## 🧑‍💻 Getting Started

### Prerequisites

- Python 3.7+
- pip

---

### 📂 Clone the Repository

```bash
git clone https://github.com/MithraReddy855/PostgreSQL-Help.git
cd PostgreSQL-Help
```

---

### 📦 Install Dependencies

(Optional) create and activate a virtual environment:

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

Then install the required packages:

```bash
pip install -r requirements.txt
```

#### `requirements.txt`

```text
flask==3.1.1
flask_sqlalchemy==3.1.1
requests==2.32.3
bs4==0.0.2
beautifulsoup4==4.13.4
```

---

### ⚙️ Configure the Database

By default, the app uses SQLite:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///postgresql_agent.db")
```

If you want to use PostgreSQL:

1. Create a PostgreSQL database (e.g., `mydb`)
2. Export the database URL as an environment variable:

**Linux/macOS:**
```bash
export DATABASE_URL=postgresql://username:password@localhost/mydb
```

**Windows (CMD):**
```cmd
set DATABASE_URL=postgresql://username:password@localhost/mydb
```

---

### 🚀 Run the Flask App

Set the Flask entry point:

**Linux/macOS:**
```bash
export FLASK_APP=app.py
```

**Windows:**
```cmd
set FLASK_APP=app.py
```

Run the app:

```bash
flask run
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 💡 Usage

Use this app as a PostgreSQL learning guide and quick reference for:

- DDL/DML commands
- Query syntax examples
- Copying tested commands quickly

You can also extend the app with your own query modules or interface.

---

## 🗺️ Roadmap

- [x] Add SQLite fallback
- [x] PostgreSQL dynamic connection
- [ ] Add command categorization by topic
- [ ] Enable query execution for sandbox DB
- [ ] User login for saving favorites

See the [issues page](https://github.com/MithraReddy855/PostgreSQL-Help/issues) for more.

---

## 🤝 Contributing

Contributions are welcome! 🎉

1. Fork the Project  
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)  
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)  
4. Push to the Branch (`git push origin feature/AmazingFeature`)  
5. Open a Pull Request  

Star the repo ⭐ if it helped you — it motivates more updates!

---

## 📬 Contact

Mithra Reddy  
[GitHub](https://github.com/MithraReddy855)  
Email: your.email@example.com *(replace with your real one)*  

Project Link: [https://github.com/MithraReddy855/PostgreSQL-Help](https://github.com/MithraReddy855/PostgreSQL-Help)

---

## 🙏 Acknowledgments

- [ShaanCoding ReadME Generator](https://github.com/ShaanCoding/ReadME-Generator)
- [Best-README-Template by othneildrew](https://github.com/othneildrew/Best-README-Template)
- [Flask Docs](https://flask.palletsprojects.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

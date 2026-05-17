# CITS3403 Online Chess Website

### Purpose
The purpose of this application is to be a platform for users to play chess matches against other online players of a similar skill level. To do this we implement an 'elo' score system. Elo being a numerical value, wins increase a users elo score and vice versa. Users are matched to the user that is closest to them in elo. 

Users must create accounts to play so that their wins and loses can be kept track of for their elo score.

## Group Members

| UWA ID   | Name                   | GitHub Username          |
| :---     | :---                   | :---                     |
| 24227223 | Liam Bush              | JollyGreg                |
| 24183532 | Jinghao Hu             | jinghao163               |
| 23982486 | Charlotte Stevens      | charlotte239             |
| 24445737 | Muhammad Afridi Ismail | freddy_for_fun           |


## Launching the application

To run this application locally, please follow these steps to set up your virtual environment and install the required dependencies.

### 1. Prerequisites
Ensure you have **Python 3** installed on your system. 
*(Important for Windows users: Make sure to check "Add Python to PATH" during installation).*

### 2. Set up the Virtual Environment
Open your terminal in the root directory of the project and run:
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
Activate the environment based on your operating system:
Windows (PowerShell):
```powershell
.\venv\Scripts\activate
```
(Note: If you encounter an execution policy error on Windows, run Set-ExecutionPolicy Unrestricted -Scope CurrentUser first).
Mac / Linux:
```bash
source venv/bin/activate
```
### 4. Install Dependencies
Once the virtual environment is activated (you should see (venv) in your terminal), install the required packages:
```bash
pip install -r requirements.txt
```
### 5. Initialize the Database
Before running the application, you must initialize the database:
```bash
python db.py
```
### 5. Run the Application
Start the Flask local development server:
```bash
python -m flask run --debug
```
The application will be running at http://127.0.0.1:5000/.

## Running the Tests

The project includes a comprehensive test suite with over 15 tests, covering both unit logic and end-to-end UI automation as required.

### 1. Prerequisite: Ensure Test Dependencies are Installed
The testing suite requires `pytest`, `selenium`, and `webdriver-manager`. If you haven't installed them yet, ensure your virtual environment is activated and run:
```bash
pip install -r requirements.txt
```
## 2. Running Tests
Run all tests
To execute the entire test suite (Unit tests + Selenium tests), run the following command from the project root:

```Bash
pytest tests/ -v
```
Run individual tests
```bash
pytest tests/test_model.py -v
pytest tests/test_routes.py -v
pytest tests/test_security.py -v
pytest tests/test_selenium.py -v
```


## 3. Test Suite Breakdown
Unit Tests: Located in test_model.py, test_routes.py, and test_security.py. These verify database integrity, password hashing, and route protection.

Selenium Tests: Located in test_selenium.py. These run against a live version of the server (automatically handled by the live_server fixture in conftest.py) to verify UI components like modals and login flows.

Note: Selenium tests run in headless mode by default, so no browser window will pop up during the automated process.

## Main Features

### Home Page & Leaderboard
The home page dynamically changes based on user authentication. Guests are greeted with a login/registration modal, while logged-in users see their personalized win-rate statistics and a quick-match launcher. The right column displays a real-time Global Leaderboard based on ELO ratings.

### Game Mode & Lobby
* **Matchmaking:** Users can create a new game room or join an existing one waiting for an opponent.
* **Real-time Gameplay:** The board is synchronized in real-time using WebSockets. 
* **Move Validation:** Double validation ensures chess rules are strictly followed (both locally and on the server side).
* **In-Game Chat:** A floating chatbox allows real-time communication between opponents during a match.

### User Dashboard (Profile)
Logged-in users can view their comprehensive match history, showing dates, opponents, playing color, ELO changes, and match results. 

---

## How The Website Works

The project uses a strict Client-Server architecture. Flask connects the frontend Jinja templates with backend REST APIs and WebSocket events.

HTML pages are stored in the `templates` folder and rely on Jinja2 for dynamic data rendering. A responsive layout is built utilizing Bootstrap 5. Forms are processed securely via Flask-WTF, utilizing CSRF tokens and secure password hashing. 

Real-time interaction (chatting and making moves) is handled via `Flask-SocketIO`, enabling instant bidirectional communication between the client and the server. SQLAlchemy acts as the ORM, securely storing user accounts, match histories, and chat logs in a local SQLite database.

---

## Tools and Libraries Used

* **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-SocketIO
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5
* **Database:** SQLite
* **Testing:** Pytest, Selenium, Webdriver Manager

---


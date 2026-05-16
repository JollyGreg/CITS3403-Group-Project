# CITS3402 Online Chess Website

### Purpose
The purpose of this application is to be a platform for users to play chess matches against other online players of a similar skill level. To do this we implement an 'elo' score system. Elo being a numerical value, wins increase a users elo score and vice versa. Users are matched to the user that is closest to them in elo. 

Users must create accounts to play so that their wins and loses can be kept track of for their elo score.

### Group members
- 24227223 - Liam Bush - "JollyGreg"
- 24183532 - Jinghao Hu - "jinghao163"
- 23982486 - Charlotte Stevens - "charlotte239"
- 24445737 - Muhammad Afridi Ismail - "MUHAMMAD AFRIDI ISMAIL", "freddy_for_fun"


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
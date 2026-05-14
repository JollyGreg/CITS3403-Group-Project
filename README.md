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

### Running the applcation NEED TO ADD
instructions for how to run the tests for the application.

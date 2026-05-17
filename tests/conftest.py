import sys
import os
# Add the project root to the Python path so pytest can find 'app' and 'models'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from models import User

# ==========================================
# Unit Tests Shared Fixtures
# ==========================================

@pytest.fixture
def app():
    """Create a Flask instance for testing using an in-memory database."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False # Disable CSRF during testing to easily simulate form submissions
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Provide a test client to simulate sending GET/POST requests."""
    return app.test_client()


# ==========================================
# Selenium (UI Tests) Shared Fixtures
# ==========================================

@pytest.fixture(scope="module")
def live_server():
    """Start a live Flask server in a background thread for Selenium to access."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost:5000"
    })

    with app.app_context():
        db.create_all()
        # Pre-create a test user in the database for subsequent login tests
        user = User(username="selenium_user", email="sel@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()

    # Run Flask in a new background thread
    server_thread = threading.Thread(target=app.run, kwargs={'port': 5000, 'use_reloader': False})
    server_thread.daemon = True
    server_thread.start()
    
    # Pause for 1 second to ensure the server is fully started
    time.sleep(1)
    
    # Yield the server URL to the test cases
    yield "http://localhost:5000"
    
    # Clean up the in-memory database after testing is complete
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope="module")
def browser():
    """Configure and start the Selenium Chrome browser (headless mode)."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Headless mode: run without a visible browser window
    options.add_argument('--disable-gpu')
    
    # Automatically download and match the WebDriver for the current Chrome version
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield driver
    
    # Close the browser after testing is complete
    driver.quit()
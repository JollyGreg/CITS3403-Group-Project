# tests/test_selenium.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_homepage_title(live_server, browser):
    """
    Selenium Test 1: Verify the browser loads the live server and 
    displays the correct HTML title.
    """
    browser.get(live_server)
    assert "Chess Master" in browser.title


def test_login_modal_opens(live_server, browser):
    """
    Selenium Test 2: Verify that clicking the 'Login' button triggers 
    the JavaScript function to display the modal overlay.
    """
    browser.get(live_server)
    
    # Find and click the login button in the navbar
    login_btn = browser.find_element(By.CSS_SELECTOR, "button.btn-login")
    login_btn.click()
    
    # Wait for the modal to become visible
    modal = WebDriverWait(browser, 3).until(
        EC.visibility_of_element_located((By.ID, "loginModal"))
    )
    assert modal.is_displayed()


def test_modal_tab_switching(live_server, browser):
    """
    Selenium Test 3: Verify the JavaScript tab switching logic inside 
    the authentication modal (Login <-> Register).
    """
    browser.get(live_server)
    browser.find_element(By.CSS_SELECTOR, "button.btn-login").click()
    
    # Wait for modal then click the 'Register' tab
    WebDriverWait(browser, 3).until(EC.visibility_of_element_located((By.ID, "loginModal")))
    register_tab = browser.find_element(By.ID, "tab-register")
    register_tab.click()
    
    # Verify the register form becomes active and login form becomes inactive
    register_form = browser.find_element(By.ID, "registerForm")
    login_form = browser.find_element(By.ID, "loginForm")
    
    assert "active" in register_form.get_attribute("class")
    assert "active" not in login_form.get_attribute("class")


def test_quick_match_unauthenticated(live_server, browser):
    """
    Selenium Test 4: Verify that clicking the 'Quick Match' button while
    logged out prompts the user with the login modal.
    """
    browser.get(live_server)
    
    # Click the large quick match button
    quick_match_btn = browser.find_element(By.CSS_SELECTOR, "button.quick-match-btn")
    quick_match_btn.click()
    
    # Wait for the modal to pop up
    modal = WebDriverWait(browser, 3).until(
        EC.visibility_of_element_located((By.ID, "loginModal"))
    )
    assert modal.is_displayed()


def test_user_login_flow(live_server, browser):
    """
    Selenium Test 5: Verify an end-to-end user login flow.
    The 'selenium_user' is pre-created by the live_server fixture in conftest.py.
    """
    browser.get(live_server)
    
    # Open modal
    browser.find_element(By.CSS_SELECTOR, "button.btn-login").click()
    WebDriverWait(browser, 3).until(EC.visibility_of_element_located((By.ID, "loginModal")))
    
    # Locate form inputs
    form = browser.find_element(By.ID, "loginForm")
    username_input = form.find_element(By.NAME, "username")
    password_input = form.find_element(By.NAME, "password")
    
    # Input credentials
    username_input.send_keys("selenium_user")
    password_input.send_keys("123456")
    
    # Submit the form
    submit_btn = form.find_element(By.CSS_SELECTOR, "button.submit-btn")
    submit_btn.click()
    
    # Wait for page reload and verify the user's name appears on the page
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'selenium_user')]"))
    )
    
    body_text = browser.find_element(By.TAG_NAME, "body").text
    assert "selenium_user" in body_text
    assert "Logout" in body_text
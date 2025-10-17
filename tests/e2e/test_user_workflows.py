"""
End-to-end tests using browser automation
"""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

class TestUserWorkflows:
    """Browser-based end-to-end tests."""
    
    @pytest.fixture
    def driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def app_url(self):
        return "http://localhost:3000"
    
    def test_upload_and_visualize_netlist(self, driver, app_url):
        """Test complete user workflow: upload -> visualize -> validate."""
        driver.get(app_url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Create test netlist file
        test_netlist = {
            "components": [
                {"id": "U1", "type": "IC", "pins": ["1", "2", "3", "4"]},
                {"id": "R1", "type": "RESISTOR", "pins": ["1", "2"]}
            ],
            "nets": [
                {"id": "VCC", "connections": [{"component": "U1", "pin": "1"}]},
                {"id": "GND", "connections": [
                    {"component": "U1", "pin": "4"},
                    {"component": "R1", "pin": "2"}
                ]}
            ]
        }
        
        # Find file upload element
        file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        
        # Create temporary file
        with open('/tmp/test_netlist.json', 'w') as f:
            json.dump(test_netlist, f)
        
        # Upload file
        file_input.send_keys('/tmp/test_netlist.json')
        
        # Wait for visualization to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="netlist-visualization"]'))
        )
        
        # Verify components are displayed
        assert "U1" in driver.page_source
        assert "R1" in driver.page_source
        
        # Clean up
        os.remove('/tmp/test_netlist.json')
    
    def test_validation_results_display(self, driver, app_url):
        """Test that validation results are properly displayed."""
        driver.get(app_url)
        
        # Upload invalid netlist
        invalid_netlist = {
            "components": [
                {"id": "", "type": "IC", "pins": ["1", "2"]}  # Blank name
            ],
            "nets": []
        }
        
        with open('/tmp/invalid_netlist.json', 'w') as f:
            json.dump(invalid_netlist, f)
        
        file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        file_input.send_keys('/tmp/invalid_netlist.json')
        
        # Wait for validation results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="validation-results"]'))
        )
        
        # Verify error messages are displayed
        assert "error" in driver.page_source.lower() or "invalid" in driver.page_source.lower()
        
        # Clean up
        os.remove('/tmp/invalid_netlist.json')

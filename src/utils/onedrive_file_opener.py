import requests, shlex
from pathlib import Path
from .onedrive_auth import OneDriveAuth
from .shared import load_env_vars, show_zenity_error, open_in_browser

class OneDriveFileOpener:
    """Handles opening OneDrive files in the browser with authentication"""
    
    def __init__(self):
        """Initialize the OneDrive file opener with configuration"""
        self.env_vars = load_env_vars()
        self.token = self.env_vars.get("ACCESS_TOKEN", "")
        self.onedrive_root = Path(self.env_vars.get("ONEDRIVE_ROOT", str(Path.home() / "OneDrive")))
        self.browser_path = self.env_vars.get("BROWSER_PATH", "/usr/bin/chromium-browser")
        self.api_base_url = "https://graph.microsoft.com/v1.0/me"
        
        # Parse browser command with arguments
        self.browser_cmd = shlex.split(self.browser_path)
        self.onedrive_auth = OneDriveAuth()
    
    def sanitize_path(self, file_path):
        """Convert local file path to OneDrive API path"""
        try:
            relative_path = str(Path(file_path).expanduser().resolve().relative_to(self.onedrive_root))
            encoded_path = requests.utils.quote(relative_path.replace("\\", "/"))
            return f"/drive/root:/{encoded_path}:"
        except ValueError as e:
            raise Exception(f"File must be within OneDrive directory: {e}")
    
    def make_api_request(self, file_path, token):
        """Make API request to get file information"""
        api_path = self.sanitize_path(file_path)
        url = f"{self.api_base_url}{api_path}"
        headers = {"Authorization": f"bearer {token}"}
        
        response = requests.get(url, headers=headers)
        return response
    
    def handle_authentication_error(self, file_path):
        """Handle 401 authentication error by refreshing token and retrying"""
        new_token = self.onedrive_auth.handle_401_error()
        if not new_token:
            raise Exception("Failed to authenticate with OneDrive")
        
        # Retry with new token
        response = self.make_api_request(file_path, new_token)
        return response, new_token
    
    def open_file(self, file_path):
        """Main method to open a OneDrive file in the browser"""
        try:
            # Make initial API request
            response = self.make_api_request(file_path, self.token)
            
            # Handle authentication error
            if response.status_code == 401:
                response, _ = self.handle_authentication_error(file_path)
            
            # Check for other errors
            response.raise_for_status()
            
            # Get web URL and open in browser
            file_data = response.json()
            web_url = file_data.get("webUrl")
            
            if not web_url:
                raise Exception("No web URL found for this file")
            
            open_in_browser(self.browser_cmd, web_url)
            
        except Exception as e:
            show_zenity_error(str(e))
            return False
        
        return True

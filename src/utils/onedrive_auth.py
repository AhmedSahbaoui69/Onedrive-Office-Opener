import requests, subprocess, shlex
from urllib.parse import urlparse, parse_qs
from .shared import send_notify_info, show_zenity_error, load_env_vars, get_env_file_path, open_in_browser

class OneDriveAuth:
    """Handles Microsoft OneDrive OAuth2 authentication and token management"""

    CLIENT_ID = "d50ca740-c83f-4d1b-b616-12c519384f0c"
    REDIRECT_URI = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    SCOPE = "Files.ReadWrite Files.ReadWrite.All Sites.ReadWrite.All offline_access"
    AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    def __init__(self):
        self.env_vars = load_env_vars()
        self.browser_path = self.env_vars.get("BROWSER_PATH", "/usr/bin/chromium-browser")
        self.browser_cmd = shlex.split(self.browser_path)

    def get_auth_url(self):
        """Generate the authorization URL"""
        params = {
            'client_id': self.CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': self.REDIRECT_URI,
            'scope': self.SCOPE,
            'prompt': 'login'
        }
        q = '&'.join([f"{k}={requests.utils.quote(v)}" for k,v in params.items()])
        return f"{self.AUTH_URL}?{q}"

    def exchange_code_for_tokens(self, auth_code):
        """Exchange authorization code for tokens"""
        data = {
            'client_id': self.CLIENT_ID,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.REDIRECT_URI,
            'scope': self.SCOPE
        }
        r = requests.post(self.TOKEN_URL, data=data); r.raise_for_status()
        t = r.json(); return t['access_token'], t['refresh_token']

    def refresh_access_token(self, refresh_token):
        """Use refresh token to get a new access token"""
        try:
            r = requests.post(self.TOKEN_URL, data={'client_id': self.CLIENT_ID,'grant_type': 'refresh_token','refresh_token': refresh_token})
            r.raise_for_status(); t = r.json()
            a, r_new = t['access_token'], t.get('refresh_token', refresh_token)
            self.save_tokens_to_env(a, r_new); return a, r_new
        except requests.exceptions.RequestException as e:
            show_zenity_error(f"Failed to refresh token: {e}"); return None, None

    def authenticate_user(self):
        """Complete OAuth2 authentication flow"""
        try:
            url = self.get_auth_url()
            send_notify_info(f"Please visit this URL to authenticate:\n\n{url}\n\nPaste the redirect URL in the next dialog.")
            open_in_browser(self.browser_cmd, url)
            redirect_url = subprocess.run(["zenity","--entry","--text=Paste the full redirect URL here:"],capture_output=True,text=True).stdout.strip()
            if not redirect_url: return None, None
            q = parse_qs(urlparse(redirect_url).query)
            if 'code' not in q: show_zenity_error("No authorization code found in URL"); return None, None
            a, r = self.exchange_code_for_tokens(q['code'][0]); self.save_tokens_to_env(a, r); return a, r
        except Exception as e:
            show_zenity_error(f"Authentication failed: {e}"); return None, None

    def handle_401_error(self):
        """Handle 401 Unauthorized error by attempting token refresh or re-authentication"""
        rt = self.env_vars.get("REFRESH_TOKEN")
        if rt:
            send_notify_info("Access token expired. Refreshing...")
            a, r = self.refresh_access_token(rt)
            if a: return a
        send_notify_info("Refresh failed. Re-authenticating...")
        a, r = self.authenticate_user(); return a

    def get_valid_token(self):
        """Get a valid access token, refreshing or re-authenticating if needed"""
        t = self.env_vars.get("ACCESS_TOKEN")
        if not t: send_notify_info("No token found. Authenticating...");
        t,_ = self.authenticate_user()
        return t

    def save_tokens_to_env(self, a, r):
        """Save tokens to .env file"""
        env_file, env_vars = get_env_file_path(), load_env_vars()
        env_vars["ACCESS_TOKEN"], env_vars["REFRESH_TOKEN"] = a, r
        with open(env_file,'w') as f: [f.write(f'{k}="{v}"\n') for k,v in env_vars.items()]
        send_notify_info(f"Tokens saved!\n\n<b>Access Token: {a[:10]}...</b>\n<b>Refresh Token: {r[:10]}...</b>")
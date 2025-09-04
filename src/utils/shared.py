import subprocess
from pathlib import Path


def show_zenity_info(message):
    """Show info dialog using zenity"""
    subprocess.run(
        ["zenity", "--info", f"--text={message}", "--width=400", "2>/dev/null"], 
        stderr=subprocess.DEVNULL, 
        check=False
    )
    print(message)


def show_zenity_error(message):
    """Show error dialog using zenity"""
    subprocess.run(
        ["zenity", "--error", f"--text={message}", "--width=400", "2>/dev/null"], 
        stderr=subprocess.DEVNULL, 
        check=False
    )
    print(f"Error: {message}")


def get_env_file_path():
    """Get the path to the .env file"""
    # Go up two levels from src/utils to reach the project root
    return Path(__file__).parent.parent.parent / ".env"


def load_env_vars():
    """Load environment variables from .env file"""
    env_file = get_env_file_path()
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"').strip("'")
    
    return env_vars

def open_in_browser(browser_cmd, web_url):
    """Open the file URL in the browser"""
    try:
        subprocess.run([*browser_cmd, web_url], check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to open browser: {e}")
    except FileNotFoundError:
        raise Exception(f"Browser not found: {browser_cmd[0]}")

# OneDrive File Opener 

This script allows you to open OneDrive files directly in your browser from the command line, with automatic OAuth2 authentication handling.

## Features

- **Automatic Token Management**: Handles access token refresh automatically
- **Seamless Re-authentication**: If tokens expire, it will guide you through re-authentication using your browser
- **Environment Configuration**: All settings stored in `.env` file

## Requirements
- `zenity` - For error dialogs
- [OneDrive client by abraunegg](https://github.com/abraunegg/onedrive) - For OneDrive synchronization
- Python 3 with `requests` library

## Setup

1. **Set up OneDrive client**  
   Follow the instructions at [abraunegg/onedrive](https://github.com/abraunegg/onedrive#installation) to install and configure the OneDrive client for your system.

2. **Create your `.env` file**  
   Copy `.env.example` to `.env` and fill in your configuration values:
   - `ONEDRIVE_ROOT`: Path to your local OneDrive folder
   - `BROWSER_PATH`: Path to your preferred browser

## Usage

```bash
python src/main.py <file_path>
```

Where `<file_path>` is the absolute path to the file inside your OneDrive directory.

## OPTIONAL: Create a desktop entry
You can create a desktop entry to integrate this script with your file manager, allowing you to open files directly from your desktop environment. 

For example, create a file like `office365.desktop` in `~/.local/share/applications/` with the following content:

```
[Desktop Entry]
Name=Office 365
Comment=Open selected file in OneDrive web
Exec=/usr/bin/python3 /home/hmed/Documents/open_in_office/src/main.py %f
Icon=folder-remote
Terminal=false
Type=Application
MimeType=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.ms-excel;application/vnd.openxmlformats-officedocument.wordprocessingml.document;application/msword;application/pdf;
NoDisplay=false
```

This will add "Office 365" as an option in your file manager's context menu for supported file types.

## Lisence
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
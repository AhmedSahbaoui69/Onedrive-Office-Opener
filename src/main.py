from utils.onedrive_file_opener import OneDriveFileOpener
import sys

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_inside_OneDrive>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    opener = OneDriveFileOpener()
    
    success = opener.open_file(file_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

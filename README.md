# Instagram Reels Scraper

A professional Instagram Reels scraper with a modern GUI that extracts view counts, captions, likes, and dates from Instagram Reels. Built with Python, Selenium, and Tkinter.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-v4.15+-green.svg)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

### Dual Scraping Methods
- **By Scrolls**: Traditional scroll-based scraping (0-20 scrolls)
- **By Posts Count**: Target specific number of posts (1-100 posts)

### Data Extraction
- **View counts** with automatic formatting (K, M, B)
- **Post captions** with full text extraction
- **Likes count** with numerical conversion
- **Post dates** with various format support
- **Reel URLs** for reference

### Auto-Conversion
- **Excel (.xlsx)** format with formatted columns
- **CSV** format for data analysis
- **JSON** raw data storage

### Professional GUI
- **Real-time logging** with status indicators
- **Progress tracking** with live updates
- **File management** with recent files view
- **Settings persistence** across sessions
- **Responsive design** with scrollable interface

### Advanced Features
- **Headless mode** support
- **Debug mode** for troubleshooting
- **Duplicate detection** and removal
- **Error handling** with detailed logging
- **Thread-safe** operations

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed
- Active internet connection

### Installation

1. **Download** the project files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run with batch file** (Recommended):
   ```bash
   run_scraper.bat
   ```
   Or run directly:
   ```bash
   python main_gui.py
   ```

### ChromeDriver Setup

The application automatically downloads ChromeDriver when needed. However, if you encounter download errors (common with corporate networks/firewalls), you'll need to install ChromeDriver manually:

#### Automatic Setup (Default)
The scraper automatically downloads and manages ChromeDriver. This works for most users with normal internet connections.

#### Manual Setup (If automatic download fails)
If you see errors like "Could not reach host" or "ChromeDriver download failed":

1. **Check your Chrome version**:
   - Open Chrome browser
   - Go to: `chrome://version/`
   - Note the version number (e.g., `120.0.6099.109`)

2. **Download ChromeDriver**:
   - Go to: https://chromedriver.chromium.org/downloads
   - Find the section matching your Chrome version
   - Download `chromedriver_win32.zip` for Windows

3. **Install ChromeDriver**:
   - Extract the zip file
   - Copy `chromedriver.exe` from the extracted folder
   - **Place it in the same folder as this scraper** (where `main_gui.py` is located)
   - The file structure should look like:
     ```
     Instagram_Reels_Scraper/
     ├── main_gui.py
     ├── InstagramScraper.py
     ├── chromedriver.exe          ← Place here
     └── requirements.txt
     ```

4. **Restart the application**:
   - The scraper will automatically detect and use the local ChromeDriver
   - No internet connection needed for ChromeDriver after this!

#### Alternative Installation (System-wide)
Advanced users can install ChromeDriver system-wide:
- Copy `chromedriver.exe` to `C:\Windows\System32\`
- Or add ChromeDriver folder to Windows PATH environment variable

#### Verification
After manual installation, you should see:
```
✅ Local ChromeDriver found and initialized successfully
```

### Easy Launch Options

#### Option 1: Using Batch File (Recommended)
Double-click `run_scraper.bat` - it will automatically:
- Find Python installation (Anaconda, Python, py launcher)
- Check and install required packages
- Handle ChromeDriver setup (automatic or guide for manual)
- Launch the application

#### Option 2: Direct Python Command
```bash
python main_gui.py
```

#### Option 3: Using Anaconda
```bash
conda activate base
python main_gui.py
```

## Usage Guide

### Basic Workflow

1. **Launch** the application using `run_scraper.bat` or `python main_gui.py`
2. **Enter** target Instagram username (without @ symbol)
3. **Choose scraping method**:
   - **By Scrolls**: Set number of scrolls (good for exploring)
   - **By Posts Count**: Set target number of posts (precise control)
4. **Configure settings** as needed
5. **Click "Start Scraping"**
6. **Login** to Instagram when browser opens
7. **Wait** for completion and check results

### Scraping Methods

#### By Scrolls
- Scrolls down the page a fixed number of times
- Good for discovering content
- Range: 0-20 scrolls
- Variable results depending on content density

#### By Posts Count
- Targets a specific number of posts
- Precise control over data volume
- Range: 1-100 posts
- Stops exactly when target is reached

### Settings Explained

| Setting | Description | Recommended |
|---------|-------------|-------------|
| **Extract captions** | Fetch full post captions | Enabled |
| **Extract likes & dates** | Get engagement data | Enabled |
| **Headless mode** | Hide browser window | Disabled for first use |
| **Debug mode** | Verbose logging | Only for troubleshooting |
| **Auto-convert Excel** | Generate .xlsx files | Enabled |
| **Auto-convert CSV** | Generate .csv files | Enabled |

## Output Files

### File Naming Convention
```
instagram_reels_data_[username]_[timestamp].json
instagram_reels_data_[username]_[timestamp].xlsx
instagram_reels_data_[username]_[timestamp].csv
```

### Data Structure
```json
{
  "views": "1.2M",
  "url": "https://instagram.com/reel/ABC123",
  "reel_index": 1,
  "caption": "Sample caption text...",
  "likes": "45.6K",
  "post_date": "2024-01-15",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Technical Details

### Project Structure
```
Scraper/
├── main_gui.py                    # GUI interface and control logic
├── InstagramScraper.py            # Core scraping engine
├── InstagramDataConverter.py      # Data processing and export
├── requirements.txt               # Dependencies
├── run_scraper.bat               # Auto-launcher script
└── README.md                     # This file
```

### Dependencies
- **selenium**: Web automation and scraping
- **webdriver-manager**: Automatic ChromeDriver management
- **pandas**: Data processing and manipulation
- **openpyxl**: Excel file generation
- **python-dateutil**: Date parsing and formatting

### Browser Requirements
- **Chrome browser** (latest version recommended)
- **ChromeDriver** (automatically managed by webdriver-manager)

## Configuration

### Default Settings
```python
# Scraping
DEFAULT_SCROLLS = 3
DEFAULT_TARGET_POSTS = 20
DEFAULT_DELAY = 3  # seconds

# Data Extraction
EXTRACT_CAPTIONS = True
EXTRACT_LIKES_DATES = True

# Export
AUTO_CONVERT_EXCEL = True
AUTO_CONVERT_CSV = True
```

### Advanced Configuration
- Modify scraping delays in `InstagramScraper.py`
- Customize data formatting in `InstagramDataConverter.py`
- Adjust GUI layout in `main_gui.py`

## Troubleshooting

### Common Issues

#### ChromeDriver Download Issues
```
❌ Automatic ChromeDriver setup failed: Could not reach host. Are you offline?
❌ All ChromeDriver download strategies failed!
```
**Cause**: Usually occurs with corporate networks, firewalls, or proxy settings blocking the download.

**Solutions**:
1. **Manual Installation** (Recommended):
   - Check Chrome version: `chrome://version/`
   - Download from: https://chromedriver.chromium.org/downloads
   - Place `chromedriver.exe` in the scraper folder
   - Restart the application

2. **Network Solutions**:
   - Try different network (mobile hotspot)
   - Contact IT support for proxy/firewall settings
   - Run as Administrator
   - Temporarily disable antivirus

3. **Alternative**:
   - Download ChromeDriver at home/personal network
   - Transfer `chromedriver.exe` to work computer
   - Place in scraper folder

#### Python Installation Issues
```
ERROR: No Python installation found!
```
**Solutions**:
- Install Python from https://www.python.org/downloads/
- Install Anaconda from https://www.anaconda.com/download
- Ensure Python is added to PATH during installation
- Try running `run_scraper.bat` which auto-detects Python

#### Package Installation Issues
```
[MISSING] selenium - not installed
```
**Solutions**:
- Run `run_scraper.bat` and select "y" when prompted to install packages
- Manually install: `pip install selenium webdriver-manager pandas openpyxl python-dateutil`
- Check if you have pip installed: `python -m pip --version`

#### Browser/Driver Issues
```
Failed to setup Chrome driver
```
**Solutions**:
- Update Chrome browser to latest version
- Clear browser cache and cookies
- Close all Chrome instances before running
- Check if Chrome is installed in default location
- **Try manual ChromeDriver installation** (see ChromeDriver Setup section)

#### Login Issues
```
Login failed or timed out
```
**Solutions**:
- Disable 2FA temporarily
- Use app-specific password
- Clear Instagram cookies
- Try different account
- Ensure stable internet connection

#### No Data Found
```
No reels found or scraping failed
```
**Solutions**:
- Check if profile is public
- Verify username spelling (without @ symbol)
- Try lower scroll count or posts count
- Enable debug mode for detailed logs
- Check if account has reels posted

#### Import Errors
```
Error importing modules
```
**Solutions**:
- Ensure all files are in the same directory:
  ```
  Scraper/
  ├── main_gui.py
  ├── InstagramScraper.py
  ├── InstagramDataConverter.py
  └── requirements.txt
  ```
- Run from the correct directory
- Check file permissions

#### File Path Issues (Windows)
```
main_gui.py not found
```
**Solutions**:
- Avoid folder names with special characters (!, @, #)
- Use `run_scraper.bat` which handles path issues automatically
- Ensure batch file is in same folder as Python files

### Debug Mode
Enable debug mode for detailed logging:
1. Check "Debug mode" in settings
2. Look for detailed error messages in log
3. Check browser developer console if needed

### Getting Verbose Output
The batch launcher (`run_scraper.bat`) provides detailed output including:
- Python installation detection
- Package installation status
- Error diagnostics
- Step-by-step progress

## Performance Tips

### For Better Results
- **Use public profiles** (private profiles require following)
- **Start with small numbers** (5-10 posts/scrolls for testing)
- **Stable internet** connection recommended
- **Close other browser instances** to avoid conflicts
- **Use wired connection** instead of WiFi for large extractions

### Rate Limiting
- Default 3-second delay between actions
- Increase delay for large extractions
- Use headless mode for background operation
- Monitor for Instagram rate limiting warnings

### Memory Usage
- Close other applications when scraping large amounts
- Use posts count method for better memory management
- Restart application periodically for long sessions

## Legal & Ethical Usage

### Guidelines
- **Respect robots.txt** and Instagram's terms of service
- **Use for research/analysis** purposes only
- **Rate limit** your requests appropriately
- **Public data only** - don't scrape private profiles without permission
- **Respect privacy** - don't scrape personal information

### Disclaimer
This tool is for educational and research purposes only. Users are responsible for complying with Instagram's Terms of Service and applicable laws. The developers are not responsible for any misuse of this software.

## Support

### Getting Help
1. Check the troubleshooting section above
2. Enable debug mode for detailed error messages
3. Review the logs in the GUI for specific error details
4. Use `run_scraper.bat` for automatic diagnostics

### Feature Requests
- Open an issue describing the desired feature
- Include use case and expected behavior
- Consider contributing the implementation

## Version History

### v1.0.0 (Current)
- Dual scraping methods (scrolls vs posts count)
- Professional GUI with real-time logging
- Auto-conversion to Excel/CSV
- Comprehensive data extraction
- Error handling and debugging features
- Auto-launcher batch file with Python detection
- Requirements checking and installation

### Planned Features
- Multiple account support
- Scheduled scraping
- Data visualization
- Export to additional formats (PDF, Word)
- Instagram Stories support
- Bulk username processing

## Installation Verification

After installation, verify everything works:

1. **Run the launcher**:
   ```bash
   run_scraper.bat
   ```

2. **Check Python detection**:
   - Should find your Python installation
   - Display Python version

3. **Verify packages**:
   - Should show [OK] for all required packages
   - Install any [MISSING] packages when prompted

4. **Test the GUI**:
   - Application should launch without errors
   - All controls should be responsive

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made for data analysis and research purposes**

*Last updated: July 2025*
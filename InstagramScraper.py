from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import re
import json
import logging
from datetime import datetime, timedelta
import os
from tkinter import filedialog
import tkinter as tk

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstagramReelsScraper:
    def __init__(self, headless=False, user_agent=None):
        """
        Initialize the Instagram Reels scraper
        
        Args:
            headless (bool): Run browser in headless mode
            user_agent (str): Custom user agent string
        """
        self.driver = None
        self.headless = headless
        self.user_agent = user_agent
        
    def setup_driver(self):
        """Setup Chrome driver with optimized options"""
        try:
            options = Options()
            
            # Basic options
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Stability options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            
            # User agent
            if self.user_agent:
                options.add_argument(f"--user-agent={self.user_agent}")
            else:
                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Memory management
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")
            
            # Create driver
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup driver: {e}")
            return False

    def convert_relative_date_to_formatted_date(self, date_text):
        """
        Convert relative date (like '2 hours ago') to formatted date (like '12 July 2025')
        Keep existing date formats as-is
        
        Args:
            date_text (str): Original date text from Instagram
            
        Returns:
            str: Formatted date string
        """
        if not date_text or date_text == "N/A":
            return "N/A"
        
        try:
            # Get current time
            now = datetime.now()
            
            # Clean the text
            date_text = date_text.strip().lower()
            
            # Check if it's already in a date format (contains month names)
            month_names = [
                'january', 'february', 'march', 'april', 'may', 'june',
                'july', 'august', 'september', 'october', 'november', 'december',
                'jan', 'feb', 'mar', 'apr', 'may', 'jun',
                'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
            ]
            
            # If it already contains a month name, keep it as-is but format it properly
            if any(month in date_text for month in month_names):
                # Try to parse and reformat existing date
                try:
                    # Handle formats like "July 26", "July 26, 2024", "26 July", etc.
                    for fmt in ['%B %d', '%b %d', '%d %B', '%d %b', '%B %d, %Y', '%b %d, %Y']:
                        try:
                            parsed_date = datetime.strptime(date_text.title(), fmt)
                            # If no year specified, assume current year
                            if parsed_date.year == 1900:
                                parsed_date = parsed_date.replace(year=now.year)
                            return parsed_date.strftime('%d %B %Y')
                        except:
                            continue
                    
                    # If parsing fails, return the original text cleaned up
                    return date_text.title()
                except:
                    return date_text.title()
            
            # Handle relative dates
            target_date = now
            
            # Minutes ago
            minutes_match = re.search(r'(\d+)\s*(?:minute|minutes|min|mins?)\s*ago', date_text)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                target_date = now - timedelta(minutes=minutes)
            
            # Hours ago
            elif re.search(r'(\d+)\s*(?:hour|hours|hr|hrs?)\s*ago', date_text):
                hours_match = re.search(r'(\d+)\s*(?:hour|hours|hr|hrs?)\s*ago', date_text)
                hours = int(hours_match.group(1))
                target_date = now - timedelta(hours=hours)
            
            # Days ago
            elif re.search(r'(\d+)\s*(?:day|days|d)\s*ago', date_text):
                days_match = re.search(r'(\d+)\s*(?:day|days|d)\s*ago', date_text)
                days = int(days_match.group(1))
                target_date = now - timedelta(days=days)
            
            # Weeks ago
            elif re.search(r'(\d+)\s*(?:week|weeks|w)\s*ago', date_text):
                weeks_match = re.search(r'(\d+)\s*(?:week|weeks|w)\s*ago', date_text)
                weeks = int(weeks_match.group(1))
                target_date = now - timedelta(weeks=weeks)
            
            # Months ago (approximate)
            elif re.search(r'(\d+)\s*(?:month|months|mo)\s*ago', date_text):
                months_match = re.search(r'(\d+)\s*(?:month|months|mo)\s*ago', date_text)
                months = int(months_match.group(1))
                target_date = now - timedelta(days=months * 30)  # Approximate
            
            # Years ago
            elif re.search(r'(\d+)\s*(?:year|years|y)\s*ago', date_text):
                years_match = re.search(r'(\d+)\s*(?:year|years|y)\s*ago', date_text)
                years = int(years_match.group(1))
                target_date = now - timedelta(days=years * 365)  # Approximate
            
            # Special cases
            elif 'yesterday' in date_text:
                target_date = now - timedelta(days=1)
            elif 'today' in date_text or 'now' in date_text:
                target_date = now
            else:
                # If we can't parse it, return the original text
                logger.warning(f"Could not parse date: {date_text}")
                return date_text
            
            # Format the target date as "12 July 2025"
            formatted_date = target_date.strftime('%d %B %Y')
            
            logger.debug(f"Converted '{date_text}' to '{formatted_date}'")
            return formatted_date
            
        except Exception as e:
            logger.warning(f"Error converting date '{date_text}': {e}")
            return date_text  # Return original if conversion fails

    def manual_login(self, timeout=300):
        """
        Manual login to Instagram with improved error handling
        
        Args:
            timeout (int): Maximum time to wait for login (seconds)
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info("🔐 Opening Instagram login page...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            # Wait for login page to load
            WebDriverWait(self.driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.NAME, "username")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                )
            )
            
            print("📝 Please login manually in the browser window")
            print("   - Enter your username and password")
            print("   - Click the login button")
            print("   - Handle any 2FA if required")
            print("   - Handle any popups that appear")
            print(f"\n⏳ Waiting up to {timeout//60} minutes for you to complete login...")
            
            # Wait for user to login manually
            login_success = False
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    time.sleep(3)
                    
                    current_url = self.driver.current_url
                    logger.debug(f"Current URL: {current_url}")
                    
                    # Check multiple indicators of successful login
                    login_indicators = [
                        # URL-based checks
                        lambda: 'instagram.com/' in current_url and 'login' not in current_url,
                        lambda: 'instagram.com/accounts/onetap' in current_url,
                        
                        # Element-based checks
                        lambda: self._element_exists("svg[aria-label='Home']"),
                        lambda: self._element_exists("svg[aria-label='New post']"),
                        lambda: self._element_exists("a[href='/']"),
                        lambda: self._element_exists("div[role='main']"),
                        lambda: self._element_exists("nav[role='navigation']"),
                    ]
                    
                    if any(indicator() for indicator in login_indicators):
                        login_success = True
                        break
                        
                except WebDriverException as e:
                    logger.warning(f"Driver error during login check: {e}")
                    # If driver crashes, try to recover
                    if "chrome not reachable" in str(e).lower():
                        logger.error("Chrome crashed during login. Please restart the script.")
                        return False
                    continue
                except Exception as e:
                    logger.warning(f"Unexpected error during login check: {e}")
                    continue
            
            if login_success:
                logger.info("✅ Login successful!")
                self._handle_login_popups()
                return True
            else:
                logger.error("❌ Login timeout or failed!")
                return False
                
        except TimeoutException:
            logger.error("❌ Login page failed to load within timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def _element_exists(self, selector, timeout=2):
        """Check if element exists without throwing exceptions"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except:
            return False
    
    def _handle_login_popups(self):
        """Handle common Instagram popups after login"""
        try:
            time.sleep(2)
            
            # Common popup button texts
            popup_texts = [
                "Not Now", "Not now", "Cancel", "Skip", "Maybe Later", 
                "Ask Later", "Dismiss", "Close"
            ]
            
            for text in popup_texts:
                try:
                    buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{text}')]")
                    for btn in buttons:
                        if btn.is_displayed():
                            btn.click()
                            time.sleep(1)
                            logger.info(f"✅ Closed popup: {text}")
                            break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Warning: Could not handle popups: {e}")
    
    def _extract_caption_from_url(self, reel_url):
        """Extract caption by visiting the reel URL"""
        if not reel_url:
            return ""
        
        try:
            # Store current window handle
            main_window = self.driver.current_window_handle
            
            # Open new tab
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Navigate to reel URL
            self.driver.get(reel_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.TAG_NAME, "h1")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
                )
            )
            
            time.sleep(2)
            
            # Try multiple caption selectors
            caption_selectors = [
                "h1",  # Main caption
                "div._a9zs span",  # Alternative caption
                "span[dir='auto']",  # Generic caption
                "article span[dir='auto']",  # Article caption
                "div[data-testid='post-comment-root'] span",  # Comment root
                "div._ac7v span[dir='auto']",  # Another variant
                "div._aacl._aaco._aacu._aacx._aada span",  # Specific Instagram classes
            ]
            
            caption = ""
            for selector in caption_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 10:  # Assume caption is longer than 10 chars
                            caption = text
                            break
                    if caption:
                        break
                except:
                    continue
            
            # Close tab and switch back to main window
            self.driver.close()
            self.driver.switch_to.window(main_window)
            
            return caption[:2500]  # Limit caption length
            
        except Exception as e:
            logger.warning(f"❌ Failed to extract caption from {reel_url}: {e}")
            # Make sure we're back on main window
            try:
                self.driver.switch_to.window(main_window)
            except:
                pass
            return ""
    
    def _extract_likes_and_date_from_url(self, reel_url):
        """Extract likes count and post date by visiting the reel URL"""
        if not reel_url:
            return "N/A", "N/A"
        
        try:
            # Store current window handle
            main_window = self.driver.current_window_handle
            
            # Open new tab
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Navigate to reel URL
            self.driver.get(reel_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.TAG_NAME, "article")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "main")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "section"))
                )
            )
            
            time.sleep(3)  # Wait for content to fully load
            
            likes_count = "N/A"
            post_date = "N/A"
            
            # Extract likes count
            likes_count = self._find_likes_count()
            
            # Extract post date
            raw_date = self._find_post_date()
            
            # Convert date to formatted date
            if raw_date and raw_date != "N/A":
                post_date = self.convert_relative_date_to_formatted_date(raw_date)
                logger.info(f"📅 Date conversion: '{raw_date}' → '{post_date}'")
            else:
                post_date = "N/A"
            
            # Close tab and switch back to main window
            self.driver.close()
            self.driver.switch_to.window(main_window)
            
            return likes_count, post_date
            
        except Exception as e:
            logger.warning(f"❌ Failed to extract likes and date from {reel_url}: {e}")
            # Make sure we're back on main window
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(main_window)
            except:
                pass
            return "N/A", "N/A"
    
    def _find_likes_count(self):
        """Find likes count on individual reel page"""
        try:
            # Multiple selectors for likes count
            likes_selectors = [
                # Likes button/text patterns
                "button[type='button'] span:contains('likes')",
                "a[href*='/liked_by/'] span",
                "section button span",
                "div[role='button'] span",
                
                # Alternative patterns
                "span[dir='auto']:contains('likes')",
                "span:contains(' likes')",
                "button span:contains('like')",
                
                # Specific Instagram classes (these change frequently)
                "span._aacl._aaco._aacu._aacx._aada",
                "span._ac2a",
                "div._ae5c span",
            ]
            
            for selector in likes_selectors:
                try:
                    if ':contains(' in selector:
                        # Use XPath for contains
                        xpath_selector = selector.replace(':contains(', '[contains(text(), ').replace(')', ')]')
                        elements = self.driver.find_elements(By.XPATH, f"//*{xpath_selector}")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        text = element.text.strip()
                        
                        # Check if this looks like a likes count
                        if self._is_likes_count(text):
                            logger.info(f"👍 Found likes: {text}")
                            return text
                        
                        # Check parent/sibling elements
                        try:
                            parent = element.find_element(By.XPATH, "..")
                            parent_text = parent.text.strip()
                            if self._is_likes_count(parent_text):
                                logger.info(f"👍 Found likes in parent: {parent_text}")
                                return parent_text
                        except:
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error with likes selector {selector}: {e}")
                    continue
            
            # Alternative method: look for patterns in all text
            try:
                all_spans = self.driver.find_elements(By.TAG_NAME, "span")
                for span in all_spans:
                    text = span.text.strip()
                    # Look for patterns like "1,234 likes" or "1.2K likes"
                    likes_match = re.search(r'([\d,]+(?:\.\d+)?[KMB]?)\s*likes?', text, re.IGNORECASE)
                    if likes_match:
                        likes_text = likes_match.group(1)
                        logger.info(f"👍 Found likes via pattern: {likes_text}")
                        return likes_text
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Error finding likes count: {e}")
        
        return "N/A"
    
    def _find_post_date(self):
        """Find post date on individual reel page"""
        try:
            # Multiple selectors for post date/time
            date_selectors = [
                # Time elements
                "time",
                "time[datetime]",
                "span[title]",
                
                # Common date patterns
                "a[href*='/p/'] time",
                "article time",
                "div time",
                
                # Alternative selectors
                "span._a9ze",
                "div._a9ze",
                "span[dir='auto'][title]",
            ]
            
            for selector in date_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        # Check datetime attribute first
                        datetime_attr = element.get_attribute("datetime")
                        if datetime_attr:
                            logger.info(f"📅 Found datetime attribute: {datetime_attr}")
                            return datetime_attr
                        
                        # Check title attribute
                        title_attr = element.get_attribute("title")
                        if title_attr and self._is_date_text(title_attr):
                            logger.info(f"📅 Found date in title: {title_attr}")
                            return title_attr
                        
                        # Check text content
                        text = element.text.strip()
                        if text and self._is_date_text(text):
                            logger.info(f"📅 Found date text: {text}")
                            return text
                            
                except Exception as e:
                    logger.debug(f"Error with date selector {selector}: {e}")
                    continue
            
            # Alternative method: look for date patterns in all text
            try:
                all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*[title]")
                for element in all_elements:
                    title = element.get_attribute("title")
                    if title and self._is_date_text(title):
                        logger.info(f"📅 Found date in title attribute: {title}")
                        return title
                        
                # Look for text patterns
                all_spans = self.driver.find_elements(By.TAG_NAME, "span")
                for span in all_spans:
                    text = span.text.strip()
                    if self._is_date_text(text):
                        logger.info(f"📅 Found date text: {text}")
                        return text
                        
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Error finding post date: {e}")
        
        return "N/A"
    
    def _is_likes_count(self, text):
        """Check if text looks like a likes count"""
        if not text:
            return False
        
        # Patterns for likes count
        patterns = [
            r'^\d+[.,]?\d*[KMB]?\s*$',  # Just numbers with K/M/B
            r'^\d{1,3}(,\d{3})*\s*$',   # Numbers with commas
            r'^\d+\s*$'                 # Plain numbers
        ]
        
        # Remove common words and check
        clean_text = re.sub(r'\s*(likes?|like)\s*', '', text, flags=re.IGNORECASE).strip()
        
        return any(re.match(pattern, clean_text) for pattern in patterns)
    
    def _is_date_text(self, text):
        """Check if text looks like a date/time"""
        if not text or len(text) < 3:
            return False
        
        # Patterns for date/time text
        date_patterns = [
            r'\d+\s*(minute|minutes|min|mins?)\s*ago',
            r'\d+\s*(hour|hours|hr|hrs?)\s*ago',
            r'\d+\s*(day|days|d)\s*ago',
            r'\d+\s*(week|weeks|w)\s*ago',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+',
            r'\d{4}-\d{2}-\d{2}',  # ISO date format
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY format
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in date_patterns)

    def scrape_reels_views(self, target_username, max_scrolls=3, delay=3, extract_captions=True, extract_likes_dates=True):
        """
        Scrape Instagram Reels view counts with improved error handling
        
        Args:
            target_username (str): Instagram username to scrape
            max_scrolls (int): Number of times to scroll down
            delay (int): Delay between actions in seconds
            extract_captions (bool): Whether to extract captions (slower but more complete)
            extract_likes_dates (bool): Whether to extract likes and dates (slower but more complete)
        
        Returns:
            list: List of dictionaries containing reel data
        """
        reels_data = []
        
        try:
            # Navigate to the Reels page
            url = f"https://www.instagram.com/{target_username}/reels/"
            logger.info(f"🌐 Navigating to: {url}")
            
            self.driver.get(url)
            
            # Wait for page to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
                    )
                )
            except TimeoutException:
                logger.error("❌ Reels page failed to load")
                return []
            
            # Check if profile exists and has reels
            if self._check_profile_issues():
                return []
            
            # Wait a bit longer for initial content to fully load
            time.sleep(5)
            
            # FIRST: Capture initial visible reels (before any scrolling)
            logger.info("🔍 Capturing initial visible reels...")
            initial_reels = self._extract_view_counts_with_urls()
            if initial_reels:
                reels_data.extend(initial_reels)
                logger.info(f"✅ Found {len(initial_reels)} initial reels")
            
            # THEN: Scroll to load more content and capture new reels
            for i in range(max_scrolls):
                try:
                    logger.info(f"📜 Scrolling to load more content... ({i+1}/{max_scrolls})")
                    
                    # Get current reels count before scrolling
                    current_count = len(reels_data)
                    
                    # Scroll down
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(delay)
                    
                    # Extract new reels after scrolling
                    new_reels = self._extract_view_counts_with_urls()
                    
                    # Add only new reels (not duplicates)
                    if new_reels:
                        for reel in new_reels:
                            # Check if this reel URL is already captured
                            reel_url = reel.get('url', '')
                            existing_urls = [r.get('url', '') for r in reels_data]
                            
                            if reel_url and reel_url not in existing_urls:
                                reels_data.append(reel)
                            elif not reel_url:  # If no URL, check by views to avoid duplicates
                                existing_views = [r.get('views', '') for r in reels_data]
                                if reel.get('views', '') not in existing_views:
                                    reels_data.append(reel)
                    
                    new_count = len(reels_data)
                    logger.info(f"📊 Total reels after scroll {i+1}: {new_count} (added {new_count - current_count})")
                    
                    # If no new reels found, we might have reached the end
                    if new_count == current_count:
                        logger.info("🔚 No new reels found, might have reached the end")
                    
                except Exception as e:
                    logger.warning(f"Scrolling error: {e}")
                    continue
            
            # Extract captions, likes, and dates if requested
            if (extract_captions or extract_likes_dates) and reels_data:
                logger.info("📝 Extracting additional data (captions, likes, dates)...")
                for i, reel in enumerate(reels_data):
                    if 'url' in reel and reel['url'] and reel['url'] != 'N/A':
                        logger.info(f"📝 Processing reel {i+1}/{len(reels_data)}...")
                        
                        if extract_captions:
                            caption = self._extract_caption_from_url(reel['url'])
                            reel['caption'] = caption
                            if caption:
                                logger.info(f"✅ Caption extracted: {caption[:50]}...")
                        
                        if extract_likes_dates:
                            likes, date = self._extract_likes_and_date_from_url(reel['url'])
                            reel['likes'] = likes
                            reel['post_date'] = date
                            reel['post_date_raw'] = date  # Keep original for reference
                            logger.info(f"✅ Likes: {likes}, Date: {date}")
                        
                        time.sleep(1)  # Be gentle with requests
                    else:
                        # Set default values if no URL
                        if extract_captions:
                            reel['caption'] = ""
                        if extract_likes_dates:
                            reel['likes'] = "N/A"
                            reel['post_date'] = "N/A"
                            reel['post_date_raw'] = "N/A"
            
            # Remove duplicates and re-index properly
            unique_reels = self._remove_duplicates_and_reindex(reels_data)
            
            return unique_reels
            
        except Exception as e:
            logger.error(f"❌ Error occurred during scraping: {e}")
            return []

    def scrape_reels_by_count(self, target_username, target_posts=20, delay=3, extract_captions=True, extract_likes_dates=True, max_scrolls=50):
        """
        Scrape Instagram Reels until reaching target number of posts
        
        Args:
            target_username (str): Instagram username to scrape
            target_posts (int): Target number of posts to scrape
            delay (int): Delay between actions in seconds
            extract_captions (bool): Whether to extract captions (slower but more complete)
            extract_likes_dates (bool): Whether to extract likes and dates (slower but more complete)
            max_scrolls (int): Maximum number of scrolls to prevent infinite loops
        
        Returns:
            list: List of dictionaries containing reel data
        """
        reels_data = []
        
        try:
            # Navigate to the Reels page
            url = f"https://www.instagram.com/{target_username}/reels/"
            logger.info(f"🌐 Navigating to: {url}")
            logger.info(f"🎯 Target posts: {target_posts}")
            
            self.driver.get(url)
            
            # Wait for page to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
                    )
                )
            except TimeoutException:
                logger.error("❌ Reels page failed to load")
                return []
            
            # Check if profile exists and has reels
            if self._check_profile_issues():
                return []
            
            # Wait a bit longer for initial content to fully load
            time.sleep(5)
            
            # FIRST: Capture initial visible reels
            logger.info("🔍 Capturing initial visible reels...")
            initial_reels = self._extract_view_counts_with_urls()
            if initial_reels:
                reels_data.extend(initial_reels)
                logger.info(f"✅ Found {len(initial_reels)} initial reels")
                logger.info(f"📊 Progress: {len(reels_data)}/{target_posts} reels captured")
            
            # Check if we already have enough reels
            if len(reels_data) >= target_posts:
                logger.info(f"✅ Target reached with initial load! Found {len(reels_data)} reels")
                reels_data = reels_data[:target_posts]  # Trim to exact target
            else:
                # THEN: Scroll to load more content until we reach target
                scroll_count = 0
                consecutive_no_new_reels = 0
                
                while len(reels_data) < target_posts and scroll_count < max_scrolls:
                    try:
                        scroll_count += 1
                        logger.info(f"📜 Scrolling to load more content... (Scroll {scroll_count}/{max_scrolls})")
                        logger.info(f"📊 Current progress: {len(reels_data)}/{target_posts} reels")
                        
                        # Get current reels count before scrolling
                        current_count = len(reels_data)
                        
                        # Scroll down
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(delay)
                        
                        # Extract new reels after scrolling
                        new_reels = self._extract_view_counts_with_urls()
                        
                        # Add only new reels (not duplicates)
                        new_reels_added = 0
                        if new_reels:
                            for reel in new_reels:
                                # Check if this reel URL is already captured
                                reel_url = reel.get('url', '')
                                existing_urls = [r.get('url', '') for r in reels_data]
                                
                                if reel_url and reel_url not in existing_urls:
                                    reels_data.append(reel)
                                    new_reels_added += 1
                                elif not reel_url:  # If no URL, check by views to avoid duplicates
                                    existing_views = [r.get('views', '') for r in reels_data]
                                    if reel.get('views', '') not in existing_views:
                                        reels_data.append(reel)
                                        new_reels_added += 1
                                
                                # Stop if we've reached our target
                                if len(reels_data) >= target_posts:
                                    break
                        
                        new_count = len(reels_data)
                        logger.info(f"📊 Added {new_reels_added} new reels. Total: {new_count}/{target_posts}")
                        
                        # Check if we reached the target
                        if len(reels_data) >= target_posts:
                            logger.info(f"🎯 Target reached! Found {len(reels_data)} reels")
                            reels_data = reels_data[:target_posts]  # Trim to exact target
                            break
                        
                        # If no new reels found, increment counter
                        if new_reels_added == 0:
                            consecutive_no_new_reels += 1
                            logger.warning(f"⚠️ No new reels found in this scroll ({consecutive_no_new_reels}/3)")
                            
                            # If we haven't found new reels in 3 consecutive scrolls, might be at the end
                            if consecutive_no_new_reels >= 3:
                                logger.warning("🔚 No new reels found in 3 consecutive scrolls. Might have reached the end.")
                                logger.info(f"📊 Final count: {len(reels_data)} reels (target was {target_posts})")
                                break
                        else:
                            consecutive_no_new_reels = 0  # Reset counter when we find new reels
                        
                        # Add a longer delay if we're getting close to prevent rate limiting
                        if len(reels_data) > target_posts * 0.8:  # 80% of target
                            time.sleep(delay + 2)
                        
                    except Exception as e:
                        logger.warning(f"Scrolling error: {e}")
                        continue
                
                # Final status
                if len(reels_data) >= target_posts:
                    logger.info(f"✅ Successfully reached target! Found {len(reels_data)} reels")
                else:
                    logger.warning(f"⚠️ Could not reach target. Found {len(reels_data)}/{target_posts} reels after {scroll_count} scrolls")
            
            # Extract captions, likes, and dates if requested
            if (extract_captions or extract_likes_dates) and reels_data:
                logger.info("📝 Extracting additional data (captions, likes, dates)...")
                for i, reel in enumerate(reels_data):
                    logger.info(f"📝 Processing reel {i+1}/{len(reels_data)} ({((i+1)/len(reels_data)*100):.1f}%)...")
                    
                    if 'url' in reel and reel['url'] and reel['url'] != 'N/A':
                        if extract_captions:
                            caption = self._extract_caption_from_url(reel['url'])
                            reel['caption'] = caption
                            if caption:
                                logger.info(f"✅ Caption extracted: {caption[:50]}...")
                        
                        if extract_likes_dates:
                            likes, date = self._extract_likes_and_date_from_url(reel['url'])
                            reel['likes'] = likes
                            reel['post_date'] = date
                            reel['post_date_raw'] = date  # Keep original for reference
                            logger.info(f"✅ Likes: {likes}, Date: {date}")
                        
                        time.sleep(1)  # Be gentle with requests
                    else:
                        # Set default values if no URL
                        if extract_captions:
                            reel['caption'] = ""
                        if extract_likes_dates:
                            reel['likes'] = "N/A"
                            reel['post_date'] = "N/A"
                            reel['post_date_raw'] = "N/A"
            
            # Remove duplicates and re-index properly
            unique_reels = self._remove_duplicates_and_reindex(reels_data)
            
            # Final trim to ensure exact count
            if len(unique_reels) > target_posts:
                unique_reels = unique_reels[:target_posts]
                logger.info(f"✂️ Trimmed to exact target: {len(unique_reels)} reels")
            
            logger.info(f"🏁 Final result: {len(unique_reels)} reels collected")
            return unique_reels
            
        except Exception as e:
            logger.error(f"❌ Error occurred during scraping by count: {e}")
            return []

    def format_likes_count(self, likes_str):
        """Convert likes count string to number (same logic as views)"""
        return self.format_view_count(likes_str)

    def _check_profile_issues(self):
        """Check for common profile issues"""
        try:
            # Check for private account
            if self._element_exists("h2[class*='private']", 3):
                logger.error("❌ This account is private")
                return True
            
            # Check for "No posts yet" or similar
            no_content_selectors = [
                "h2:contains('No Posts Yet')",
                "span:contains('No posts yet')",
                "span:contains('No Reels yet')",
                "div:contains('No posts yet')"
            ]
            
            for selector in no_content_selectors:
                if self._element_exists(selector, 2):
                    logger.error("❌ This account has no reels")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Could not check profile issues: {e}")
            return False
    
    def _extract_view_counts_with_urls(self):
        """Extract view counts and URLs using multiple methods with proper grid traversal"""
        reels_data = []
        
        # Enhanced comprehensive search that focuses on getting both views and URLs
        logger.info("🔄 Searching for reels with views and URLs...")
        
        try:
            # Wait a moment for content to stabilize
            time.sleep(2)
            
            # First, try to find the main grid container
            grid_selectors = [
                "main article div",  # Main grid container
                "div[style*='grid']",  # CSS Grid container
                "section main div",   # Section main container
                "main div",           # General main container
            ]
            
            grid_found = False
            
            for grid_selector in grid_selectors:
                try:
                    grid_containers = self.driver.find_elements(By.CSS_SELECTOR, grid_selector)
                    
                    for grid in grid_containers:
                        # Look for all reel links within this grid, ordered by position
                        reel_links = grid.find_elements(By.CSS_SELECTOR, "a[href*='/reel/']")
                        
                        if reel_links:
                            logger.info(f"🔍 Found {len(reel_links)} reel links in grid with selector: {grid_selector}")
                            
                            # Sort by position (top to bottom, left to right)
                            reel_links_with_position = []
                            for link in reel_links:
                                try:
                                    location = link.location
                                    # Make sure the element is visible
                                    if location['y'] >= 0 and location['x'] >= 0:
                                        reel_links_with_position.append((link, location['y'], location['x']))
                                except:
                                    # If can't get location, still include it with default position
                                    reel_links_with_position.append((link, 0, 0))
                            
                            # Sort by Y position first (row), then X position (column)
                            reel_links_with_position.sort(key=lambda x: (x[1], x[2]))
                            
                            # Extract data from sorted links
                            for idx, (link, y, x) in enumerate(reel_links_with_position):
                                try:
                                    reel_url = link.get_attribute("href")
                                    if not reel_url or '/reel/' not in reel_url:
                                        continue
                                    
                                    # Look for view count in the link or its parent containers
                                    view_count = self._find_view_count_in_reel_link(link)
                                    
                                    # Create reel data entry
                                    reel_data = {
                                        'views': view_count if view_count else 'N/A',
                                        'url': reel_url,
                                        'reel_index': idx + 1,
                                        'position': {'row': int(y), 'col': int(x)},
                                        'selector_used': f'grid_search_{grid_selector}',
                                        'timestamp': datetime.now().isoformat(),
                                        'caption': ""
                                    }
                                    
                                    reels_data.append(reel_data)
                                    
                                    if view_count:
                                        logger.info(f"🎥 Reel {idx + 1}: {view_count} views - Position(Y:{y}, X:{x})")
                                    else:
                                        logger.info(f"🎥 Reel {idx + 1}: No views found - Position(Y:{y}, X:{x})")
                                    
                                except Exception as e:
                                    logger.debug(f"Error processing reel link {idx}: {e}")
                                    continue
                            
                            if reels_data:
                                grid_found = True
                                break
                                
                except Exception as e:
                    logger.warning(f"Error with grid selector {grid_selector}: {e}")
                    continue
                
                if grid_found:
                    break
            
            # Fallback method: Find all reel containers regardless of grid
            if not reels_data:
                logger.info("🔄 Grid method failed, trying fallback container search...")
                reels_data = self._fallback_container_search()
            
            # Final fallback: Original extraction methods
            if not reels_data:
                logger.info("🔄 Falling back to original extraction methods...")
                reels_data = self._extract_view_counts()
            
            return reels_data
        
        except Exception as e:
            logger.error(f"Error in enhanced search: {e}")
            return []

    def _find_view_count_in_reel_link(self, link_element):
        """Find view count within a reel link element and its parents"""
        try:
            # Search in multiple container levels
            containers_to_check = [
                link_element,  # The link itself
                link_element.find_element(By.XPATH, ".."),  # Parent
                link_element.find_element(By.XPATH, "../.."),  # Grandparent
            ]
            
            for container in containers_to_check:
                try:
                    # Look for spans with view counts
                    spans = container.find_elements(By.CSS_SELECTOR, "span")
                    for span in spans:
                        text = span.text.strip()
                        if self._is_view_count(text):
                            return text
                    
                    # Look for divs with view counts  
                    divs = container.find_elements(By.CSS_SELECTOR, "div")
                    for div in divs:
                        text = div.text.strip()
                        if self._is_view_count(text):
                            return text
                            
                    # Check for view count in overlay elements
                    overlay_selectors = [
                        "[aria-label*='views']",
                        "[title*='views']", 
                        "div[style*='position: absolute'] span",
                        "div[class*='overlay'] span",
                    ]
                    
                    for selector in overlay_selectors:
                        try:
                            overlay_elements = container.find_elements(By.CSS_SELECTOR, selector)
                            for element in overlay_elements:
                                # Check aria-label or title
                                aria_text = (element.get_attribute("aria-label") or 
                                           element.get_attribute("title") or
                                           element.text.strip())
                                
                                if aria_text and "view" in aria_text.lower():
                                    view_match = re.search(r'([\d,]+(?:\.\d+)?[KMB]?)\s*views?', 
                                                         aria_text, re.IGNORECASE)
                                    if view_match:
                                        return view_match.group(1)
                                
                                # Check text content
                                text = element.text.strip()
                                if self._is_view_count(text):
                                    return text
                                    
                        except:
                            continue
                            
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Error finding view count in reel link: {e}")
        
        return None

    def _fallback_container_search(self):
        """Fallback method to find all reel containers"""
        reels_data = []
        
        try:
            # Find all links that contain '/reel/' in href
            all_reel_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/reel/']")
            logger.info(f"🔍 Found {len(all_reel_links)} total reel links")
            
            # Sort by position to maintain order
            reel_links_with_position = []
            for link in all_reel_links:
                try:
                    location = link.location
                    size = link.size
                    # Calculate center position for better sorting
                    center_y = location['y'] + size['height'] / 2
                    center_x = location['x'] + size['width'] / 2
                    reel_links_with_position.append((link, center_y, center_x))
                except:
                    reel_links_with_position.append((link, 0, 0))
            
            # Sort by Y position first (rows), then X position (columns)
            reel_links_with_position.sort(key=lambda x: (x[1], x[2]))
            
            for idx, (link, y, x) in enumerate(reel_links_with_position):
                try:
                    reel_url = link.get_attribute("href")
                    if not reel_url or '/reel/' not in reel_url:
                        continue
                    
                    # Look for view count
                    view_count = self._find_view_count_in_reel_link(link)
                    
                    if view_count:
                        reel_data = {
                            'views': view_count,
                            'url': reel_url,
                            'reel_index': idx + 1,
                            'position': {'row': int(y), 'col': int(x)},
                            'selector_used': 'fallback_container_search',
                            'timestamp': datetime.now().isoformat(),
                            'caption': ""
                        }
                        
                        reels_data.append(reel_data)
                        logger.info(f"🎥 Reel {idx + 1}: {view_count} views - URL: {reel_url}")
                    else:
                        # Even if no view count found, still capture the reel for URL and caption
                        reel_data = {
                            'views': 'N/A',
                            'url': reel_url,
                            'reel_index': idx + 1,
                            'position': {'row': int(y), 'col': int(x)},
                            'selector_used': 'fallback_container_search_no_views',
                            'timestamp': datetime.now().isoformat(),
                            'caption': ""
                        }
                        
                        reels_data.append(reel_data)
                        logger.info(f"🎥 Reel {idx + 1}: No views found - URL: {reel_url}")
                    
                except Exception as e:
                    logger.debug(f"Error processing fallback reel {idx}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in fallback container search: {e}")
        
        return reels_data

    def _extract_view_counts(self):
        """Extract view counts using multiple methods (original method)"""
        reels_data = []
        
        # Method 1: Direct selectors
        view_selectors = [
            "div._aabd span",
            "div._ac7v span", 
            "span[dir='auto']",
            "div._aagw span",
            "div._ac2a span",
            "div[role='button'] span",
            "div._aacl span",
            "div._ab8w span",
            "article span",
        ]
        
        for selector in view_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"🔍 Found {len(elements)} elements with selector: {selector}")
                
                for element in elements:
                    try:
                        text = element.text.strip()
                        if self._is_view_count(text):
                            reels_data.append({
                                'views': text,
                                'selector_used': selector,
                                'timestamp': datetime.now().isoformat(),
                                'url': "",
                                'caption': ""
                            })
                            logger.info(f"👁️ Found view count: {text}")
                    except:
                        continue
                        
                if reels_data:
                    break
                    
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {e}")
                continue
        
        return reels_data
    
    def _is_view_count(self, text):
        """Check if text looks like a view count"""
        if not text:
            return False
        
        # Patterns for view counts
        patterns = [
            r'^\d+[.,]?\d*[KMB]?$',  # 1.2K, 500M, 1B
            r'^\d{1,3}(,\d{3})*$',   # 1,000,000
            r'^\d+(\.\d+)?[KMB]$',   # 1.5K, 2.3M
            r'^\d+$'                 # Plain numbers
        ]
        
        return any(re.match(pattern, text) for pattern in patterns)
    
    def _remove_duplicates_and_reindex(self, reels_data):
        """Remove duplicate view counts and URLs with improved deduplication and proper indexing"""
        unique_reels = []
        seen_urls = set()
        seen_views = set()
        
        for reel in reels_data:
            url = reel.get('url', '')
            views = reel.get('views', '')
            
            # Use URL as primary deduplication key
            if url and url not in seen_urls:
                unique_reels.append(reel)
                seen_urls.add(url)
                if views:
                    seen_views.add(views)
            elif not url and views and views not in seen_views:
                # If no URL, use views for deduplication
                unique_reels.append(reel)
                seen_views.add(views)
        
        # Sort by position to maintain proper grid order (top to bottom, left to right)
        def sort_key(reel):
            position = reel.get('position', {})
            row = position.get('row', 0)
            col = position.get('col', 0)
            return (row, col)
        
        unique_reels.sort(key=sort_key)
        
        # Re-index properly starting from 1
        for i, reel in enumerate(unique_reels):
            reel['reel_index'] = i + 1
        
        logger.info(f"✅ Final count: {len(unique_reels)} unique reels after deduplication")
        
        return unique_reels
    
    def format_view_count(self, view_str):
        """Convert view count string to number"""
        try:
            if 'K' in view_str:
                return float(view_str.replace('K', '').replace(',', '')) * 1000
            elif 'M' in view_str:
                return float(view_str.replace('M', '').replace(',', '')) * 1000000
            elif 'B' in view_str:
                return float(view_str.replace('B', '').replace(',', '')) * 1000000000
            else:
                return float(view_str.replace(',', ''))
        except:
            return 0
        
    def choose_output_directory(self):
        """Let user choose output directory"""
        try:
            # Create a temporary root window for the dialog
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Open directory selection dialog
            output_dir = filedialog.askdirectory(
                title="Choose Output Directory for Results",
                initialdir=os.path.expanduser("~/Documents")  # Start in Documents folder
            )
            
            root.destroy()  # Clean up the temporary window
            
            if output_dir:
                return output_dir
            else:
                # If user cancels, return current directory
                return os.getcwd()
                
        except Exception as e:
            logger.warning(f"Error choosing directory: {e}")
            return os.getcwd()  # Fallback to current directory

    def save_results(self, results, filename=None, output_dir=None):
        """Save results to JSON file with custom directory"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_reels_data_{timestamp}.json"
        
        # Use provided output directory or current directory
        if output_dir:
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"📁 Results saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
            return None
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"📁 Results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
    
    def close(self):
        """Close the driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔒 Driver closed successfully")
            except Exception as e:
                logger.warning(f"Warning: Error closing driver: {e}")

def main():
    """Main function to run the scraper"""
    # Configuration
    TARGET_USERNAME = "bankmandiri"  # Change this to your target username
    MAX_SCROLLS = 0
    HEADLESS = False  # Set to True to run without GUI
    EXTRACT_CAPTIONS = True  # Set to False to skip caption extraction (faster)
    EXTRACT_LIKES_DATES = True  # Set to False to skip likes and dates extraction (faster)
    
    # Initialize scraper
    scraper = InstagramReelsScraper(headless=HEADLESS)
    
    try:
        # Setup driver
        if not scraper.setup_driver():
            logger.error("❌ Failed to setup driver. Exiting...")
            return
        
        # Login
        if not scraper.manual_login():
            logger.error("❌ Failed to login. Exiting...")
            return
        
        # Scrape reels
        logger.info("🚀 Starting Instagram Reels scraper...")
        results = scraper.scrape_reels_views(
            TARGET_USERNAME, 
            max_scrolls=MAX_SCROLLS, 
            extract_captions=EXTRACT_CAPTIONS,
            extract_likes_dates=EXTRACT_LIKES_DATES
        )
        
        # Display results
        if results:
            logger.info(f"\n📊 Found {len(results)} reels with view counts:")
            print("=" * 80)
            
            total_views = 0
            total_likes = 0
            for i, reel in enumerate(results, 1):
                views = reel['views']
                url = reel.get('url', 'N/A')
                caption = reel.get('caption', 'N/A')
                likes = reel.get('likes', 'N/A')
                post_date = reel.get('post_date', 'N/A')
                
                try:
                    numeric_views = scraper.format_view_count(views)
                    total_views += numeric_views
                    print(f"🎥 Reel {i}: {views} views (≈{numeric_views:,.0f})")
                except:
                    print(f"🎥 Reel {i}: {views} views")
                
                # Display likes
                try:
                    numeric_likes = scraper.format_likes_count(likes)
                    total_likes += numeric_likes
                    print(f"   👍 Likes: {likes} (≈{numeric_likes:,.0f})")
                except:
                    print(f"   👍 Likes: {likes}")
                
                # Display formatted post date
                print(f"   📅 Posted: {post_date}")
                
                # Display URL
                print(f"   🔗 URL: {url}")
                
                # Display caption
                if caption and caption != 'N/A':
                    # Truncate long captions for display
                    display_caption = caption[:100] + "..." if len(caption) > 100 else caption
                    print(f"   📝 Caption: {display_caption}")
                else:
                    print(f"   📝 Caption: No caption found")
                
                print("-" * 40)
            
            print("=" * 80)
            if total_views > 0:
                print(f"📈 Total estimated views: {total_views:,.0f}")
            if total_likes > 0:
                print(f"👍 Total estimated likes: {total_likes:,.0f}")
            
            # Save results
            scraper.save_results(results)
            
        else:
            logger.error("❌ No reels with view counts found!")
            print("\n🔧 Troubleshooting tips:")
            print("1. Make sure you're logged in to Instagram")
            print("2. Check if the profile has public reels")
            print("3. Try increasing the scroll count")
            print("4. The page structure might have changed")
            print("5. Try running in non-headless mode to see what's happening")
            print("6. Try setting EXTRACT_CAPTIONS = False for faster testing")
            print("7. Try setting EXTRACT_LIKES_DATES = False for faster testing")
    
    except KeyboardInterrupt:
        logger.info("⏹️ Scraping interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
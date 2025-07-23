import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
import os
import sys
from datetime import datetime
import logging
import re
from io import StringIO

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

# Import your existing modules - try different import patterns
try:
    from InstagramScraper import InstagramReelsScraper
    from InstagramDataConverter import InstagramDataConverter
except ImportError:
    try:
        from Instagram_Reels_Scraper.InstagramScraper import InstagramReelsScraper
        from Instagram_Reels_Scraper.InstagramDataConverter import InstagramDataConverter
    except ImportError:
        try:
            # If running from parent directory
            sys.path.append(os.path.join(parent_dir, 'Scraper'))
            from InstagramScraper import InstagramReelsScraper
            from InstagramDataConverter import InstagramDataConverter
        except ImportError as e:
            print(f"Error importing modules: {e}")
            print(f"Current directory: {current_dir}")
            print(f"Parent directory: {parent_dir}")
            print("Please make sure InstagramScraper.py and InstagramDataConverter.py are in the correct location")
            sys.exit(1)

class PrintCapture:
    """Capture print statements and redirect to GUI"""
    
    def __init__(self, gui_callback):
        self.gui_callback = gui_callback
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, message):
        if message.strip():  # Only capture non-empty messages
            # Send to GUI callback in a thread-safe way
            self.gui_callback(message.strip())
        # REMOVED: Don't write to original stdout to prevent duplication
        # self.original_stdout.write(message)
        
    def flush(self):
        self.original_stdout.flush()

class GUILogHandler(logging.Handler):
    """Custom logging handler to redirect logs to GUI"""
    
    def __init__(self, gui_callback):
        super().__init__()
        self.gui_callback = gui_callback
        
    def emit(self, record):
        try:
            msg = self.format(record)
            self.gui_callback(msg)
        except Exception:
            pass

class InstagramScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Reels Scraper - Professional Edition")
        self.root.geometry("950x800")  # Increased height for new controls
        self.root.configure(bg='#f0f0f0')
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Variables
        self.scraper = None
        self.converter = InstagramDataConverter()
        self.is_scraping = False
        
        # Setup console and logging capture
        self.setup_logging_and_console_capture()
        
        # Set icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.setup_ui()
        
    def setup_logging_and_console_capture(self):
        """Setup both logging and print statement capture"""
        
        # Create print capture that sends to GUI
        self.print_capture = PrintCapture(self.log_message_from_external)
        
        # Create custom log handler that sends logs to GUI
        self.gui_log_handler = GUILogHandler(self.log_message_from_external)
        
        # Set format for logs
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.gui_log_handler.setFormatter(formatter)
        
        # Only capture specific loggers to avoid duplication
        loggers_to_capture = [
            logging.getLogger('InstagramScraper'),
            logging.getLogger('selenium'),
        ]
        
        for logger in loggers_to_capture:
            # Check if handler already exists to prevent duplicates
            if not any(isinstance(h, GUILogHandler) for h in logger.handlers):
                logger.addHandler(self.gui_log_handler)
                logger.setLevel(logging.INFO)
    
    def log_message_from_external(self, message):
        """Thread-safe callback to receive messages from print statements and loggers"""
        try:
            # Use thread-safe method to update GUI
            self.root.after(0, lambda: self._update_log_text_external(message))
        except:
            pass
    
    def _update_log_text_external(self, message):
        """Thread-safe method to update log text from external sources"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Clean up the message
            clean_message = message.strip()
            
            # Skip empty messages
            if not clean_message:
                return
            
            # Skip duplicate messages (simple deduplication)
            if hasattr(self, '_last_message') and self._last_message == clean_message:
                return
            self._last_message = clean_message
            
            # Convert common log patterns to emojis
            if any(x in clean_message.lower() for x in ['error', 'failed']):
                emoji = "❌"
            elif any(x in clean_message.lower() for x in ['warning', 'warn']):
                emoji = "⚠️"
            elif any(x in clean_message.lower() for x in ['success', 'completed']):
                emoji = "✅"
            elif any(x in clean_message.lower() for x in ['info', 'found']):
                emoji = "ℹ️"
            elif any(x in clean_message.lower() for x in ['debug']):
                emoji = "🔍"
            elif any(x in clean_message.lower() for x in ['starting', 'initializing']):
                emoji = "🚀"
            elif any(x in clean_message.lower() for x in ['scrolling', 'scroll']):
                emoji = "📜"
            elif any(x in clean_message.lower() for x in ['reel']):
                emoji = "🎥"
            elif any(x in clean_message.lower() for x in ['login']):
                emoji = "🔐"
            elif any(x in clean_message.lower() for x in ['saving', 'saved']):
                emoji = "💾"
            else:
                emoji = "📝"
            
            # Remove timestamp from logger messages to avoid duplication
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}', clean_message):
                # Extract just the message part after the log level
                parts = clean_message.split(' - ', 2)
                if len(parts) >= 3:
                    clean_message = parts[2]
                elif len(parts) >= 2:
                    clean_message = parts[1]
            
            log_entry = f"[{timestamp}] {emoji} {clean_message}\n"
            
            if hasattr(self, 'log_text'):
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)
                self.root.update_idletasks()
                
        except Exception as e:
            print(f"Error updating log: {e}")  # Fallback to console
        
    def setup_ui(self):
        """Setup the user interface with better layout"""
        
        # Create a canvas and scrollbar for scrollable content
        canvas = tk.Canvas(self.root, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now use scrollable_frame instead of main_frame
        main_frame = ttk.Frame(scrollable_frame, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Configure grid weights for responsive design
        main_frame.columnconfigure(0, weight=1)
        
        # Title Section
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="Instagram Reels Scraper", 
                               font=('Arial', 18, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Extract view counts, captions, likes and dates from Instagram Reels", 
                                  font=('Arial', 10), foreground='gray')
        subtitle_label.pack()
        
        # Target Account Section
        target_frame = ttk.LabelFrame(main_frame, text="🎯 Target Account", padding="12")
        target_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        target_frame.columnconfigure(1, weight=1)
        
        ttk.Label(target_frame, text="Username:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.target_username_var = tk.StringVar(value="bankmandiri")
        self.target_username_entry = ttk.Entry(target_frame, textvariable=self.target_username_var, 
                                              width=25, font=('Arial', 11))
        self.target_username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(target_frame, text="(without @ symbol)", 
                 font=('Arial', 9), foreground='gray').grid(row=1, column=1, sticky=tk.W, pady=(2, 0))
        
        # Settings Section - Enhanced Layout
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Settings", padding="12")
        settings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # First row of settings - Scraping Method
        settings_row1 = ttk.Frame(settings_frame)
        settings_row1.pack(fill="x", pady=(0, 8))
        
        # Scraping method selection
        ttk.Label(settings_row1, text="Scraping method:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.scraping_method_var = tk.StringVar(value="scrolls")
        method_frame = ttk.Frame(settings_row1)
        method_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Radiobutton(method_frame, text="By Scrolls", variable=self.scraping_method_var, 
                       value="scrolls", command=self.on_scraping_method_change).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(method_frame, text="By Posts Count", variable=self.scraping_method_var, 
                       value="posts", command=self.on_scraping_method_change).pack(side=tk.LEFT)
        
        # Second row - Dynamic controls based on method
        settings_row2 = ttk.Frame(settings_frame)
        settings_row2.pack(fill="x", pady=(0, 8))
        
        # Scrolls setting (initially visible)
        self.scrolls_frame = ttk.Frame(settings_row2)
        self.scrolls_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(self.scrolls_frame, text="Scrolls:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.scroll_count_var = tk.IntVar(value=3)
        self.scroll_spinbox = ttk.Spinbox(self.scrolls_frame, from_=0, to=20, textvariable=self.scroll_count_var, width=6)
        self.scroll_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        
        # Posts count setting (initially hidden)
        self.posts_frame = ttk.Frame(settings_row2)
        
        ttk.Label(self.posts_frame, text="Target posts:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.posts_count_var = tk.IntVar(value=20)
        self.posts_spinbox = ttk.Spinbox(self.posts_frame, from_=1, to=100, textvariable=self.posts_count_var, width=6)
        self.posts_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delay setting
        ttk.Label(settings_row2, text="Delay:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.delay_var = tk.IntVar(value=3)
        delay_spinbox = ttk.Spinbox(settings_row2, from_=1, to=10, textvariable=self.delay_var, width=6)
        delay_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(settings_row2, text="sec", font=('Arial', 9), foreground='gray').pack(side=tk.LEFT)
        
        # Third row of settings - Checkboxes
        settings_row3 = ttk.Frame(settings_frame)
        settings_row3.pack(fill="x", pady=(0, 8))
        
        self.headless_var = tk.BooleanVar()
        ttk.Checkbutton(settings_row3, text="Headless mode", 
                       variable=self.headless_var, command=self.on_headless_change).pack(side=tk.LEFT, padx=(0, 20))
        
        self.extract_captions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_row3, text="Extract captions", 
                       variable=self.extract_captions_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.extract_likes_dates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_row3, text="Extract likes & dates", 
                       variable=self.extract_likes_dates_var).pack(side=tk.LEFT)
        
        # Fourth row - Auto-convert options
        settings_row4 = ttk.Frame(settings_frame)
        settings_row4.pack(fill="x")
        
        ttk.Label(settings_row4, text="Auto-convert to:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.auto_convert_excel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_row4, text="Excel", 
                       variable=self.auto_convert_excel_var).pack(side=tk.LEFT, padx=(0, 15))
        
        self.auto_convert_csv_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_row4, text="CSV", 
                       variable=self.auto_convert_csv_var).pack(side=tk.LEFT)
        
        # Debug mode option
        self.debug_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_row4, text="Debug mode (verbose logs)", 
                       variable=self.debug_mode_var).pack(side=tk.LEFT, padx=(20, 0))
        
        # Output Settings Section - NEW
        output_frame = ttk.LabelFrame(main_frame, text="📁 Output Settings", padding="12")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Output directory selection
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Label(dir_frame, text="Output Directory:", font=('Arial', 10, 'bold')).pack(side="left")
        
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        self.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.pack(side="left", padx=(10, 5), fill="x", expand=True)
        
        self.browse_button = ttk.Button(
            dir_frame, 
            text="Browse...", 
            command=self.browse_output_directory,
            width=12
        )
        self.browse_button.pack(side="right")
        
        # Custom filename
        filename_frame = ttk.Frame(output_frame)
        filename_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Label(filename_frame, text="Custom Filename (optional):", font=('Arial', 10, 'bold')).pack(side="left")
        self.custom_filename_var = tk.StringVar()
        ttk.Entry(filename_frame, textvariable=self.custom_filename_var, width=30).pack(side="left", padx=(10, 0))
        
        # File format options
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill="x")
        
        ttk.Label(format_frame, text="Export Formats:", font=('Arial', 10, 'bold')).pack(side="left")
        
        self.export_json_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(format_frame, text="JSON", variable=self.export_json_var).pack(side="left", padx=(10, 5))
        
        self.export_excel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(format_frame, text="Excel (.xlsx)", variable=self.export_excel_var).pack(side="left", padx=5)
        
        self.export_csv_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(format_frame, text="CSV", variable=self.export_csv_var).pack(side="left", padx=5)
        
        # Buttons Section - Better organized
        buttons_frame = ttk.LabelFrame(main_frame, text="🎛️ Controls", padding="12")
        buttons_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Main action buttons
        main_buttons = ttk.Frame(buttons_frame)
        main_buttons.pack(fill="x", pady=(0, 8))
        
        self.start_button = ttk.Button(main_buttons, text="🚀 Start Scraping", 
                                      command=self.start_scraping, width=18)
        self.start_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.stop_button = ttk.Button(main_buttons, text="⏹️ Stop", 
                                     command=self.stop_scraping, state=tk.DISABLED, width=12)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.clear_button = ttk.Button(main_buttons, text="🗑️ Clear Log", 
                                      command=self.clear_log, width=14)
        self.clear_button.pack(side=tk.LEFT)
        
        # Converter buttons
        converter_buttons = ttk.Frame(buttons_frame)
        converter_buttons.pack(fill="x", pady=(0, 8))
        
        self.convert_latest_button = ttk.Button(converter_buttons, text="📊 Convert Latest JSON", 
                                               command=self.convert_latest_json, width=25)
        self.convert_latest_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.convert_custom_button = ttk.Button(converter_buttons, text="📁 Select & Convert", 
                                               command=self.convert_custom_json, width=18)
        self.convert_custom_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # File management buttons
        file_buttons = ttk.Frame(buttons_frame)
        file_buttons.pack(fill="x")
        
        self.open_folder_button = ttk.Button(file_buttons, text="📂 Open Results Folder", 
                                            command=self.open_results_folder, width=20)
        self.open_folder_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.refresh_files_button = ttk.Button(file_buttons, text="🔄 Refresh Files", 
                                              command=self.refresh_file_list, width=16)
        self.refresh_files_button.pack(side=tk.LEFT)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progress", padding="12")
        progress_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="Ready to start scraping...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var, font=('Arial', 10))
        self.progress_label.pack(fill="x", pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x")
        
        # Results Summary Section
        results_frame = ttk.LabelFrame(main_frame, text="📈 Results Summary", padding="12")
        results_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        results_content = ttk.Frame(results_frame)
        results_content.pack(fill="x")
        
        self.reels_count_var = tk.StringVar(value="Reels: 0")
        self.total_views_var = tk.StringVar(value="Total Views: 0")
        self.total_likes_var = tk.StringVar(value="Total Likes: 0")
        
        ttk.Label(results_content, textvariable=self.reels_count_var, font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 30))
        ttk.Label(results_content, textvariable=self.total_views_var, font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 30))
        ttk.Label(results_content, textvariable=self.total_likes_var, font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        # Recent Files Section - Compact
        files_frame = ttk.LabelFrame(main_frame, text="📁 Recent Files", padding="12")
        files_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.files_listbox = tk.Listbox(files_frame, height=3, font=('Consolas', 9))
        self.files_listbox.pack(fill="x", pady=(0, 5))
        
        # Activity Log Section - Prominent
        log_frame = ttk.LabelFrame(main_frame, text="📝 Activity Log", padding="12")
        log_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=120, font=('Consolas', 9))
        self.log_text.pack(fill="both", expand=True)
        
        # Initialize file list
        self.refresh_file_list()
        
        # Add some initial help text
        self.log_message("🎯 Welcome to Instagram Reels Scraper!")
        self.log_message("📝 Quick Start Guide:")
        self.log_message("   1. Enter Instagram username (without @)")
        self.log_message("   2. Choose scraping method: By Scrolls or By Posts Count")
        self.log_message("   3. Set output directory and filename if desired")
        self.log_message("   4. Select export formats (JSON, Excel, CSV)")
        self.log_message("   5. Adjust settings if needed")
        self.log_message("   6. Click 'Start Scraping'")
        self.log_message("   7. Login when browser opens")
        self.log_message("   8. Wait for completion")
        self.log_message("✨ Ready to start!")
        
    def browse_output_directory(self):
        """Open directory browser"""
        try:
            directory = filedialog.askdirectory(
                title="Choose Output Directory",
                initialdir=self.output_dir_var.get()
            )
            if directory:
                self.output_dir_var.set(directory)
                self.log_message(f"📁 Output directory set to: {directory}")
        except Exception as e:
            self.log_message(f"❌ Error selecting directory: {e}")
        
    def on_scraping_method_change(self):
        """Handle scraping method change"""
        if self.scraping_method_var.get() == "scrolls":
            self.scrolls_frame.pack(side=tk.LEFT, padx=(0, 20))
            self.posts_frame.pack_forget()
            self.log_message("📜 Switched to scroll-based scraping")
        else:  # posts
            self.posts_frame.pack(side=tk.LEFT, padx=(0, 20))
            self.scrolls_frame.pack_forget()
            self.log_message("📊 Switched to posts count-based scraping")
        
    def on_headless_change(self):
        """Handle headless mode checkbox change"""
        if self.headless_var.get():
            response = messagebox.askquestion(
                "Headless Mode Warning",
                "Headless mode hides the browser window, but you'll still need to login manually.\n"
                "The browser will temporarily become visible during login.\n\n"
                "Continue with headless mode?",
                icon='warning'
            )
            if response == 'no':
                self.headless_var.set(False)
        
    def log_message(self, message):
        """Add GUI-specific message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("📝 Log cleared")
        # Reset last message tracking
        self._last_message = ""
        
    def update_progress(self, message):
        """Update progress message"""
        self.progress_var.set(message)
        self.root.update_idletasks()
        
    def update_results_summary(self, results):
        """Update the results summary display"""
        reels_count = len(results) if results else 0
        self.reels_count_var.set(f"Reels: {reels_count}")
        
        if results:
            try:
                total_views = sum(self.converter.convert_views_to_numeric(reel.get('views', '0')) for reel in results)
                self.total_views_var.set(f"Total Views: {total_views:,.0f}")
            except:
                self.total_views_var.set("Total Views: N/A")
            
            try:
                total_likes = sum(self.converter.convert_likes_to_numeric(reel.get('likes', '0')) for reel in results if reel.get('likes', 'N/A') != 'N/A')
                if total_likes > 0:
                    self.total_likes_var.set(f"Total Likes: {total_likes:,.0f}")
                else:
                    self.total_likes_var.set("Total Likes: N/A")
            except:
                self.total_likes_var.set("Total Likes: N/A")
        else:
            self.total_views_var.set("Total Views: 0")
            self.total_likes_var.set("Total Likes: 0")
    
    def refresh_file_list(self):
        """Refresh the list of recent files"""
        try:
            self.files_listbox.delete(0, tk.END)
            
            # Get output directory
            output_dir = self.output_dir_var.get() if hasattr(self, 'output_dir_var') else os.getcwd()
            
            # Find files in output directory
            json_files = []
            excel_files = []
            csv_files = []
            
            for file in os.listdir(output_dir):
                full_path = os.path.join(output_dir, file)
                if os.path.isfile(full_path):
                    if file.lower().endswith('.json') and 'instagram' in file.lower():
                        json_files.append(file)
                    elif file.lower().endswith('.xlsx') and 'instagram' in file.lower():
                        excel_files.append(file)
                    elif file.lower().endswith('.csv') and 'instagram' in file.lower():
                        csv_files.append(file)
            
            # Sort files by modification time (newest first)
            all_files = []
            for f in json_files + excel_files + csv_files:
                full_path = os.path.join(output_dir, f)
                if os.path.exists(full_path):
                    all_files.append((f, os.path.getmtime(full_path)))
            
            all_files.sort(key=lambda x: x[1], reverse=True)
            
            # Add to listbox
            for file_name, _ in all_files[:10]:  # Show only last 10 files
                full_path = os.path.join(output_dir, file_name)
                file_size = os.path.getsize(full_path)
                file_size_str = f"{file_size/1024:.1f} KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f} MB"
                display_text = f"{file_name} ({file_size_str})"
                self.files_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            self.log_message(f"⚠️ Error refreshing file list: {e}")
    
    def convert_latest_json(self):
        """Convert the latest JSON file to Excel/CSV"""
        try:
            self.log_message("🔄 Converting latest JSON file...")
            
            # Find latest JSON file in output directory
            output_dir = self.output_dir_var.get()
            latest_json = None
            latest_time = 0
            
            for file in os.listdir(output_dir):
                if file.lower().endswith('.json') and 'instagram' in file.lower():
                    full_path = os.path.join(output_dir, file)
                    file_time = os.path.getmtime(full_path)
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_json = full_path
            
            if not latest_json:
                self.log_message("❌ No JSON files found")
                messagebox.showwarning("No Files", f"No Instagram JSON files found in {output_dir}.")
                return
            
            self.log_message(f"📂 Found latest file: {os.path.basename(latest_json)}")
            
            # Convert with current settings
            output_excel = self.auto_convert_excel_var.get()
            output_csv = self.auto_convert_csv_var.get()
            
            if not output_excel and not output_csv:
                messagebox.showwarning("No Output Format", "Please select at least one output format (Excel or CSV).")
                return
            
            # Start conversion in thread
            thread = threading.Thread(target=self._convert_thread, args=(latest_json, output_excel, output_csv), daemon=True)
            thread.start()
            
        except Exception as e:
            error_msg = f"❌ Conversion error: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def convert_custom_json(self):
        """Let user select a JSON file to convert"""
        try:
            # File dialog to select JSON file
            json_file = filedialog.askopenfilename(
                title="Select Instagram JSON file",
                filetypes=[
                    ("Instagram JSON files", "instagram_reels_data_*.json"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ],
                initialdir=self.output_dir_var.get()
            )
            
            if not json_file:
                return
            
            self.log_message(f"📂 Selected file: {os.path.basename(json_file)}")
            
            # Convert with current settings
            output_excel = self.auto_convert_excel_var.get()
            output_csv = self.auto_convert_csv_var.get()
            
            if not output_excel and not output_csv:
                messagebox.showwarning("No Output Format", "Please select at least one output format (Excel or CSV).")
                return
            
            # Start conversion in thread
            thread = threading.Thread(target=self._convert_thread, args=(json_file, output_excel, output_csv), daemon=True)
            thread.start()
            
        except Exception as e:
            error_msg = f"❌ Conversion error: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def _convert_thread(self, json_file_path, output_excel, output_csv):
        """Conversion thread function"""
        try:
            self.update_progress("Converting data...")
            
            # Get output settings
            output_dir = self.output_dir_var.get() if self.output_dir_var.get() != os.getcwd() else None
            custom_filename = self.custom_filename_var.get().strip() if self.custom_filename_var.get().strip() else None
            
            # Convert data
            results = self.converter.convert_json_to_excel_csv(
                json_file_path=json_file_path,
                output_excel=output_excel,
                output_csv=output_csv,
                output_dir=output_dir,
                custom_filename=custom_filename
            )
            
            if results:
                self.log_message("✅ Conversion completed successfully!")
                
                created_files = []
                for file_type, file_path in results.items():
                    self.log_message(f"📁 {file_type.upper()}: {os.path.basename(file_path)}")
                    created_files.append(os.path.basename(file_path))
                
                # Refresh file list
                self.refresh_file_list()
                
                # Show success message
                messagebox.showinfo(
                    "Conversion Complete",
                    f"Successfully converted data!\n\nFiles created:\n" + 
                    "\n".join([f"• {file}" for file in created_files])
                )
                
                self.update_progress("✅ Conversion completed successfully")
            else:
                self.log_message("❌ Conversion failed")
                messagebox.showerror("Error", "Conversion failed. Check the log for details.")
                self.update_progress("❌ Conversion failed")
                
        except Exception as e:
            error_msg = f"❌ Conversion error: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            self.update_progress("❌ Conversion failed with error")
    
    def show_completion_dialog(self, output_directory, reels_count, username):
        """Show completion dialog with output location"""
        message = f"✅ Scraping completed successfully!\n\n"
        message += f"📊 Found {reels_count} reels from @{username}\n"
        message += f"📁 Files saved to:\n{output_directory}\n\n"
        message += "Would you like to open the output folder?"
        
        result = messagebox.askyesno("Scraping Complete", message)
        if result:
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(output_directory)
                elif os.name == 'posix':  # macOS/Linux
                    os.system(f'open "{output_directory}"' if sys.platform == 'darwin' else f'xdg-open "{output_directory}"')
                self.log_message(f"📁 Opened output folder: {output_directory}")
            except Exception as e:
                self.log_message(f"❌ Could not open folder: {e}")
    
    def start_scraping(self):
        """Start the scraping process with full console capture"""
        # Validate inputs
        target_username = self.target_username_var.get().strip()
        if not target_username:
            messagebox.showerror("Error", "Please enter a target username")
            return
        
        # Validate export formats
        if not (self.export_json_var.get() or self.export_excel_var.get() or self.export_csv_var.get()):
            messagebox.showerror("Error", "Please select at least one export format")
            return
            
        # Confirm before starting
        auto_convert_text = []
        if self.auto_convert_excel_var.get():
            auto_convert_text.append("Excel")
        if self.auto_convert_csv_var.get():
            auto_convert_text.append("CSV")
        
        auto_convert_str = f"\n• Auto-convert to: {', '.join(auto_convert_text)}" if auto_convert_text else "\n• Auto-convert: No"
        
        # Get output settings info
        output_dir = self.output_dir_var.get()
        output_info = f"• Output directory: {output_dir}"
        custom_filename = self.custom_filename_var.get().strip()
        if custom_filename:
            output_info += f"\n• Custom filename: {custom_filename}"
        
        # Get export formats
        export_formats = []
        if self.export_json_var.get():
            export_formats.append("JSON")
        if self.export_excel_var.get():
            export_formats.append("Excel")
        if self.export_csv_var.get():
            export_formats.append("CSV")
        export_info = f"• Export formats: {', '.join(export_formats)}" if export_formats else "• Export formats: None"
        
        # Display different settings based on scraping method
        if self.scraping_method_var.get() == "scrolls":
            method_info = f"• Scrolls: {self.scroll_count_var.get()}"
        else:
            method_info = f"• Target posts: {self.posts_count_var.get()}"
        
        response = messagebox.askyesno(
            "Confirm Scraping",
            f"Start scraping reels from @{target_username}?\n\n"
            f"Settings:\n"
            f"• Method: {self.scraping_method_var.get().title()}\n"
            f"{method_info}\n"
            f"• Extract captions: {'Yes' if self.extract_captions_var.get() else 'No'}\n"
            f"• Extract likes & dates: {'Yes' if self.extract_likes_dates_var.get() else 'No'}\n"
            f"• Headless mode: {'Yes' if self.headless_var.get() else 'No'}\n"
            f"• Debug mode: {'Yes' if self.debug_mode_var.get() else 'No'}\n\n"
            f"Output Settings:\n"
            f"{output_info}\n"
            f"{export_info}"
            f"{auto_convert_str}"
        )
        
        if not response:
            return
        
        # Disable start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_scraping = True
        
        # Start progress bar
        self.progress_bar.start(10)
        
        # Clear previous results
        self.update_results_summary([])
        
        self.log_message("🚀 Starting scraping process...")
        
        # Redirect print statements to GUI
        sys.stdout = self.print_capture
        sys.stderr = self.print_capture
        
        # Set debug mode if enabled
        if self.debug_mode_var.get():
            logging.getLogger().setLevel(logging.DEBUG)
            self.log_message("🔍 Debug mode enabled - showing verbose logs")
        else:
            logging.getLogger().setLevel(logging.INFO)
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=self._scraping_thread, daemon=True)
        thread.start()
        
    def _scraping_thread(self):
        """Enhanced scraping thread that captures all output"""
        try:
            self.log_message("🔧 Initializing Instagram scraper...")
            self.update_progress("Setting up scraper...")
            
            # Get parameters
            target_username = self.target_username_var.get().strip()
            delay = self.delay_var.get()
            extract_captions = self.extract_captions_var.get()
            extract_likes_dates = self.extract_likes_dates_var.get()
            headless = self.headless_var.get()
            
            # Get output settings
            output_dir = self.output_dir_var.get() if self.output_dir_var.get() != os.getcwd() else None
            custom_filename = self.custom_filename_var.get().strip() if self.custom_filename_var.get().strip() else None
            
            # Get scraping parameters based on method
            if self.scraping_method_var.get() == "scrolls":
                scroll_count = self.scroll_count_var.get()
                target_posts = None
                self.log_message(f"📜 Scraping method: By scrolls ({scroll_count} scrolls)")
            else:
                scroll_count = None
                target_posts = self.posts_count_var.get()
                self.log_message(f"📊 Scraping method: By posts count (target: {target_posts} posts)")
            
            self.log_message(f"🎯 Target username: {target_username}")
            self.log_message(f"⏱️ Delay: {delay} seconds")
            self.log_message(f"📝 Extract captions: {'Yes' if extract_captions else 'No'}")
            self.log_message(f"📊 Extract likes & dates: {'Yes' if extract_likes_dates else 'No'}")
            self.log_message(f"👻 Headless mode: {'Yes' if headless else 'No'}")
            self.log_message(f"📁 Output directory: {output_dir or 'Current directory'}")
            if custom_filename:
                self.log_message(f"📝 Custom filename: {custom_filename}")
            
            # Initialize scraper
            self.scraper = InstagramReelsScraper(headless=headless)
            
            # All the print statements from InstagramScraper will now appear in the GUI log
            self.update_progress("Setting up Chrome driver...")
            if not self.scraper.setup_driver():
                self.log_message("❌ Failed to setup Chrome driver")
                self._scraping_finished()
                return
            
            # Login process
            self.update_progress("Waiting for login...")
            self.log_message("🔐 Please complete login in the browser...")
            
            if not self.scraper.manual_login():
                self.log_message("❌ Login failed or timed out")
                self._scraping_finished()
                return
            
            # Start scraping - all print output will be captured
            self.update_progress("Scraping reels...")
            self.log_message("🎬 Starting to scrape reels...")
            
            # Call scraping method based on user choice
            if self.scraping_method_var.get() == "scrolls":
                # Traditional scroll-based scraping
                results = self.scraper.scrape_reels_views(
                    target_username=target_username,
                    max_scrolls=scroll_count,
                    delay=delay,
                    extract_captions=extract_captions,
                    extract_likes_dates=extract_likes_dates
                )
            else:
                # Posts count-based scraping
                results = self.scraper.scrape_reels_by_count(
                    target_username=target_username,
                    target_posts=target_posts,
                    delay=delay,
                    extract_captions=extract_captions,
                    extract_likes_dates=extract_likes_dates
                )
            
            if results:
                self.log_message(f"✅ Scraping completed! Found {len(results)} reels")
                
                # Save JSON if requested
                if self.export_json_var.get():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    if custom_filename:
                        json_filename = f"{custom_filename}_{timestamp}.json"
                    else:
                        json_filename = f"instagram_reels_data_{target_username}_{timestamp}.json"
                    
                    # Save with custom directory
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)
                        json_filepath = os.path.join(output_dir, json_filename)
                    else:
                        json_filepath = json_filename
                    
                    # Save results
                    with open(json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    self.log_message(f"💾 JSON saved: {json_filepath}")
                
                # Auto-convert if enabled
                if (self.export_excel_var.get() and self.auto_convert_excel_var.get()) or \
                   (self.export_csv_var.get() and self.auto_convert_csv_var.get()):
                    self.log_message("🔄 Auto-converting results...")
                    self.update_progress("Converting to Excel/CSV...")
                    
                    try:
                        # Use the converter with output directory
                        if self.export_excel_var.get() and self.auto_convert_excel_var.get():
                            excel_path = self.converter.convert_to_excel(results, output_dir, custom_filename)
                            if excel_path:
                                self.log_message(f"📊 Excel saved: {excel_path}")
                        
                        if self.export_csv_var.get() and self.auto_convert_csv_var.get():
                            csv_path = self.converter.convert_to_csv(results, output_dir, custom_filename)
                            if csv_path:
                                self.log_message(f"📄 CSV saved: {csv_path}")
                        
                        self.log_message("✅ Auto-conversion completed!")
                        
                    except Exception as e:
                        self.log_message(f"⚠️ Auto-conversion error: {e}")
                
                # Display summary
                self.log_message("📊 Results Summary:")
                total_views = 0
                total_likes = 0
                
                for i, reel in enumerate(results[:5], 1):  # Show first 5 reels in detail
                    views = reel.get('views', 'N/A')
                    likes = reel.get('likes', 'N/A')
                    date = reel.get('post_date', 'N/A')
                    
                    self.log_message(f"   🎥 Reel {i}: {views} views, {likes} likes, Posted: {date}")
                    
                    # Calculate totals for summary
                    try:
                        if views != 'N/A':
                            total_views += self.converter.convert_views_to_numeric(views)
                    except:
                        pass
                    
                    try:
                        if likes != 'N/A':
                            total_likes += self.converter.convert_likes_to_numeric(likes)
                    except:
                        pass
                
                if len(results) > 5:
                    self.log_message(f"   ... and {len(results) - 5} more reels")
                
                if total_views > 0:
                    self.log_message(f"📈 Total estimated views: {total_views:,.0f}")
                if total_likes > 0:
                    self.log_message(f"👍 Total estimated likes: {total_likes:,.0f}")
                
                # Update GUI summary
                self.update_results_summary(results)
                
                # Refresh file list
                self.refresh_file_list()
                
                self.update_progress(f"✅ Completed! Found {len(results)} reels")
                
                # Show completion message with output location
                output_location = output_dir if output_dir else os.getcwd()
                self.show_completion_dialog(output_location, len(results), target_username)
                
            else:
                self.log_message("❌ No reels found or scraping failed")
                self.update_progress("❌ Scraping failed")
                messagebox.showwarning(
                    "No Results",
                    "No reels were found. Check the log for details."
                )
                
        except Exception as e:
            self.log_message(f"❌ Unexpected error: {str(e)}")
            self.update_progress("❌ Error occurred")
            messagebox.showerror("Error", f"An error occurred:\n\n{str(e)}")
            
        finally:
            self._scraping_finished()
            
    def _scraping_finished(self):
        """Clean up after scraping"""
        # Restore original stdout/stderr
        sys.stdout = self.print_capture.original_stdout
        sys.stderr = self.print_capture.original_stderr
        
        # Close scraper
        if self.scraper:
            try:
                self.scraper.close()
            except:
                pass
        
        # Update UI
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        self.log_message("🏁 Scraping process finished")
                
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.is_scraping:
            response = messagebox.askyesno(
                "Stop Scraping",
                "Are you sure you want to stop the scraping process?"
            )
            if response:
                self.log_message("⏹️ Stopping scraper...")
                self.is_scraping = False
                self._scraping_finished()
                
    def open_results_folder(self):
        """Open the folder containing result files"""
        try:
            output_dir = self.output_dir_var.get()
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{output_dir}"' if sys.platform == 'darwin' else f'xdg-open "{output_dir}"')
            self.log_message(f"📁 Opened results folder: {output_dir}")
        except Exception as e:
            self.log_message(f"❌ Failed to open folder: {e}")
            messagebox.showerror("Error", f"Failed to open results folder:\n{e}")

def main():
    """Main function"""
    root = tk.Tk()
    app = InstagramScraperGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application interrupted")
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")

if __name__ == "__main__":
    main()
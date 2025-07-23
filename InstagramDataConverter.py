import json
import pandas as pd
import os
import glob
import re  # Add this line
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstagramDataConverter:
    def __init__(self):
        """Initialize the Instagram data converter"""
        pass
    
    def load_json_data(self, json_file_path):
        """
        Load JSON data from file
        
        Args:
            json_file_path (str): Path to the JSON file
            
        Returns:
            list: List of dictionaries containing Instagram data
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ Successfully loaded {len(data)} records from {json_file_path}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to load JSON file: {e}")
            return []
    
    def convert_views_to_numeric(self, view_str):
        """Convert view count string to numeric value"""
        if not view_str or view_str == 'N/A':
            return 0
        
        try:
            # Remove any whitespace
            view_str = str(view_str).strip()
            
            # Handle K, M, B notation
            if 'K' in view_str:
                return float(view_str.replace('K', '').replace(',', '')) * 1000
            elif 'M' in view_str:
                return float(view_str.replace('M', '').replace(',', '')) * 1000000
            elif 'B' in view_str:
                return float(view_str.replace('B', '').replace(',', '')) * 1000000000
            else:
                # Handle comma-separated numbers
                return float(view_str.replace(',', ''))
        except:
            return 0
    
    def convert_likes_to_numeric(self, likes_str):
        """Convert likes count string to numeric value"""
        if not likes_str or likes_str == 'N/A':
            return 0
        
        try:
            # Remove any whitespace and "likes" text
            likes_str = str(likes_str).strip()
            
            # Remove "likes" word if present (case insensitive)
            likes_str = re.sub(r'\s*likes?\s*$', '', likes_str, flags=re.IGNORECASE).strip()
            
            # Handle K, M, B notation
            if 'K' in likes_str.upper():
                return float(likes_str.upper().replace('K', '').replace(',', '')) * 1000
            elif 'M' in likes_str.upper():
                return float(likes_str.upper().replace('M', '').replace(',', '')) * 1000000
            elif 'B' in likes_str.upper():
                return float(likes_str.upper().replace('B', '').replace(',', '')) * 1000000000
            else:
                # Handle comma-separated numbers
                return float(likes_str.replace(',', ''))
        except:
            return 0
    
    def process_data(self, data):
        """
        Process and clean the Instagram data
        
        Args:
            data (list): Raw Instagram data
            
        Returns:
            pandas.DataFrame: Processed data as DataFrame
        """
        processed_data = []
        
        for item in data:
            try:
                # Extract basic information
                processed_item = {
                    'Reel_Index': item.get('reel_index', ''),
                    'Views_Raw': item.get('views', 'N/A'),
                    'Views_Numeric': self.convert_views_to_numeric(item.get('views', 'N/A')),
                    'Likes_Raw': item.get('likes', 'N/A'),
                    'Likes_Numeric': self.convert_likes_to_numeric(item.get('likes', 'N/A')),
                    'Post_Date': item.get('post_date', 'N/A'),
                    'Post_Date_Raw': item.get('post_date_raw', 'N/A'),
                    'URL': item.get('url', 'N/A'),
                    'Caption': item.get('caption', ''),
                    'Timestamp_Scraped': item.get('timestamp', ''),
                    'Selector_Used': item.get('selector_used', ''),
                }
                
                # Extract position data if available
                position = item.get('position', {})
                if position:
                    processed_item['Position_Row'] = position.get('row', 0)
                    processed_item['Position_Col'] = position.get('col', 0)
                else:
                    processed_item['Position_Row'] = 0
                    processed_item['Position_Col'] = 0
                
                processed_data.append(processed_item)
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing item: {e}")
                continue
        
        # Create DataFrame
        df = pd.DataFrame(processed_data)
        
        # Sort by reel index
        if 'Reel_Index' in df.columns:
            df = df.sort_values('Reel_Index').reset_index(drop=True)
        
        logger.info(f"✅ Processed {len(df)} records successfully")
        return df
    
    def save_to_excel(self, df, filename=None, output_dir=None):
        """
        Save DataFrame to Excel file
        
        Args:
            df (pandas.DataFrame): Data to save
            filename (str): Output filename (optional)
            output_dir (str): Output directory (optional)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_reels_data_{timestamp}.xlsx"
        
        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename = f"{filename}.xlsx"
        
        # Use provided output directory or current directory
        if output_dir:
            # Ensure directory exists
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        try:
            # Create Excel writer with formatting
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Write main data
                df.to_excel(writer, sheet_name='Instagram_Reels_Data', index=False)
                
                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Instagram_Reels_Data']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    # Set column width (max 50 characters)
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Create summary sheet
                summary_data = {
                    'Metric': [
                        'Total Reels',
                        'Total Views',
                        'Total Likes',
                        'Average Views per Reel',
                        'Average Likes per Reel',
                        'Max Views',
                        'Max Likes',
                        'Scraped At'
                    ],
                    'Value': [
                        len(df),
                        df['Views_Numeric'].sum(),
                        df['Likes_Numeric'].sum(),
                        df['Views_Numeric'].mean(),
                        df['Likes_Numeric'].mean(),
                        df['Views_Numeric'].max(),
                        df['Likes_Numeric'].max(),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Auto-adjust summary sheet columns
                summary_worksheet = writer.sheets['Summary']
                for column in summary_worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 30)
                    summary_worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"📊 Excel file saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save Excel file: {e}")
            return None
    
    def save_to_csv(self, df, filename=None, output_dir=None):
        """
        Save DataFrame to CSV file
        
        Args:
            df (pandas.DataFrame): Data to save
            filename (str): Output filename (optional)
            output_dir (str): Output directory (optional)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_reels_data_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename = f"{filename}.csv"
        
        # Use provided output directory or current directory
        if output_dir:
            # Ensure directory exists
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        try:
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"📄 CSV file saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"❌ Failed to save CSV file: {e}")
            return None
    
    def find_latest_json_file(self, directory="."):
        """
        Find the latest JSON file in the specified directory
        
        Args:
            directory (str): Directory to search in
            
        Returns:
            str: Path to the latest JSON file
        """
        try:
            # Look for Instagram JSON files
            pattern = os.path.join(directory, "instagram_reels_data_*.json")
            json_files = glob.glob(pattern)
            
            if not json_files:
                logger.warning("⚠️ No Instagram JSON files found")
                return None
            
            # Get the most recent file
            latest_file = max(json_files, key=os.path.getctime)
            logger.info(f"🔍 Found latest JSON file: {latest_file}")
            return latest_file
            
        except Exception as e:
            logger.error(f"❌ Error finding JSON files: {e}")
            return None
    
    def convert_json_to_excel_csv(self, json_file_path=None, output_excel=True, output_csv=True, output_dir=None, custom_filename=None):
        """
        Main conversion function
        
        Args:
            json_file_path (str): Path to JSON file (if None, finds latest)
            output_excel (bool): Whether to create Excel file
            output_csv (bool): Whether to create CSV file
            output_dir (str): Output directory (optional)
            custom_filename (str): Custom filename without extension (optional)
            
        Returns:
            dict: Dictionary with paths to created files
        """
        try:
            # Find JSON file if not provided
            if json_file_path is None:
                json_file_path = self.find_latest_json_file()
                if json_file_path is None:
                    logger.error("❌ No JSON file found")
                    return None
            
            # Load and process data
            raw_data = self.load_json_data(json_file_path)
            if not raw_data:
                logger.error("❌ No data loaded from JSON file")
                return None
            
            # Process data
            df = self.process_data(raw_data)
            if df.empty:
                logger.error("❌ No data to convert")
                return None
            
            # Generate base filename
            if custom_filename:
                base_name = custom_filename
            else:
                base_name = os.path.splitext(os.path.basename(json_file_path))[0]
            
            results = {}
            
            # Save to Excel
            if output_excel:
                excel_filename = f"{base_name}.xlsx"
                excel_path = self.save_to_excel(df, excel_filename, output_dir)
                if excel_path:
                    results['excel'] = excel_path
            
            # Save to CSV
            if output_csv:
                csv_filename = f"{base_name}.csv"
                csv_path = self.save_to_csv(df, csv_filename, output_dir)
                if csv_path:
                    results['csv'] = csv_path
            
            # Print summary
            output_location = output_dir if output_dir else "current directory"
            logger.info(f"\n📊 Conversion Summary:")
            logger.info(f"   📁 Source JSON: {json_file_path}")
            logger.info(f"   📊 Total Reels: {len(df)}")
            logger.info(f"   👁️ Total Views: {df['Views_Numeric'].sum():,.0f}")
            logger.info(f"   👍 Total Likes: {df['Likes_Numeric'].sum():,.0f}")
            logger.info(f"   📁 Output Location: {output_location}")
            
            if results:
                logger.info(f"   📁 Output Files:")
                for file_type, file_path in results.items():
                    logger.info(f"      {file_type.upper()}: {file_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Conversion failed: {e}")
            return None
        
    def convert_to_excel(self, json_data, output_dir=None, custom_filename=None):
        """
        Convert JSON data directly to Excel (for use with scraper)
        
        Args:
            json_data (list): List of dictionaries containing scraped data
            output_dir (str): Output directory (optional)
            custom_filename (str): Custom filename without extension (optional)
            
        Returns:
            str: Path to created Excel file
        """
        try:
            if not json_data:
                logger.error("No data to convert")
                return None
            
            # Process data
            df = self.process_data(json_data)
            if df.empty:
                logger.error("No data to convert after processing")
                return None
            
            # Generate filename
            if custom_filename:
                filename = custom_filename if custom_filename.endswith('.xlsx') else f"{custom_filename}.xlsx"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"instagram_reels_data_{timestamp}.xlsx"
            
            # Save to Excel
            return self.save_to_excel(df, filename, output_dir)
            
        except Exception as e:
            logger.error(f"❌ Error converting to Excel: {e}")
            return None

    def convert_to_csv(self, json_data, output_dir=None, custom_filename=None):
        """
        Convert JSON data directly to CSV (for use with scraper)
        
        Args:
            json_data (list): List of dictionaries containing scraped data
            output_dir (str): Output directory (optional)
            custom_filename (str): Custom filename without extension (optional)
            
        Returns:
            str: Path to created CSV file
        """
        try:
            if not json_data:
                logger.error("No data to convert")
                return None
            
            # Process data
            df = self.process_data(json_data)
            if df.empty:
                logger.error("No data to convert after processing")
                return None
            
            # Generate filename
            if custom_filename:
                filename = custom_filename if custom_filename.endswith('.csv') else f"{custom_filename}.csv"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"instagram_reels_data_{timestamp}.csv"
            
            # Save to CSV
            return self.save_to_csv(df, filename, output_dir)
            
        except Exception as e:
            logger.error(f"❌ Error converting to CSV: {e}")
            return None       

def main():
    """Main function to run the converter"""
    print("🔄 Instagram JSON to Excel/CSV Converter")
    print("=" * 50)
    
    # Initialize converter
    converter = InstagramDataConverter()
    
    # Configuration
    JSON_FILE_PATH = None  # Set to specific file path or None to auto-find latest
    OUTPUT_EXCEL = True    # Set to False to skip Excel output
    OUTPUT_CSV = True      # Set to False to skip CSV output
    
    # Convert data
    results = converter.convert_json_to_excel_csv(
        json_file_path=JSON_FILE_PATH,
        output_excel=OUTPUT_EXCEL,
        output_csv=OUTPUT_CSV
    )
    
    if results:
        print("\n✅ Conversion completed successfully!")
        print("\n📁 Created files:")
        for file_type, file_path in results.items():
            print(f"   {file_type.upper()}: {file_path}")
    else:
        print("\n❌ Conversion failed!")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure JSON file exists in the current directory")
        print("2. Check that the JSON file has the correct format")
        print("3. Ensure you have write permissions in the current directory")

if __name__ == "__main__":
    main()
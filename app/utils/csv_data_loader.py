import pandas as pd
import datetime
import os
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CSVDataLoader:
    """
    Loads and manages medical sensor data from CSV files.
    Supports various medical sensor types: ACC, BVP, Dexcom, EDA, TEMP, IBI, HR, Food Log
    """
    
    def __init__(self, data_directory: str):
        """
        Initialize the CSV data loader.
        
        Args:
            data_directory: Path to directory containing CSV files
        """
        self.data_directory = data_directory
        self.loaded_data: Dict[str, pd.DataFrame] = {}
        self.current_indices: Dict[str, int] = {}
        
    def load_csv_file(self, sensor_type: str, file_path: str) -> bool:
        """
        Load a CSV file for a specific sensor type.
        
        Args:
            sensor_type: Type of sensor (ACC, BVP, Dexcom, EDA, TEMP, IBI, HR, Food Log)
            file_path: Path to the CSV file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
                
            df = pd.read_csv(file_path)
            
            # Validate and process data based on sensor type
            processed_df = self._validate_and_process_data(sensor_type, df)
            if processed_df is None:
                return False
                
            self.loaded_data[sensor_type] = processed_df
            self.current_indices[sensor_type] = 0
            
            logger.info(f"Successfully loaded {len(processed_df)} records for {sensor_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {str(e)}")
            return False
    
    def _validate_and_process_data(self, sensor_type: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and process data based on sensor type.
        
        Args:
            sensor_type: Type of sensor
            df: DataFrame to validate and process
            
        Returns:
            Processed DataFrame if validation passed, None otherwise
        """
        try:
            if sensor_type == "ACC":
                # ACC data should have Timestamp, X, Y, Z columns
                required_cols = ['Timestamp', 'X', 'Y', 'Z']
                if not all(col in df.columns for col in required_cols):
                    logger.error(f"ACC data missing required columns: {required_cols}")
                    return None
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                
            elif sensor_type in ["BVP", "Dexcom", "EDA", "TEMP", "IBI", "HR"]:
                # These sensors should have Timestamp and Value columns
                # Handle both 'datetime' and 'Timestamp' column names
                timestamp_col = None
                value_col = None
                
                if 'Timestamp' in df.columns:
                    timestamp_col = 'Timestamp'
                elif 'datetime' in df.columns:
                    timestamp_col = 'datetime'
                    df = df.rename(columns={'datetime': 'Timestamp'})
                
                if 'Value' in df.columns:
                    value_col = 'Value'
                elif len(df.columns) >= 2:
                    # Use the second column as value if no 'Value' column
                    second_col = df.columns[1]
                    df = df.rename(columns={second_col: 'Value'})
                    value_col = 'Value'
                
                if not ('Timestamp' in df.columns and 'Value' in df.columns):
                    logger.error(f"{sensor_type} data missing required columns. Found: {list(df.columns)}")
                    return None
                    
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                
            elif sensor_type == "Food Log":
                # Food Log has multiple columns
                required_cols = ['date', 'time_of_day', 'logged_food', 'calorie', 'total_carb', 'protein', 'total_fat']
                if not all(col in df.columns for col in required_cols):
                    logger.error(f"Food Log data missing some required columns")
                    return None
                df['date'] = pd.to_datetime(df['date'])
                
            else:
                logger.error(f"Unknown sensor type: {sensor_type}")
                return None
                
            # Sort by timestamp
            timestamp_col = 'Timestamp' if 'Timestamp' in df.columns else 'date'
            df = df.sort_values(by=timestamp_col).reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error validating data for {sensor_type}: {str(e)}")
            return None
    
    def get_next_data_point(self, sensor_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the next data point for a specific sensor type.
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            Dictionary containing the data point, or None if no more data
        """
        if sensor_type not in self.loaded_data:
            logger.warning(f"No data loaded for sensor type: {sensor_type}")
            return None
            
        df = self.loaded_data[sensor_type]
        current_index = self.current_indices[sensor_type]
        
        if current_index >= len(df):
            # Reset to beginning for continuous simulation
            self.current_indices[sensor_type] = 0
            current_index = 0
            
        row = df.iloc[current_index]
        self.current_indices[sensor_type] = current_index + 1
        
        # Convert row to dictionary based on sensor type
        return self._row_to_dict(sensor_type, row)
    
    def _row_to_dict(self, sensor_type: str, row: pd.Series) -> Dict[str, Any]:
        """
        Convert a DataFrame row to a dictionary based on sensor type.
        
        Args:
            sensor_type: Type of sensor
            row: DataFrame row
            
        Returns:
            Dictionary representation of the data point
        """
        if sensor_type == "ACC":
            return {
                'timestamp': row['Timestamp'],
                'x': float(row['X']),
                'y': float(row['Y']),
                'z': float(row['Z'])
            }
        elif sensor_type in ["BVP", "Dexcom", "EDA", "TEMP", "IBI", "HR"]:
            return {
                'timestamp': row['Timestamp'],
                'value': float(row['Value'])
            }
        elif sensor_type == "Food Log":
            return {
                'date': row['date'],
                'time_of_day': row.get('time_of_day', ''),
                'logged_food': row.get('logged_food', ''),
                'calorie': float(row.get('calorie', 0)),
                'total_carb': float(row.get('total_carb', 0)),
                'protein': float(row.get('protein', 0)),
                'total_fat': float(row.get('total_fat', 0))
            }
        
        return {}
    
    def get_data_count(self, sensor_type: str) -> int:
        """
        Get the total number of data points for a sensor type.
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            Number of data points
        """
        if sensor_type not in self.loaded_data:
            return 0
        return len(self.loaded_data[sensor_type])
    
    def reset_index(self, sensor_type: str):
        """
        Reset the current index for a sensor type to start from beginning.
        
        Args:
            sensor_type: Type of sensor
        """
        if sensor_type in self.current_indices:
            self.current_indices[sensor_type] = 0
    
    def get_available_sensor_types(self) -> List[str]:
        """
        Get list of available sensor types that have been loaded.
        
        Returns:
            List of sensor type names
        """
        return list(self.loaded_data.keys())
    
    def auto_load_directory(self) -> Dict[str, bool]:
        """
        Automatically load all CSV files from the data directory.
        Attempts to detect sensor type from filename.
        
        Returns:
            Dictionary mapping sensor types to load success status
        """
        results = {}
        
        if not os.path.exists(self.data_directory):
            logger.error(f"Data directory not found: {self.data_directory}")
            return results
            
        for filename in os.listdir(self.data_directory):
            if filename.lower().endswith('.csv'):
                file_path = os.path.join(self.data_directory, filename)
                
                # Try to detect sensor type from filename
                sensor_type = self._detect_sensor_type_from_filename(filename)
                
                if sensor_type:
                    results[sensor_type] = self.load_csv_file(sensor_type, file_path)
                else:
                    logger.warning(f"Could not detect sensor type from filename: {filename}")
                    
        return results
    
    def _detect_sensor_type_from_filename(self, filename: str) -> Optional[str]:
        """
        Detect sensor type from filename.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            Detected sensor type or None
        """
        filename_lower = filename.lower()
        
        if 'acc' in filename_lower:
            return 'ACC'
        elif 'bvp' in filename_lower:
            return 'BVP'
        elif 'dexcom' in filename_lower or 'glucose' in filename_lower:
            return 'Dexcom'
        elif 'eda' in filename_lower:
            return 'EDA'
        elif 'temp' in filename_lower:
            return 'TEMP'
        elif 'ibi' in filename_lower:
            return 'IBI'
        elif 'hr' in filename_lower or 'heart' in filename_lower:
            return 'HR'
        elif 'food' in filename_lower:
            return 'Food Log'
            
        return None

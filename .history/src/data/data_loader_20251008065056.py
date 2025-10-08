"""
Data Loader Worker for Time Graph Application

Handles threaded data loading from CSV/Excel files with Polars.
Includes robust data cleaning and time column processing.
"""

import logging
import os
import numpy as np
import polars as pl
from PyQt5.QtCore import QObject, pyqtSignal as Signal

logger = logging.getLogger(__name__)


class DataLoader(QObject):
    """
    Worker class for loading data in a separate thread.
    
    Features:
    - Threaded CSV/Excel loading
    - Parquet caching for performance
    - Robust data cleaning
    - Time column processing
    """
    
    finished = Signal(object, str)  # DataFrame, time_column
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, settings: dict):
        super().__init__()
        self.settings = settings
        self._datetime_converted = False
        
        # PERFORMANCE: Parquet cache manager
        from src.data.data_cache_manager import DataCacheManager
        self.cache_manager = DataCacheManager()

    def run(self):
        """Start the data loading process."""
        try:
            df = self._load_data()
            time_column = self.settings.get('time_column')
            self.finished.emit(df, time_column)
        except FileNotFoundError as e:
            self.error.emit(f"Dosya bulunamadı: {e.filename if hasattr(e, 'filename') else str(e)}")
        except ValueError as e:
            self.error.emit(f"Veri formatı hatası: {e}")
        except Exception as e:
            self.error.emit(f"Beklenmedik bir hata oluştu: {e}")
            logger.exception("Data loading error:")

    def _load_data(self):
        """Main data loading logic."""
        file_path = self.settings['file_path']
        
        # Determine loading method by file extension
        file_ext = os.path.splitext(file_path)[1].lower()

        # Prepare Polars reading settings
        header_row = self.settings.get('header_row')
        start_row = self.settings.get('start_row', 0)
        
        has_header = header_row is not None
        skip_rows = start_row if not has_header else start_row - (header_row + 1)
        
        # CSV reading options - ROBUST MODE
        csv_opts = {
            'encoding': self.settings.get('encoding', 'latin-1'),
            'separator': self.settings.get('delimiter', ','),
            'has_header': has_header,
            'skip_rows': skip_rows,
            'ignore_errors': True,
            'try_parse_dates': False,
            'null_values': ['', 'NULL', 'null', 'None', 'NA', 'N/A', 'nan', 'NaN', '-'],
            'infer_schema_length': 10000,
            'quote_char': '"'  # Handle quoted fields properly
        }
        
        # Excel reading options
        excel_opts = {
            'has_header': has_header,
            'skip_rows': skip_rows
        }

        if file_ext == '.csv':
            try:
                self.progress.emit("CSV yükleniyor (cache kontrolü)...")
                
                # Try cache first
                df = self.cache_manager.load_with_cache(
                    file_path,
                    infer_schema_length=10000
                )
                
                if df is None:
                    logger.warning("Cache failed, falling back to direct CSV read")
                    df = pl.read_csv(file_path, **csv_opts)
                    
            except Exception as e:
                raise ValueError(f"CSV dosyası okunamadı. Ayarları kontrol edin. Hata: {e}")
                
        elif file_ext in ['.xlsx', '.xls']:
            try:
                df = pl.read_excel(file_path, **excel_opts)
            except Exception as e:
                raise ValueError(f"Excel dosyası okunamadı. Dosya bozuk olabilir. Hata: {e}")
        else:
            # Try as CSV for unsupported formats
            try:
                df = pl.read_csv(file_path, **csv_opts)
            except Exception as e:
                raise ValueError(f"Desteklenmeyen dosya formatı: {file_ext}. Sadece CSV ve Excel dosyaları desteklenmektedir.")
        
        if df is None or df.height == 0:
            raise ValueError("Dosya boş veya okunamadı")
        
        # ROBUST: Data cleaning and standardization
        df = self._sanitize_dataframe(df)
        
        # Time column processing
        if self.settings.get('create_custom_time', False):
            df = self._create_custom_time_column(df, self.settings)
        else:
            df = self._use_existing_time_column(df, self.settings)

        # Update time column in settings if auto-generated
        time_col_setting = self.settings.get('time_column')
        if not time_col_setting and self.settings.get('create_custom_time', False):
            self.settings['time_column'] = self.settings.get('new_time_column_name', 'time_generated')
        elif not time_col_setting:
            self.settings['time_column'] = 'time'

        return df
    
    def _sanitize_dataframe(self, df):
        """Clean and robustify the dataframe."""
        try:
            logger.info("[DATA CLEANING] Starting data cleaning...")
            
            df = self._clean_column_names(df)
            df = self._fix_mixed_type_columns(df)
            df = self._handle_null_values(df)
            df = self._clean_infinite_values(df)
            
            logger.info(f"[DATA CLEANING] Data cleaning complete: {df.height} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.warning(f"Data cleaning error: {e}")
            return df
    
    def _clean_column_names(self, df):
        """Clean and standardize column names."""
        try:
            new_names = {}
            for col in df.columns:
                clean_name = str(col).strip()
                
                # Prevent duplicate names
                if clean_name in new_names.values():
                    counter = 1
                    while f"{clean_name}_{counter}" in new_names.values():
                        counter += 1
                    clean_name = f"{clean_name}_{counter}"
                new_names[col] = clean_name
            
            if new_names != {col: col for col in df.columns}:
                df = df.rename(new_names)
                logger.debug(f"Column names cleaned: {len(new_names)} columns")
            
            return df
        except Exception as e:
            logger.warning(f"Column name cleaning error: {e}")
            return df
    
    def _fix_mixed_type_columns(self, df):
        """Fix mixed type columns (string + number)."""
        try:
            for col in df.columns:
                dtype = df[col].dtype
                
                if dtype == pl.Utf8:
                    try:
                        numeric_col = df[col].cast(pl.Float64, strict=False)
                        
                        null_count_before = df[col].null_count()
                        null_count_after = numeric_col.null_count()
                        
                        success_rate = 1 - ((null_count_after - null_count_before) / df.height)
                        if success_rate > 0.8:
                            df = df.with_columns(numeric_col.alias(col))
                            logger.debug(f"'{col}' converted to numeric ({success_rate*100:.1f}% success)")
                    except:
                        pass
                        
            return df
            
        except Exception as e:
            logger.warning(f"Mixed type fix error: {e}")
            return df
    
    def _handle_null_values(self, df):
        """Intelligently handle NULL values."""
        try:
            for col in df.columns:
                dtype = df[col].dtype
                null_count = df[col].null_count()
                
                if null_count > 0 and dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]:
                    null_pct = (null_count / df.height) * 100
                    
                    if null_pct < 50:
                        try:
                            df = df.with_columns(
                                df[col].fill_null(strategy="forward").fill_null(0.0).alias(col)
                            )
                            logger.debug(f"'{col}' fixed {null_count} NULL values")
                        except:
                            df = df.with_columns(df[col].fill_null(0.0).alias(col))
                    else:
                        logger.warning(f"'{col}' has too many NULLs ({null_pct:.1f}%), left as is")
            
            return df
            
        except Exception as e:
            logger.warning(f"NULL handling error: {e}")
            return df
    
    def _clean_infinite_values(self, df):
        """Clean infinite values (±inf)."""
        try:
            for col in df.columns:
                dtype = df[col].dtype
                
                if dtype in [pl.Float32, pl.Float64]:
                    df = df.with_columns(
                        pl.when(df[col].is_infinite())
                        .then(None)
                        .otherwise(df[col])
                        .fill_null(strategy="forward")
                        .fill_null(0.0)
                        .alias(col)
                    )
            
            return df
            
        except Exception as e:
            logger.warning(f"Infinite cleaning error: {e}")
            return df

    def _create_custom_time_column(self, df, settings):
        """Create a custom time column."""
        try:
            sampling_freq = settings.get('sampling_frequency', 1000)
            start_time_mode = settings.get('start_time_mode', '0 (Sıfırdan Başla)')
            custom_start_time = settings.get('custom_start_time')
            time_unit = settings.get('time_unit', 'saniye')
            column_name = settings.get('new_time_column_name', 'time_generated')
            
            data_length = df.height
            time_step = 1.0 / sampling_freq
            
            # Time unit conversion
            if time_unit == 'milisaniye':
                time_step *= 1000
            elif time_unit == 'mikrosaniye':
                time_step *= 1000000
            elif time_unit == 'nanosaniye':
                time_step *= 1000000000
            
            # Determine start time
            if start_time_mode == "Şimdiki Zaman":
                import datetime
                start_timestamp = datetime.datetime.now().timestamp()
                if time_unit != 'saniye':
                    if time_unit == 'milisaniye':
                        start_timestamp *= 1000
                    elif time_unit == 'mikrosaniye':
                        start_timestamp *= 1000000
                    elif time_unit == 'nanosaniye':
                        start_timestamp *= 1000000000
            elif start_time_mode == "Özel Zaman" and custom_start_time:
                try:
                    import datetime
                    dt = datetime.datetime.strptime(custom_start_time, '%Y-%m-%d %H:%M:%S')
                    start_timestamp = dt.timestamp()
                    if time_unit != 'saniye':
                        if time_unit == 'milisaniye':
                            start_timestamp *= 1000
                        elif time_unit == 'mikrosaniye':
                            start_timestamp *= 1000000
                        elif time_unit == 'nanosaniye':
                            start_timestamp *= 1000000000
                except:
                    logger.warning(f"Custom start time parse failed: {custom_start_time}, using zero")
                    start_timestamp = 0.0
            else:
                start_timestamp = 0.0
            
            # Create time array
            time_array = np.arange(data_length) * time_step + start_timestamp
            df = df.with_columns(pl.Series(column_name, time_array))
            
            logger.info(f"Custom time column created: '{column_name}' "
                       f"(Freq: {sampling_freq} Hz, Unit: {time_unit}, "
                       f"Start: {start_timestamp}, Length: {data_length})")
                       
        except Exception as e:
            logger.error(f"Error creating custom time column: {e}")
            column_name = settings.get('new_time_column_name', 'time_generated')
            df = df.with_columns(pl.Series(column_name, np.arange(df.height) / 1000.0))
            
        return df
            
    def _use_existing_time_column(self, df, settings):
        """Use existing time column."""
        time_column_name = settings.get('time_column')

        try:
            if time_column_name and time_column_name in df.columns:
                logger.info(f"Using time column: '{time_column_name}'")
                time_format = settings.get('time_format', 'Otomatik')
                
                original_series = df.get_column(time_column_name)
                logger.debug(f"Time column '{time_column_name}' dtype: {original_series.dtype}")
                logger.debug(f"Time column '{time_column_name}' first 5: {original_series.head().to_list()}")

                converted_series = None

                if time_format == 'Unix Timestamp':
                    converted_series = original_series.cast(pl.Datetime)
                elif time_format == 'Saniyelik Index':
                    time_unit = settings.get('time_unit', 'saniye')
                    multiplier = {'saniye': 1.0, 'milisaniye': 1000.0, 'mikrosaniye': 1e6, 'nanosaniye': 1e9}.get(time_unit, 1.0)
                    converted_series = original_series.cast(pl.Float64) / multiplier
                else:  # Otomatik
                    if original_series.dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]:
                        logger.info(f"Time column '{time_column_name}' is already numeric")
                        converted_series = original_series
                    else:
                        try:
                            logger.info(f"Converting time column '{time_column_name}' to datetime")
                            converted_series = original_series.str.to_datetime(errors='coerce')
                        except Exception:
                            logger.warning(f"'{time_column_name}' conversion failed, trying numeric")
                            converted_series = original_series.cast(pl.Float64, strict=False)
                
                if converted_series is not None:
                    if converted_series.dtype == pl.Datetime:
                        logger.info("Converting Datetime to Unix timestamp...")
                        converted_series = converted_series.dt.timestamp('ms') / 1000.0
                        self._datetime_converted = True
                    elif converted_series.dtype in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]:
                        first_value = converted_series[0]
                        if first_value is not None and abs(first_value) > 1e12:
                            logger.info("Time column detected as millisecond timestamp, converting to seconds...")
                            converted_series = converted_series / 1000.0
                            self._datetime_converted = True
                    
                    df = df.with_columns(converted_series.alias(time_column_name))
            else:
                if time_column_name:
                    logger.warning(f"Time column '{time_column_name}' not found, creating auto index 'time'")
                else:
                    logger.info("No time column specified, creating auto index 'time'")
                
                df = df.with_columns(pl.Series('time', np.arange(df.height) / 1000.0))
        
        except Exception as e:
            logger.error(f"Error processing time column: {e}")
            df = df.with_columns(pl.Series('time', np.arange(df.height) / 1000.0))
        
        return df


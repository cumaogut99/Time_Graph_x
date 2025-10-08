"""
Project File Manager for Time Graph Application
================================================

Manages .mpai project files (Motor Performance Analysis Interface format)
- Single file containing: data (parquet), layout (json), metadata (json)
- ZIP-based container for efficient storage and portability
- Fast loading with parquet format (no CSV conversion needed)
"""

import os
import json
import logging
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import polars as pl
from PyQt5.QtCore import QObject, pyqtSignal as Signal

logger = logging.getLogger(__name__)


class ProjectFileManager(QObject):
    """
    Manages .mpai project files.
    
    Features:
    - Save complete project state (data + layout + metadata)
    - Load project with fast parquet data loading
    - Validate project file integrity
    - Support for project metadata (version, timestamps, etc.)
    """
    
    # Signals
    save_progress = Signal(str, int)  # message, percentage
    load_progress = Signal(str, int)  # message, percentage
    save_completed = Signal(str)  # file_path
    load_completed = Signal(dict)  # project_data
    error_occurred = Signal(str)  # error_message
    
    # Project format version
    PROJECT_VERSION = "1.0"
    PROJECT_EXTENSION = ".mpai"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_dir = None
        
    def save_project(
        self, 
        file_path: str,
        dataframe: pl.DataFrame,
        layout_config: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a complete project to .mpai file.
        
        Args:
            file_path: Path to save the .mpai file
            dataframe: Polars DataFrame with the data
            layout_config: Layout configuration dict
            metadata: Additional metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure .mpai extension
            if not file_path.endswith(self.PROJECT_EXTENSION):
                file_path += self.PROJECT_EXTENSION
            
            logger.info(f"Starting project save to: {file_path}")
            self.save_progress.emit("Proje kaydediliyor...", 0)
            
            # Create temporary directory for files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Save data as parquet
                self.save_progress.emit("Veri kaydediliyor (Parquet format)...", 20)
                data_path = temp_path / "data.parquet"
                dataframe.write_parquet(
                    data_path,
                    compression="zstd",  # Best compression
                    statistics=True,     # Include metadata
                )
                logger.debug(f"Data saved to parquet: {dataframe.height} rows, {len(dataframe.columns)} cols")
                
                # 2. Save layout configuration
                self.save_progress.emit("Layout kaydediliyor...", 50)
                layout_path = temp_path / "layout.json"
                with open(layout_path, 'w', encoding='utf-8') as f:
                    json.dump(layout_config, f, indent=2, ensure_ascii=False)
                logger.debug("Layout config saved")
                
                # 3. Create and save metadata
                self.save_progress.emit("Metadata hazırlanıyor...", 70)
                project_metadata = self._create_metadata(dataframe, metadata)
                metadata_path = temp_path / "metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(project_metadata, f, indent=2, ensure_ascii=False)
                logger.debug("Metadata saved")
                
                # 4. Create ZIP archive (.mpai file)
                self.save_progress.emit("Proje dosyası oluşturuluyor...", 80)
                with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(data_path, "data.parquet")
                    zipf.write(layout_path, "layout.json")
                    zipf.write(metadata_path, "metadata.json")
                
                logger.info(f"Project saved successfully: {file_path}")
                self.save_progress.emit("Proje başarıyla kaydedildi!", 100)
                self.save_completed.emit(file_path)
                return True
                
        except Exception as e:
            error_msg = f"Proje kaydedilemedi: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
    
    def load_project(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a complete project from .mpai file.
        
        Args:
            file_path: Path to the .mpai file
            
        Returns:
            Dict containing:
                - 'dataframe': Polars DataFrame
                - 'layout_config': Layout configuration
                - 'metadata': Project metadata
            None if failed
        """
        try:
            logger.info(f"Starting project load from: {file_path}")
            self.load_progress.emit("Proje açılıyor...", 0)
            
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Proje dosyası bulunamadı: {file_path}")
            
            if not file_path.endswith(self.PROJECT_EXTENSION):
                raise ValueError(f"Geçersiz dosya uzantısı. .mpai dosyası bekleniyor.")
            
            # Create temporary directory for extraction
            if self.temp_dir:
                try:
                    import shutil
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                except:
                    pass
            
            self.temp_dir = tempfile.mkdtemp()
            temp_path = Path(self.temp_dir)
            
            # Extract ZIP contents
            self.load_progress.emit("Proje dosyası açılıyor...", 20)
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(temp_path)
            
            # Validate extracted files
            required_files = ["data.parquet", "layout.json", "metadata.json"]
            for req_file in required_files:
                if not (temp_path / req_file).exists():
                    raise ValueError(f"Proje dosyası eksik: {req_file}")
            
            # Load data from parquet (FAST!)
            self.load_progress.emit("Veri yükleniyor (Parquet - Hızlı!)...", 40)
            data_path = temp_path / "data.parquet"
            dataframe = pl.read_parquet(data_path)
            logger.debug(f"Data loaded: {dataframe.height} rows, {len(dataframe.columns)} cols")
            
            # Load layout configuration
            self.load_progress.emit("Layout yükleniyor...", 70)
            layout_path = temp_path / "layout.json"
            with open(layout_path, 'r', encoding='utf-8') as f:
                layout_config = json.load(f)
            logger.debug("Layout config loaded")
            
            # Load metadata
            self.load_progress.emit("Metadata yükleniyor...", 85)
            metadata_path = temp_path / "metadata.json"
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            logger.debug("Metadata loaded")
            
            # Prepare result
            project_data = {
                'dataframe': dataframe,
                'layout_config': layout_config,
                'metadata': metadata,
                'file_path': file_path
            }
            
            logger.info(f"Project loaded successfully: {file_path}")
            self.load_progress.emit("Proje başarıyla yüklendi!", 100)
            self.load_completed.emit(project_data)
            
            return project_data
            
        except Exception as e:
            error_msg = f"Proje yüklenemedi: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return None
    
    def validate_project(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate a .mpai project file.
        
        Args:
            file_path: Path to the .mpai file
            
        Returns:
            (is_valid, message) tuple
        """
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return False, "Dosya bulunamadı"
            
            # Check extension
            if not file_path.endswith(self.PROJECT_EXTENSION):
                return False, f"Geçersiz uzantı (beklenen: {self.PROJECT_EXTENSION})"
            
            # Check if valid ZIP
            if not zipfile.is_zipfile(file_path):
                return False, "Geçersiz proje dosyası formatı"
            
            # Check contents
            with zipfile.ZipFile(file_path, 'r') as zipf:
                file_list = zipf.namelist()
                required_files = ["data.parquet", "layout.json", "metadata.json"]
                
                for req_file in required_files:
                    if req_file not in file_list:
                        return False, f"Eksik dosya: {req_file}"
                
                # Try to read metadata for version check
                try:
                    metadata_content = zipf.read("metadata.json")
                    metadata = json.loads(metadata_content)
                    
                    version = metadata.get('version', 'unknown')
                    logger.debug(f"Project version: {version}")
                    
                except Exception as e:
                    return False, f"Metadata okunamadı: {str(e)}"
            
            return True, "Geçerli proje dosyası"
            
        except Exception as e:
            return False, f"Doğrulama hatası: {str(e)}"
    
    def _create_metadata(
        self, 
        dataframe: pl.DataFrame,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create project metadata.
        
        Args:
            dataframe: The data DataFrame
            additional_metadata: Additional metadata to include
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'version': self.PROJECT_VERSION,
            'created_date': datetime.now().isoformat(),
            'app_name': 'Time Graph Widget',
            'app_version': '1.0.0',  # TODO: Get from app config
            'data_info': {
                'row_count': dataframe.height,
                'column_count': len(dataframe.columns),
                'columns': list(dataframe.columns),
                'dtypes': {col: str(dtype) for col, dtype in zip(dataframe.columns, dataframe.dtypes)}
            }
        }
        
        # Add additional metadata if provided
        if additional_metadata:
            metadata['custom'] = additional_metadata
        
        return metadata
    
    def get_project_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get project information without loading the full data.
        Useful for file browser preview.
        
        Args:
            file_path: Path to the .mpai file
            
        Returns:
            Project info dict or None
        """
        try:
            if not zipfile.is_zipfile(file_path):
                return None
            
            with zipfile.ZipFile(file_path, 'r') as zipf:
                # Read only metadata
                metadata_content = zipf.read("metadata.json")
                metadata = json.loads(metadata_content)
                
                # Add file info
                file_stats = os.stat(file_path)
                metadata['file_info'] = {
                    'size_bytes': file_stats.st_size,
                    'size_mb': file_stats.st_size / (1024 * 1024),
                    'modified_date': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                }
                
                return metadata
                
        except Exception as e:
            logger.error(f"Error getting project info: {e}")
            return None
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir:
            try:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                logger.debug("Temporary files cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up temp files: {e}")
            finally:
                self.temp_dir = None
    
    def __del__(self):
        """Destructor - cleanup temp files."""
        self.cleanup()


def create_project_from_csv(
    csv_path: str,
    mpai_path: str,
    layout_config: Dict[str, Any],
    import_settings: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Helper function to create a .mpai project from a CSV file.
    
    Args:
        csv_path: Path to CSV file
        mpai_path: Path to save .mpai file
        layout_config: Layout configuration
        import_settings: CSV import settings (encoding, delimiter, etc.)
        
    Returns:
        True if successful
    """
    try:
        logger.info(f"Creating project from CSV: {csv_path}")
        
        # Load CSV
        df = pl.read_csv(csv_path)
        
        # Create metadata
        metadata = {
            'original_file': os.path.basename(csv_path),
            'original_file_path': csv_path,
            'import_settings': import_settings or {}
        }
        
        # Save project
        manager = ProjectFileManager()
        success = manager.save_project(mpai_path, df, layout_config, metadata)
        manager.cleanup()
        
        return success
        
    except Exception as e:
        logger.error(f"Error creating project from CSV: {e}")
        return False


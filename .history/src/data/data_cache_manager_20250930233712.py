"""
Data Cache Manager - CSV to Parquet automatic caching
"""

import logging
import hashlib
import polars as pl
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataCacheManager:
    """
    Otomatik CSV → Parquet cache sistemi.
    
    - CSV dosyaları ilk yüklemede Parquet'e çevrilir
    - Cache'den sonraki yüklemeler 8-27x daha hızlı
    - Kullanıcı hiçbir şey fark etmez (transparent)
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Cache klasörü yolu (default: .cache)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        logger.info(f"DataCacheManager initialized (cache dir: {self.cache_dir})")
    
    def _get_cache_path(self, csv_path: Path) -> Path:
        """
        CSV dosyası için unique cache path hesapla.
        
        Hash = dosya yolu + modification time
        """
        file_stat = csv_path.stat()
        cache_key = f"{csv_path.absolute()}_{file_stat.st_mtime}_{file_stat.st_size}"
        file_hash = hashlib.md5(cache_key.encode()).hexdigest()[:16]
        
        cache_filename = f"{csv_path.stem}_{file_hash}.parquet"
        return self.cache_dir / cache_filename
    
    def _is_cache_valid(self, cache_path: Path, csv_path: Path) -> bool:
        """
        Cache'in güncel olup olmadığını kontrol et.
        """
        if not cache_path.exists():
            return False
        
        cache_time = cache_path.stat().st_mtime
        csv_time = csv_path.stat().st_mtime
        
        # Cache CSV'den daha yeni mi?
        return cache_time >= csv_time
    
    def load_with_cache(self, csv_path: str, infer_schema_length: int = 10000) -> Optional[pl.DataFrame]:
        """
        CSV'yi cache'den yükle veya yeni cache oluştur.
        
        Args:
            csv_path: CSV dosya yolu
            infer_schema_length: Schema inference için satır sayısı
            
        Returns:
            Polars DataFrame veya None (hata durumunda)
        """
        try:
            csv_file = Path(csv_path)
            
            if not csv_file.exists():
                logger.error(f"CSV file not found: {csv_path}")
                return None
            
            cache_path = self._get_cache_path(csv_file)
            
            # Cache varsa ve güncel mi?
            if self._is_cache_valid(cache_path, csv_file):
                logger.info(f"Loading from cache: {cache_path.name}")
                start_time = datetime.now()
                
                # Cache'den yükle (HIZLI!)
                df = pl.read_parquet(cache_path)
                
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.info(f"Cache loaded in {elapsed:.3f}s ({df.height} rows, {len(df.columns)} columns)")
                return df
            
            # Cache yok veya eski - CSV'yi yükle
            logger.info(f"Creating cache for: {csv_file.name}")
            start_time = datetime.now()
            
            df = pl.read_csv(
                csv_path,
                infer_schema_length=infer_schema_length,
                try_parse_dates=True
            )
            
            csv_load_time = (datetime.now() - start_time).total_seconds()
            
            # Parquet'e çevir ve kaydet
            cache_start = datetime.now()
            df.write_parquet(
                cache_path,
                compression="zstd",  # En iyi sıkıştırma
                statistics=True,     # Metadata ekle
            )
            cache_time = (datetime.now() - cache_start).total_seconds()
            
            # Dosya boyutları
            csv_size = csv_file.stat().st_size / (1024 * 1024)  # MB
            cache_size = cache_path.stat().st_size / (1024 * 1024)  # MB
            compression_ratio = (1 - cache_size / csv_size) * 100
            
            logger.info(
                f"Cache created in {cache_time:.3f}s: {cache_path.name} "
                f"({cache_size:.2f} MB, {compression_ratio:.1f}% smaller)"
            )
            logger.info(f"Total load time: {csv_load_time + cache_time:.3f}s")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV with cache: {e}", exc_info=True)
            return None
    
    def clear_cache(self):
        """Tüm cache'i temizle."""
        try:
            cache_files = list(self.cache_dir.glob("*.parquet"))
            
            if not cache_files:
                logger.info("Cache is already empty")
                return
            
            total_size = sum(f.stat().st_size for f in cache_files)
            
            for cache_file in cache_files:
                cache_file.unlink()
            
            logger.info(
                f"Cache cleared: {len(cache_files)} files, "
                f"{total_size / (1024 * 1024):.2f} MB freed"
            )
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_cache_size(self) -> float:
        """
        Cache boyutunu MB olarak döndür.
        
        Returns:
            Cache boyutu (MB)
        """
        try:
            cache_files = list(self.cache_dir.glob("*.parquet"))
            total_bytes = sum(f.stat().st_size for f in cache_files)
            return total_bytes / (1024 * 1024)
        except Exception as e:
            logger.error(f"Error getting cache size: {e}")
            return 0.0
    
    def get_cache_info(self) -> dict:
        """
        Cache hakkında detaylı bilgi döndür.
        
        Returns:
            {
                'file_count': int,
                'total_size_mb': float,
                'files': [...]
            }
        """
        try:
            cache_files = list(self.cache_dir.glob("*.parquet"))
            
            files_info = []
            for cache_file in cache_files:
                stat = cache_file.stat()
                files_info.append({
                    'name': cache_file.name,
                    'size_mb': stat.st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            return {
                'file_count': len(cache_files),
                'total_size_mb': sum(f['size_mb'] for f in files_info),
                'files': files_info
            }
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {'file_count': 0, 'total_size_mb': 0.0, 'files': []}


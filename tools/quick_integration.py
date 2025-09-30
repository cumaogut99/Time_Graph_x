#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hızlı Entegrasyon Kodu
=====================

Bu kodu mevcut app.py dosyanıza ekleyerek hemen kullanmaya başlayabilirsiniz.
"""

import polars as pl
from data_validator import DataValidator
from error_handler import ErrorHandler

def quick_load_and_display(file_path: str, time_graph_widget):
    """
    Hızlı veri yükleme ve görüntüleme fonksiyonu.
    
    Args:
        file_path (str): Yüklenecek dosyanın yolu.
        time_graph_widget: TimeGraphWidget'in bir örneği.
    """
    data_validator = DataValidator()
    error_handler = ErrorHandler()

    try:
        # Dosya uzantısına göre Polars ile oku
        if file_path.endswith('.csv'):
            df = pl.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pl.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

        # Veri doğrulama
        validation_results = data_validator.validate_dataframe(df)
        if not validation_results['is_valid']:
            if data_validator.can_auto_fix(validation_results):
                df = data_validator.auto_fix_dataframe(df, validation_results)
            else:
                error_handler.handle_error("Data Validation Error", context={'details': validation_results['errors']})
                return

        # Zaman kolonunu belirle (ilk kolonu varsayalım)
        time_column = df.columns[0]
        
        # Veriyi widget'a yükle
        time_graph_widget.update_data(df, time_column=time_column)
        
        print(f"'{file_path}' başarıyla yüklendi ve görüntülendi.")

    except Exception as e:
        error_handler.handle_error("Quick Load Error", exception=e, context={'file_path': file_path})

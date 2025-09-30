#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entegrasyon Rehberi
==================

Bu dosya, yeni hata yönetimi sistemlerinin mevcut uygulamaya
nasıl entegre edileceğini gösterir.
"""

import polars as pl
from data_validator import DataValidator

class IntegrationGuide:
    def __init__(self, time_graph_widget, data_validator=None, error_handler=None):
        self.time_graph_widget = time_graph_widget
        self.data_validator = data_validator or DataValidator()
        self.error_handler = error_handler or ErrorHandler()
        self.data_source = None
        self.is_connected = False
        
    def connect_to_data_source(self, data_source_func: callable):
        self.data_source = data_source_func
        self.is_connected = True
        self._fetch_and_update_data()
        
    def _fetch_and_update_data(self):
        """Veri kaynağından veri al ve widget'ı güncelle."""
        if not self.is_connected or not self.data_source:
            return

        try:
            # 1. Veri al (örneğin bir Polars DataFrame olarak)
            df = self.data_source()
            
            if df is None:
                return

            # 2. Veri doğrulama
            validation_results = self.data_validator.validate_dataframe(df)
            if not validation_results['is_valid']:
                # Hata yönetimi veya otomatik düzeltme
                if self.data_validator.can_auto_fix(validation_results):
                    df = self.data_validator.auto_fix_dataframe(df, validation_results)
                else:
                    self.error_handler.handle_error(
                        "Data Validation Error", 
                        context={'details': validation_results['errors']}
                    )
                    return

            # 3. TimeGraphWidget'i güncelle
            # Zaman kolonunu doğru şekilde belirttiğinizden emin olun
            self.time_graph_widget.update_data(df, time_column='timestamp')

        except Exception as e:
            self.error_handler.handle_error("Data Fetch Error", exception=e)
            
    def disconnect(self):
        self.is_connected = False
        self.data_source = None
        self.time_graph_widget.clear_data()

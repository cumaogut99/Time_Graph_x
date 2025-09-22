#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time Graph Widget - Basit Launcher
==================================

Bu basit launcher, time graph widget'ını import sorunları olmadan başlatır.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

def main():
    """Ana fonksiyon."""
    print("Time Graph Widget başlatılıyor...")
    
    # QApplication oluştur
    app = QApplication(sys.argv)
    app.setApplicationName("Time Graph Widget")
    
    try:
        # Mevcut dizini path'e ekle
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Widget'ı import et
        from time_graph_widget import TimeGraphWidget
        
        # Ana pencere oluştur
        main_window = QMainWindow()
        main_window.setWindowTitle("Time Graph Widget - Veri Analizi")
        main_window.setMinimumSize(1200, 800)
        main_window.resize(1600, 1000)
        
        # Widget'ı merkezi widget olarak ayarla
        time_graph_widget = TimeGraphWidget()
        main_window.setCentralWidget(time_graph_widget)
        
        # File menü sinyallerini bağla
        if hasattr(time_graph_widget, 'toolbar_manager'):
            toolbar = time_graph_widget.toolbar_manager
            
            if hasattr(toolbar, 'file_open_requested'):
                toolbar.file_open_requested.connect(lambda: print("File Open istendi"))
            if hasattr(toolbar, 'file_save_requested'):
                toolbar.file_save_requested.connect(lambda: print("File Save istendi"))
            if hasattr(toolbar, 'file_exit_requested'):
                toolbar.file_exit_requested.connect(main_window.close)
        
        # Pencereyi göster
        main_window.show()
        
        print("Uygulama başarıyla başlatıldı!")
        print("File > Open ile veri dosyası açabilirsiniz.")
        
        # Uygulama döngüsünü başlat
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"Import hatası: {e}")
        print("Lütfen tüm gerekli modüllerin mevcut olduğundan emin olun.")
        
        # Hata mesajı göster
        error_app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        QMessageBox.critical(None, "Import Hatası", 
                           f"Gerekli modüller yüklenemedi:\n\n{str(e)}\n\nLütfen kurulumu kontrol edin.")
        sys.exit(1)
        
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        
        # Hata mesajı göster
        error_app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        QMessageBox.critical(None, "Uygulama Hatası", 
                           f"Uygulama başlatılamadı:\n\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

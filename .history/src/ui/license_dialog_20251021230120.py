#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
License Dialog - Lisans Aktivasyon ve Bilgi Dialog'u
====================================================
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QMessageBox, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class LicenseDialog(QDialog):
    """Lisans aktivasyon ve bilgi gösterme dialog'u"""
    
    def __init__(self, license_manager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("Lisans Yönetimi")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self._setup_ui()
        self._load_license_info()
    
    def _setup_ui(self):
        """Arayüzü kur"""
        layout = QVBoxLayout()
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # 1. Lisans Bilgileri Tab
        info_tab = self._create_info_tab()
        tab_widget.addTab(info_tab, "📋 Lisans Bilgileri")
        
        # 2. Aktivasyon Tab
        activation_tab = self._create_activation_tab()
        tab_widget.addTab(activation_tab, "🔑 Lisans Aktivasyonu")
        
        layout.addWidget(tab_widget)
        
        # Kapat butonu
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _create_info_tab(self) -> QWidget:
        """Lisans bilgileri tab'ını oluştur"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Durum grubu
        status_group = QGroupBox("Lisans Durumu")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(10)
        self.status_label.setFont(font)
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Detaylar grubu
        details_group = QGroupBox("Lisans Detayları")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Makine ID grubu
        machine_group = QGroupBox("Makine Kimliği")
        machine_layout = QVBoxLayout()
        
        machine_info = QLabel(
            "Lisans aktivasyonu için aşağıdaki makine kimliğini kullanın:"
        )
        machine_info.setWordWrap(True)
        machine_layout.addWidget(machine_info)
        
        self.machine_id_edit = QLineEdit()
        self.machine_id_edit.setReadOnly(True)
        machine_layout.addWidget(self.machine_id_edit)
        
        copy_btn = QPushButton("📋 Kopyala")
        copy_btn.clicked.connect(self._copy_machine_id)
        machine_layout.addWidget(copy_btn)
        
        machine_group.setLayout(machine_layout)
        layout.addWidget(machine_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_activation_tab(self) -> QWidget:
        """Aktivasyon tab'ını oluştur"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Açıklama
        info_label = QLabel(
            "<b>Lisans Aktivasyonu</b><br><br>"
            "Tam lisans satın aldıysanız, aşağıdaki formu doldurun ve aktivasyonu tamamlayın."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Form grubu
        form_group = QGroupBox("Aktivasyon Bilgileri")
        form_layout = QVBoxLayout()
        
        # Lisans sahibi
        owner_label = QLabel("Lisans Sahibi (Ad Soyad/Şirket):")
        form_layout.addWidget(owner_label)
        
        self.owner_edit = QLineEdit()
        self.owner_edit.setPlaceholderText("Örn: Ahmet Yılmaz / ABC Şirketi")
        form_layout.addWidget(self.owner_edit)
        
        # Lisans anahtarı
        key_label = QLabel("Lisans Anahtarı:")
        form_layout.addWidget(key_label)
        
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        form_layout.addWidget(self.key_edit)
        
        # Aktivasyon butonu
        activate_btn = QPushButton("🔓 Lisansı Aktive Et")
        activate_btn.clicked.connect(self._activate_license)
        form_layout.addWidget(activate_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Satın alma bilgisi
        purchase_group = QGroupBox("Lisans Satın Alma")
        purchase_layout = QVBoxLayout()
        
        purchase_info = QLabel(
            "<b>Henüz lisans satın almadınız mı?</b><br><br>"
            "Tam özellikli lisans için lütfen satıcı ile iletişime geçin.<br>"
            "E-posta: sales@timegraph.com<br>"
            "Web: www.timegraph.com"
        )
        purchase_info.setWordWrap(True)
        purchase_layout.addWidget(purchase_info)
        
        purchase_group.setLayout(purchase_layout)
        layout.addWidget(purchase_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _load_license_info(self):
        """Lisans bilgilerini yükle"""
        is_valid, message, license_info = self.license_manager.check_license()
        
        # Durum
        if is_valid:
            status_text = f"✅ <b>Lisans Geçerli</b><br><br>{message}"
            status_style = "color: green;"
        else:
            status_text = f"⚠️ <b>Lisans Problemi</b><br><br>{message}"
            status_style = "color: orange;"
        
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(status_style)
        
        # Detaylar
        if license_info:
            details = f"""
Lisans Tipi: {license_info.get('type', 'N/A').upper()}
Lisans Sahibi: {license_info.get('owner', 'Trial Kullanıcı')}
Aktivasyon Tarihi: {license_info.get('activation_date', license_info.get('start_date', 'N/A'))}
            """
            
            if license_info.get('type') == 'trial':
                details += f"\nBitiş Tarihi: {license_info.get('end_date', 'N/A')}"
            elif license_info.get('type') == 'subscription':
                details += f"\nAbonelik Bitiş: {license_info.get('subscription_end', 'N/A')}"
            
            self.details_text.setText(details.strip())
        else:
            self.details_text.setText("Lisans bilgisi bulunamadı.")
        
        # Makine ID
        machine_id = self.license_manager.get_machine_id_for_activation()
        self.machine_id_edit.setText(machine_id)
    
    def _copy_machine_id(self):
        """Makine ID'sini kopyala"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.machine_id_edit.text())
        
        QMessageBox.information(
            self,
            "Kopyalandı",
            "Makine kimliği panoya kopyalandı."
        )
    
    def _activate_license(self):
        """Lisansı aktive et"""
        owner = self.owner_edit.text().strip()
        license_key = self.key_edit.text().strip()
        
        if not owner or not license_key:
            QMessageBox.warning(
                self,
                "Eksik Bilgi",
                "Lütfen tüm alanları doldurun."
            )
            return
        
        # Aktivasyon
        success, message = self.license_manager.activate_license(
            license_key=license_key,
            owner=owner,
            license_type='full'
        )
        
        if success:
            QMessageBox.information(
                self,
                "Başarılı",
                f"✅ {message}\n\nUygulama yeniden başlatılacak."
            )
            self._load_license_info()
        else:
            QMessageBox.critical(
                self,
                "Aktivasyon Başarısız",
                f"❌ {message}\n\nLütfen bilgileri kontrol edin."
            )


class LicenseCheckDialog(QDialog):
    """Basit lisans kontrol dialog'u (uygulama başlangıcında)"""
    
    def __init__(self, message: str, is_valid: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lisans Bilgisi")
        self.setMinimumWidth(400)
        self._setup_ui(message, is_valid)
    
    def _setup_ui(self, message: str, is_valid: bool):
        """Arayüzü kur"""
        layout = QVBoxLayout()
        
        # İkon ve mesaj
        icon_text = "✅" if is_valid else "⚠️"
        label = QLabel(f"<h3>{icon_text} Lisans Durumu</h3><p>{message}</p>")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        if not is_valid:
            # Trial bitmiş ise satın alma bilgisi
            info_btn = QPushButton("📋 Lisans Satın Al")
            info_btn.clicked.connect(self._show_purchase_info)
            button_layout.addWidget(info_btn)
        
        ok_btn = QPushButton("Devam Et" if is_valid else "Yine de Devam Et")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _show_purchase_info(self):
        """Satın alma bilgisini göster"""
        QMessageBox.information(
            self,
            "Lisans Satın Alma",
            "<b>Tam Lisans Satın Alma</b><br><br>"
            "Lisans satın almak için:<br>"
            "E-posta: sales@timegraph.com<br>"
            "Web: www.timegraph.com<br><br>"
            "Aktivasyon için makine kimliğinizi hazır bulundurun."
        )


# type: ignore
"""
TimeGraph UI Setup Module

Bu modül TimeGraphWidget'ın UI kurulum işlemlerini yönetir.
Ana sınıftan UI kurulum kodlarını ayırarak daha yönetilebilir hale getirir.
"""

import logging
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QSplitter, QStackedWidget, QToolButton,
    QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

if TYPE_CHECKING:
    from .time_graph_widget_v2 import TimeGraphWidget

logger = logging.getLogger(__name__)


class TimeGraphUISetup:
    """TimeGraphWidget için UI kurulum işlemlerini yöneten sınıf."""
    
    def __init__(self, widget: 'TimeGraphWidget'):
        self.widget = widget
        
    def setup_ui(self):
        """Ana UI layout'unu kur."""
        main_layout = QVBoxLayout(self.widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.widget.toolbar_manager.get_toolbar())
        
        self.widget.content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.widget.content_splitter)
        
        # Sol panel yönetimi
        self._setup_left_panel()
        
        # Tab widget kurulumu
        self._setup_tab_widget()
        
        # İstatistik paneli kurulumu
        self._setup_statistics_panel()
        
        # Splitter ayarları
        self._configure_splitter()
        
        # Tab değişiklik sinyalini bağla
        self.widget.tab_widget.currentChanged.connect(self.widget._on_tab_changed)
        
        # İlk tab'ı ekle
        self.widget._add_tab()
        
        # Gecikmeli kurulum
        QTimer.singleShot(200, self.widget._delayed_initial_setup)
        
    def _setup_left_panel(self):
        """Sol panel stack'ini kur."""
        self.widget.left_panel_stack = QStackedWidget()
        self.widget.left_panel_stack.setMinimumWidth(280)
        self.widget.left_panel_stack.setMaximumWidth(350)
        
        # Panel'leri oluştur ve ekle
        self.widget.settings_panel = self.widget.settings_panel_manager.get_settings_panel()
        self.widget.statistics_settings_panel = self.widget.statistics_settings_panel_manager.get_settings_panel()
        self.widget.graph_settings_panel = self.widget.graph_settings_panel_manager.get_settings_panel()
        
        # Analiz panelleri
        self.widget.correlations_panel = self.widget._create_correlations_panel()
        self.widget.bitmask_panel = self.widget._create_bitmask_panel()
        
        # Stack'e ekle
        self.widget.left_panel_stack.addWidget(self.widget.settings_panel)
        self.widget.left_panel_stack.addWidget(self.widget.statistics_settings_panel)
        self.widget.left_panel_stack.addWidget(self.widget.graph_settings_panel)
        self.widget.left_panel_stack.addWidget(self.widget.correlations_panel)
        self.widget.left_panel_stack.addWidget(self.widget.bitmask_panel)
        
        self.widget.left_panel_stack.setVisible(False)  # Başlangıçta gizli
        self.widget.content_splitter.addWidget(self.widget.left_panel_stack)
        
    def _setup_tab_widget(self):
        """Tab widget'ını kur."""
        self.widget.tab_widget = QTabWidget()
        self.widget.tab_widget.setTabsClosable(True)
        self.widget.tab_widget.setMovable(True)
        self.widget.tab_widget.tabBarDoubleClicked.connect(self.widget._rename_tab)
        self.widget.tab_widget.tabCloseRequested.connect(self.widget._remove_tab)

        # '+' butonu ekle
        self.widget.add_tab_button = QToolButton(self.widget)
        self.widget.add_tab_button.setText("+")
        self.widget.add_tab_button.setCursor(Qt.PointingHandCursor)
        self.widget.add_tab_button.clicked.connect(self.widget._add_tab)
        self.widget.tab_widget.setCornerWidget(self.widget.add_tab_button, Qt.TopRightCorner)
        
        # Modern stil uygula
        self.widget._apply_tab_stylesheet()
        
        self.widget.content_splitter.addWidget(self.widget.tab_widget)
        
    def _setup_statistics_panel(self):
        """İstatistik panelini kur."""
        self.widget.channel_stats_panel = self.widget._create_channel_statistics_panel()
        self.widget.content_splitter.addWidget(self.widget.channel_stats_panel)
        
    def _configure_splitter(self):
        """Splitter ayarlarını yapılandır."""
        self.widget.content_splitter.setSizes([280, 660, 300])
        self.widget.content_splitter.setCollapsible(0, True)
        self.widget.content_splitter.setCollapsible(1, False)
        self.widget.content_splitter.setCollapsible(2, False)
        
        logger.debug("UI setup completed successfully")


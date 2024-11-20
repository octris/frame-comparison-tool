FRAME_STYLE = '''
    QLabel {
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }
'''

CONFIG_AREA_STYLE = '''
    QLabel {
        color: #333333;
        margin-right: 4px;
    }
'''

FILE_ICON_LABEL_STYLE = '''
    QLabel {
            background-color: #007AFF;
            border-radius: 12px;
            color: white;
            padding: 2px;
    }
'''

SOURCE_LABEL_STYLE = '''
    QLabel {
        color: #333333;
        padding: 0 4px;
        background: transparent;
        border: none;
    }
'''

SCROLL_AREA_STYLE = '''
    QScrollArea {
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }
'''

WIDGET_STYLE = '''
    QWidget {
        background-color: #F8F8F8;
        border-radius: 4px;
    }
'''

SOURCE_WIDGET = '''
    QWidget {
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        margin: 2px;
    }
'''

SPIN_BOX_STYLE = '''
    QSpinBox {
        background-color: white;
        border: 1px solid #C0C0C0;
        border-radius: 3px;
        padding: 2px 5px;
        color: #333333;
    }
    QSpinBox:hover {
        border-color: #808080;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        background-color: #F0F0F0;
        border: 1px solid #C0C0C0;
        border-radius: 2px;
        width: 16px;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #E0E0E0;
    }
'''

DROPDOWN_STYLE = '''
    QComboBox {
        min-width: 120px;
        max-width: 120px;
        padding: 5px;
        border: 1px solid #C0C0C0;
        border-radius: 3px;
        background-color: white;
        color: #333333;
    }
    QComboBox:hover {
        border-color: #808080;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox QAbstractItemView {
        border: 1px solid #C0C0C0;
        background-color: white;
        selection-background-color: #E0E0E0;
        selection-color: #333333;
        padding: 4px;
    }
    QComboBox QAbstractItemView::item {
        min-height: 24px;
        padding: 4px;
    }
    QComboBox QAbstractItemView::item:hover {
        background-color: #F0F0F0;
        color: #333333;
    }
'''

ADD_BUTTON_STYLE = '''
    QPushButton {
        background-color: #007AFF;
        color: white;
        padding: 5px 15px;
        border: none;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }
    QPushButton:pressed {
        background-color: #004494;
    }
'''

DELETE_BUTTON_STYLE = '''
    QPushButton {
        background-color: #FF3B30;
        color: white;
        border: none;
        border-radius: 3px;
        padding: 4px 8px;
    }
    QPushButton:hover {
        background-color: #FF2D55;
    }
    QPushButton:pressed {
        background-color: #D63964;
    }
'''

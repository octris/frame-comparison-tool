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

SPIN_BOX_STYLE = """
    QSpinBox {
        background-color: white;
        color: #333333;
        padding: 2px 4px;
    }

    QSpinBox::up-button, QSpinBox::down-button {
        border-left: 1px solid #E0E0E0;
    }

    QSpinBox::up-button {
        border-top-right-radius: 4px;
    }

    QSpinBox::down-button {
        border-bottom-right-radius: 4px;
    }
"""

DROPDOWN_STYLE = """
    QComboBox {
        background-color: white;
        color: #333333;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 2px 4px;
    }

    QComboBox:hover {
        border: 1px solid #007AFF;
    }

    QComboBox:focus {
        border: 1px solid #007AFF;
    }

    QComboBox::drop-down {
        border: none;
        width: 20px;
    }

    QComboBox::down-arrow {
        color: #333333;
        width: 8px;
        height: 8px;
    }

    QComboBox QAbstractItemView {
        background-color: white;
        color: #333333;
        selection-background-color: #E8E8E8;
        border: 1px solid #E0E0E0;
    }
"""

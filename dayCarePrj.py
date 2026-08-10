import sys
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QPushButton, QMessageBox, QFileDialog, QLineEdit)
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from logic import DaycareAllocator
from format_config import get_input_format_help, get_selection_instructions
# updater removed: update checking/installation disabled per user request

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("מערכת שיבוץ מעונות")
        self.resize(560, 420)
        # Friendly default font for non-technical users
        self.base_font = QFont("Segoe UI", 11)
        self.setFont(self.base_font)
        
        self.daycares_path = ""
        self.salaries_path = ""
        
        self.lbl_daycares = QLabel("לא נבחר קובץ מעונות (Excel)")
        self.lbl_salaries = QLabel("לא נבחר קובץ משכורות (CSV)")
        self.lbl_daycares.setStyleSheet(
            "color: #1f2937; font-size: 12px; font-weight: 600; padding: 6px;"
            "background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px;"
        )
        self.lbl_salaries.setStyleSheet(
            "color: #1f2937; font-size: 12px; font-weight: 600; padding: 6px;"
            "background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px;"
        )
        self.lbl_daycares.setWordWrap(True)
        self.lbl_salaries.setWordWrap(True)
        self.lbl_daycares.setMinimumHeight(40)
        self.lbl_salaries.setMinimumHeight(40)
        self.lbl_daycares.setToolTip("בחר קובץ Excel שמכיל את רשימת המעונות (עמודה ראשונה)")
        self.lbl_salaries.setToolTip("בחר קובץ CSV עם שדות השכר לפי ההגדרות")
        
        btn_daycares = QPushButton("בחר קובץ מעונות...")
        btn_daycares.clicked.connect(self.select_daycares)
        btn_daycares.setMinimumHeight(42)
        btn_daycares.setFont(QFont(self.base_font.family(), 11, QFont.Bold))
        
        btn_salaries = QPushButton("בחר קובץ משכורות...")
        btn_salaries.clicked.connect(self.select_salaries)
        btn_salaries.setMinimumHeight(42)
        btn_salaries.setFont(QFont(self.base_font.family(), 11, QFont.Bold))
        
        self.input_rate = QLineEdit("220")
        self.input_rate.setFixedWidth(140)
        self.input_rate.setMaximumWidth(200)
        self.input_rate.setToolTip('הקלד תעריף שעתי במספרים — לדוגמה 220')
        validator = QDoubleValidator(0.0, 10000.0, 2, self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.input_rate.setValidator(validator)
        self.input_rate.textChanged.connect(self.update_run_button_state)
        
        self.btn_run = QPushButton("הפקת דוח שיבוץ")
        self.btn_run.setStyleSheet("padding: 12px; font-size: 15px; font-weight: bold; background-color: #1976D2; color: white;")
        self.btn_run.clicked.connect(self.run_process)
        self.btn_run.setMinimumHeight(48)
        self.btn_run.setEnabled(False)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        header = QLabel(get_selection_instructions())
        header.setStyleSheet("font-size: 12px; color: #222; line-height: 1.3;")
        header.setWordWrap(True)
        layout.addWidget(header)
        layout.addWidget(QLabel("<b>קובץ רשימת מעונות:</b>"))
        layout.addWidget(btn_daycares)
        layout.addWidget(self.lbl_daycares)
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("<b>קובץ משכורות:</b>"))
        layout.addWidget(btn_salaries)
        layout.addWidget(self.lbl_salaries)
        layout.addSpacing(10)

        btn_format_info = QPushButton("הגדרות קבצי קלט")
        btn_format_info.clicked.connect(self.show_format_info)
        btn_format_info.setToolTip("הסבר על מבנה הקבצים הנדרש")
        btn_format_info.setMinimumHeight(36)
        layout.addWidget(btn_format_info)

        # Update checking removed — keep UI compact
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("<b>תעריף שעתי (ש\"ח):</b>"))
        layout.addWidget(self.input_rate)
        
        layout.addSpacing(20)
        layout.addWidget(self.btn_run)

        # status label for friendly messages
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #444; font-size: 12px;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # internal state
        self.daycares_path = ""
        self.salaries_path = ""

        # initial validation
        self.update_run_button_state()

    def select_daycares(self):
        file, _ = QFileDialog.getOpenFileName(self, "בחר קובץ מעונות", "", "Excel Files (*.xlsx *.xls)")
        if file:
            self.daycares_path = file
            chosen_name = Path(file).name
            self.lbl_daycares.setText(f"נבחר: {chosen_name}")
            self.lbl_daycares.setToolTip(file)
            self.status_label.setText("קובץ מעונות נבחר — בדוק שהעמודה הראשונה היא שם המעון.")
            self.update_run_button_state()

    def select_salaries(self):
        file, _ = QFileDialog.getOpenFileName(self, "בחר קובץ משכורות", "", "CSV Files (*.csv)")
        if file:
            self.salaries_path = file
            chosen_name = Path(file).name
            self.lbl_salaries.setText(f"נבחר: {chosen_name}")
            self.lbl_salaries.setToolTip(file)
            self.status_label.setText("קובץ משכורות נבחר — ודא שיש עמודת תקופה ומחרוזות שם מלא.")
            self.update_run_button_state()

    def run_process(self):
        if not self.daycares_path or not self.salaries_path:
            QMessageBox.warning(self, "שגיאה", "יש לבחור את שני הקבצים לפני ההפעלה.")
            return
            
        try:
            rate = float(self.input_rate.text())
            save_path, _ = QFileDialog.getSaveFileName(self, "שמור קובץ שיבוץ", "שיבוץ_מעונות_סופי.xlsx", "Excel Files (*.xlsx)")
            if not save_path:
                return
                
            allocator = DaycareAllocator(hourly_rate=rate)
            warnings_list = allocator.generate_schedule(self.daycares_path, self.salaries_path, save_path)
            
            if warnings_list:
                msg = f"הקובץ נוצר בהצלחה ונשמר ב:\n{save_path}\n\n"
                msg += "שים לב - חסרות שעות תקציב במערכת עבור המעונות הבאים:\n"
                msg += "\n".join(warnings_list)
                QMessageBox.warning(self, "הצלחה עם חריגות", msg)
            else:
                QMessageBox.information(self, "הצלחה", f"הקובץ נוצר בהצלחה ונשמר ב:\n{save_path}")
            
            # סגירת החלון לאחר אישור ההודעה
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "שגיאת מערכת", f"אירעה שגיאה במהלך עיבוד הנתונים:\n{str(e)}")

    def show_format_info(self):
        QMessageBox.information(self, "הגדרות קבצי קלט", get_input_format_help())

    def check_updates(self):
        # intentionally left blank: update functionality removed
        return

    def update_run_button_state(self):
        """Enable the run button only when both files are selected and rate is valid."""
        rate_ok = False
        try:
            txt = self.input_rate.text().strip()
            rate_ok = bool(txt) and float(txt) > 0
        except Exception:
            rate_ok = False

        enabled = bool(self.daycares_path) and bool(self.salaries_path) and rate_ok
        self.btn_run.setEnabled(enabled)
        if not enabled:
            if not self.daycares_path or not self.salaries_path:
                self.status_label.setText("בחר קבצים ובדוק את התעריף לפני הפקת הדוח.")
            elif not rate_ok:
                self.status_label.setText("הזן תעריף שעתי תקין (מספר חיובי).")
        else:
            self.status_label.setText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
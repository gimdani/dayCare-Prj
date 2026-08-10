from dataclasses import dataclass

@dataclass(frozen=True)
class SalaryColumns:
    FIRST_NAME: str = 'שם פרטי'
    LAST_NAME: str = 'שם משפחה'
    PERIOD: str = 'תקופה'
    TOTAL_EMPLOYER_COST: str = 'סהכ כללי עלות מעביד'
    DISPLAY_NAME: str = 'שם_לתצוגה'

@dataclass(frozen=True)
class ScheduleColumns:
    WORKER_NAME: str = 'שם מדריכה'
    DAYCARE_NAME: str = 'שם המעון'
    SYMBOL: str = 'סמל'
    TOTAL_HOURS_LABEL: str = 'סה"כ שעות'
    TOTAL_PAY_LABEL: str = 'סה"כ לתשלום'
    DATE_TEMPLATE: str = 'תאריך ({month})'
    HOURS_TEMPLATE: str = 'שעות ({month})'
    RATE_TEMPLATE: str = 'תעריף ({month})'

@dataclass(frozen=True)
class InputFileFormats:
    salary_file: str = 'קובץ משכורות (CSV)'
    daycare_file: str = 'קובץ מעונות (Excel)'
    salary_columns: tuple[str, ...] = (
        SalaryColumns.FIRST_NAME,
        SalaryColumns.LAST_NAME,
        SalaryColumns.PERIOD,
        SalaryColumns.TOTAL_EMPLOYER_COST,
    )
    daycare_columns: tuple[str, ...] = ('שם המעון', 'סמל')


def month_column(name_template: str, month: int) -> str:
    return name_template.format(month=f"{month:02d}")


def format_period(year: int, month: int) -> str:
    return f"{year}/{month:02d}"


def parse_period(period: str) -> tuple[int, int] | None:
    if not isinstance(period, str):
        return None
    period = period.strip()
    try:
        year, month = map(int, period.split('/'))
        return year, month
    except ValueError:
        return None


def get_selection_instructions() -> str:
    salary_labels = ', '.join(InputFileFormats.salary_columns)
    daycare_labels = ', '.join(InputFileFormats.daycare_columns)

    return (
        "הנחיות מהירות:\n"
        f"• קובץ מעונות: בחר קובץ {InputFileFormats.daycare_file} עם עמודה ראשונה של {InputFileFormats.daycare_columns[0]}."
        f" אם יש עמודה שנייה, היא תשמש כסמל של המעון.\n"
        f"• קובץ משכורות: בחר קובץ {InputFileFormats.salary_file} עם עמודות {salary_labels}.\n"
        f"• העמודה '{SalaryColumns.PERIOD}' חייבת להיות בפורמט YYYY/MM, למשל 2024/05.\n"
        "• אם בקובץ המעונות יש רק עמודה אחת, המערכת תשתמש בה כשמות המעונות."
    )


def get_input_format_help() -> str:
    salary_labels = ', '.join(InputFileFormats.salary_columns)
    daycare_labels = ', '.join(InputFileFormats.daycare_columns)

    return (
        f"{get_selection_instructions()}\n\n"
        f"הקובץ הראשון הוא {InputFileFormats.daycare_file}.\n"
        f"העמודות שנמצאות בו הן: {daycare_labels}.\n"
        "אם הקובץ מכיל רק עמודה אחת, הוא ייקרא רק את שמות המעונות.\n\n"
        f"הקובץ השני הוא {InputFileFormats.salary_file}.\n"
        f"העמודות הנדרשות בו הן: {salary_labels}.\n"
        "הקובץ יכול להיות בקידוד UTF-8 או Windows-1255."
    )

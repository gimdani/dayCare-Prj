"""Scheduler utilities for work-date selection.

Provides `WorkDateScheduler`, a small, well-documented class that encapsulates
rules for which dates are valid work-days in an Israeli context. Rules are
configurable via constructor parameters so the logic is reusable and easy to
test.

Behavior (defaults):
- Exclude Fridays and Saturdays.
- Exclude full Jewish holidays detected by `pyluach` (e.g., Rosh Hashana,
  Yom Kippur, Sukkot, etc.).
- Exclude secular Israeli national holidays (Yom HaZikaron, Yom HaAtzmaut,
  Yom Yerushalayim) by default.
- Exclude "Erev" (the day before a holiday) when `exclude_eves=True`.

The class focuses only on determining valid dates and distributing dates
evenly across a month; it does not know anything about the payroll or
spreadsheet layout.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, List, Optional, Set, Tuple

from pyluach import dates


@dataclass
class WorkDateScheduler:
    """Decides whether a date is a valid work-day and selects dates.

    Parameters:
    - excluded_weekdays: iterable of Python weekday integers to exclude
      (Monday=0 .. Sunday=6). Defaults to exclude Friday (4) and Saturday (5).
    - excluded_hebrew_md: set of (month, day) tuples in Hebrew calendar to
      always exclude (useful for secular national holidays).
    - allowed_holidays: set of holiday names (as returned by pyluach)
      that should not be excluded even if pyluach recognizes them (e.g.
      Yom HaShoah if you want it permitted).
    - exclude_eves: whether to treat the day before a holiday as excluded.
    """

    excluded_weekdays: Set[int] = None
    excluded_hebrew_md: Set[Tuple[int, int]] = None
    allowed_holidays: Set[str] = None
    exclude_eves: bool = True

    def __post_init__(self) -> None:
        if self.excluded_weekdays is None:
            # Default: Friday and Saturday
            self.excluded_weekdays = {4, 5}

        if self.excluded_hebrew_md is None:
            # Default secular Israeli observances to exclude (month, day)
            # Month numbering: Nisan=1, Iyar=2, Sivan=3, ... per pyluach
            self.excluded_hebrew_md = {
                # Yom HaZikaron - 4 Iyar
                (2, 4),
                # Yom HaAtzmaut - 5 Iyar
                (2, 5),
                # Yom Yerushalayim - 28 Iyar
                (2, 28),
            }

        if self.allowed_holidays is None:
            # By default allow Yom HaShoah (27 Nisan) if pyluach reports it.
            self.allowed_holidays = {"Yom HaShoah"}

    def is_valid_workday(self, check_date: date) -> bool:
        """Return True if `check_date` is acceptable for scheduling work.

        The method applies these checks (short-circuiting on first failure):
        1. weekday exclusion (e.g., Friday/Saturday)
        2. pyluach-detected holiday (unless it's in `allowed_holidays`)
        3. exclusion by explicit Hebrew month/day tuple
        4. (optional) if it's the eve of a holiday
        """

        if check_date.weekday() in self.excluded_weekdays:
            return False

        heb = dates.HebrewDate.from_pydate(check_date)

        # pyluach may return a holiday name or object; handle both safely.
        hol = heb.holiday()
        if hol is not None:
            # Normalize to string name when possible
            hol_name = str(hol)
            if hol_name not in self.allowed_holidays:
                return False

        # Explicit secular holidays by Hebrew month/day
        if (heb.month, heb.day) in self.excluded_hebrew_md:
            return False

        if self.exclude_eves:
            # Check if tomorrow is a holiday or a secular excluded MD
            tomorrow = check_date + timedelta(days=1)
            heb_t = dates.HebrewDate.from_pydate(tomorrow)
            if heb_t.holiday() is not None:
                hol_name_t = str(heb_t.holiday())
                if hol_name_t not in self.allowed_holidays:
                    return False
            if (heb_t.month, heb_t.day) in self.excluded_hebrew_md:
                return False

        return True

    def get_evenly_distributed_dates(self, year: int, month: int, n_shifts: int) -> List[date]:
        """Return `n_shifts` dates in `year`/`month` distributed over valid days.

        If there are fewer valid days than `n_shifts` the returned list will
        cycle through valid days until the requested number is reached.
        """

        if n_shifts <= 0:
            return []

        import calendar

        num_days = calendar.monthrange(year, month)[1]
        all_days = [date(year, month, d) for d in range(1, num_days + 1)]
        valid_days = [d for d in all_days if self.is_valid_workday(d)]

        if not valid_days:
            return []

        if n_shifts >= len(valid_days):
            # Repeat the sequence if more shifts than valid days
            res: List[date] = []
            while len(res) < n_shifts:
                res.extend(valid_days)
            return res[:n_shifts]

        # Distribute by selecting approximate evenly spaced indices
        step = len(valid_days) / n_shifts
        indices = [min(int(i * step + step / 2), len(valid_days) - 1) for i in range(n_shifts)]
        return [valid_days[i] for i in indices]


__all__ = ["WorkDateScheduler"]

import re
from calendar import IllegalMonthError
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, ClassVar

from dateutil import parser

from reconcile.pylib import darwin_core as dwc
from reconcile.pylib.base import Base


@dataclass
class TraiterDate:
    key: str
    raw_date: str
    raw_verb: str
    has_roman: bool


@dataclass
class OpenaiDate:
    key: str
    raw_date: str


@dataclass
class MergedDates:
    openai: OpenaiDate | None = None
    traiter: TraiterDate | None = None


class EventDate(Base):
    label: ClassVar[str] = "dwc:eventDate"
    verbatim_label: ClassVar[str] = "dwc:verbatimEventDate"
    aliases: ClassVar[list[str]] = Base.get_aliases(
        label,
        """
        dwc:collectionDate dwc:earliestDateCollected dwc:latestDateCollected
        dwc:date """,
    )
    verbatim_aliases: ClassVar[list[str]] = Base.get_aliases(verbatim_label)

    clean_re: ClassVar[Any] = re.compile(r"date", flags=re.IGNORECASE | re.VERBOSE)

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, Any]:
        o_val = cls.search(other, cls.aliases)
        t_val = traiter.get(cls.label, "")
        t_verbatim = traiter.get(cls.verbatim_label, "")

        if not o_val or not t_val:
            return {}

        # Format dates
        all_dates = defaultdict(MergedDates)

        for o_date in cls.convert_openai_dates(o_val):
            all_dates[o_date.key].openai = o_date

        for t_date in cls.convert_traiter_dates(t_val, t_verbatim):
            all_dates[t_date.key].traiter = t_date

        # Determine which, if any, date to use
        use_dates = []
        use_verbs = []

        for merged_date in all_dates.values():
            if merged_date.traiter and merged_date.traiter.has_roman:
                use_dates.append(merged_date.traiter.raw_date)
                use_verbs.append(merged_date.traiter.raw_verb)

            elif merged_date.openai:
                use_dates.append(merged_date.openai.raw_date)
                if merged_date.traiter and merged_date.traiter.raw_verb:
                    use_verbs.append(merged_date.traiter.raw_verb)

        # Format output
        output = {}

        if use_dates:
            output[cls.label] = dwc.SEP.join(use_dates)

        if use_verbs:
            output[cls.verbatim_label] = dwc.SEP.join(use_verbs)

        return output

    @classmethod
    def convert_openai_dates(cls, o_val):
        """
        Convert OpenAI value(s) to a list of dates.

        It may be a proper date, a dict, a list, or a verbatim date.
        """
        # Put dates into list form
        if o_val and isinstance(o_val, str):
            date_list = [o_val]

        elif o_val and isinstance(o_val, list):
            date_list = [v for v in o_val if isinstance(v, str)]

        elif o_val and isinstance(o_val, dict):
            sub_keys = list(o_val.keys())
            if all(k in sub_keys for k in ("year", "month", "day")):
                date_list = [f"{o_val['year']}-{o_val['month']}-{o_val['day']}"]
            else:
                msg = f"BAD FORMAT in OpenAI {cls.label} {o_val}"
                raise ValueError(msg)

        else:
            msg = f"BAD FORMAT in OpenAI {cls.label} {o_val}"
            raise ValueError(msg)

        # Convert the dates
        try:
            o_dates = []
            for o_date in date_list:
                dt = parser.parse(o_date).date()
                key = dt.isoformat()
                o_dates.append(OpenaiDate(raw_date=o_date, key=key))
        except (parser.ParserError, IllegalMonthError) as err:
            msg = f"BAD FORMAT in OpenAI {cls.label} {o_val}"
            raise ValueError(msg) from err

        return o_dates

    @classmethod
    def convert_traiter_dates(cls, t_val, t_verbatim):
        t_dates = []
        try:
            raw_dates = t_val.split(dwc.SEP)
            raw_verbs = [cls.clean_re.sub("", d) for d in t_verbatim.split(dwc.SEP)]

            for raw_date, raw_verb in zip(raw_dates, raw_verbs, strict=True):
                dt = parser.parse(raw_date).date()

                t_dates.append(
                    TraiterDate(
                        key=dt.isoformat(),
                        raw_date=raw_date,
                        raw_verb=raw_verb,
                        has_roman=bool(re.search(r"[IXVixv]", raw_verb)),
                    )
                )
        except (parser.ParserError, IllegalMonthError) as err:
            msg = f"BAD FORMAT in Traiter {cls.label} {t_val}"
            raise ValueError(msg) from err
        return t_dates

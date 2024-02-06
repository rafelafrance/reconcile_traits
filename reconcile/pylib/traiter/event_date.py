import re
from calendar import IllegalMonthError
from typing import Any, ClassVar, NamedTuple

from dateutil import parser

from .. import darwin_core as dwc
from ..base import Base


class TraiterDate(NamedTuple):
    raw_date: str
    date: Any
    raw_verb: str
    verb: Any


class EventDate(Base):
    label: ClassVar[str] = "dwc:eventDate"
    verbatim_label = "dwc:verbatimEventDate"
    aliases: ClassVar[list[str]] = Base.get_aliases(
        label,
        """
        dwc:collectionDate dwc:earliestDateCollected dwc:latestDateCollected
        dwc:date """,
    )
    verbatim_aliases: ClassVar[list[str]] = Base.get_aliases(verbatim_label)

    clean_re: ClassVar[Any] = re.compile(r"date", flags=re.IGNORECASE | re.VERBOSE)

    roman: ClassVar[dict[str, str]] = {
        "i": " January ",
        "ii": " February ",
        "iii": " March ",
        "iv": " April ",
        "v": " May ",
        "vi": " June ",
        "vii": " July ",
        "viii": " August ",
        "ix": " September ",
        "x": " October ",
        "xi": " November ",
        "xii": " December ",
    }
    roman_re: ClassVar[Any] = re.compile(
        rf"( \b {'|'.join(k for k in roman)} \b )",
        flags=re.IGNORECASE | re.VERBOSE,
    )

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, Any]:
        o_val = cls.search(other, cls.aliases)
        t_val = traiter.get(cls.label, "")
        t_verbatim = traiter.get(cls.verbatim_label, "")

        if not o_val or not t_val:
            return {}

        o_dates = cls.convert_openai_dates(o_val)
        t_dates = cls.convert_traiter_dates(t_val, t_verbatim)

        dates = []
        for o_date in o_dates:
            for t_date in t_dates:
                if o_date in (t_date.date, t_date.verb):
                    dates.append(t_date)  # noqa: PERF401

        if not dates:
            return {}

        return {
            cls.label: dwc.SEP.join([d.raw_date for d in dates]),
            cls.verbatim_label: dwc.SEP.join([d.raw_verb for d in dates]),
        }

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
                dt = cls.roman_re.sub(cls.roman_replace, o_date)
                dt = parser.parse(dt).date()
                o_dates.append(dt)
        except (parser.ParserError, IllegalMonthError) as err:
            msg = f"BAD FORMAT in OpenAI {cls.label} {o_val}"
            raise ValueError(msg) from err

        return o_dates

    @classmethod
    def roman_replace(cls, match):
        return cls.roman.get(match.group(0).lower())

    @classmethod
    def convert_traiter_dates(cls, t_val, t_verbatim):
        t_dates = []
        try:
            raw_dates = t_val.split(dwc.SEP)
            raw_verbs = [cls.clean_re.sub("", d) for d in t_verbatim.split(dwc.SEP)]

            for raw_date, raw_verb in zip(raw_dates, raw_verbs, strict=True):
                verb = cls.roman_re.sub(cls.roman_replace, raw_verb)
                verb = parser.parse(verb).date()

                t_dates.append(
                    TraiterDate(
                        raw_date,
                        parser.parse(raw_date).date(),
                        raw_verb,
                        verb,
                    )
                )
        except (parser.ParserError, IllegalMonthError) as err:
            msg = f"BAD FORMAT in Traiter {cls.label} {t_val}"
            raise ValueError(msg) from err
        return t_dates

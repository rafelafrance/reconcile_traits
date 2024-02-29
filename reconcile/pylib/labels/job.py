import re
from typing import Any, ClassVar

from reconcile.pylib import darwin_core as dwc
from reconcile.pylib.base import Base


class Job(Base):
    rec_lb: ClassVar[str] = "dwc:recordedBy"
    id_lb: ClassVar[str] = "dwc:identifiedBy"
    rec_match: ClassVar[list[str]] = Base.get_aliases(rec_lb, """dwc:recordedByName""")
    id_match: ClassVar[list[str]] = Base.get_aliases(id_lb)
    record_no: ClassVar[str] = "dwc:recordNumber"

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, Any]:
        o_rec = cls.search(other, cls.rec_match)
        o_id = cls.search(other, cls.id_match)

        obj = {}

        # Use OpenAI output
        if o_rec:
            if isinstance(o_rec, list):
                obj[cls.rec_lb] = dwc.SEP.join([j for j in o_rec if isinstance(j, str)])
            else:
                obj[cls.rec_lb] = o_rec

        if match := re.search(r"\s*\d+$", obj[cls.rec_lb]):
            obj[cls.rec_lb] = obj[cls.rec_lb].removesuffix(match.group(0))
            obj[cls.record_no] = match.group(0).strip()

        if o_id:
            obj[cls.id_lb] = o_id

        return obj

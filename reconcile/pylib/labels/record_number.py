from typing import Any, ClassVar

import reconcile.pylib.darwin_core as dwc
from reconcile.pylib.base import Base


class RecordNumber(Base):
    label: ClassVar[str] = "dwc:recordNumber"
    aliases: ClassVar[list[str]] = Base.get_aliases(
        label, "dwc:record dwc:recordId dwc:recordedNumber dwc:catalogNumber"
    )
    is_labeled_key: ClassVar[str] = "recordNumberIsLabeled"
    cat_label: ClassVar[str] = "dwc:catalogNumber"

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, str]:
        # Use the traiter version if it is a labeled ID number & there is only 1
        if (
            dwc.is_labeled(traiter, cls.label, cls.is_labeled_key)
            and dwc.field_len(traiter[cls.label]) == 1
        ):
            return {cls.label: traiter[cls.label]}

        # Sometimes GPT labels the recordNuber as catalogNumber
        # If it matches what's in the traiter version, use it
        if traiter.get(cls.label) and traiter[cls.label] == other.get(cls.cat_label):
            return {cls.label: traiter[cls.label]}

        # Default to the GPT version if there is one
        if val := cls.search(other, cls.aliases):
            return {cls.label: val}

        return {}

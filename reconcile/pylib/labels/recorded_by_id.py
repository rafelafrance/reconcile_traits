from typing import Any, ClassVar

import reconcile.pylib.darwin_core as dwc
from reconcile.pylib.base import Base


class RecordedById(Base):
    label: ClassVar[str] = "dwc:recordedByID"
    aliases: ClassVar[list[str]] = Base.get_aliases(label, "dwc:recordedById")
    is_labeled_key: ClassVar[str] = "recordedByIDIsLabeled"

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

        # Default to the GPT version if there is one
        if val := cls.search(other, cls.aliases):
            return {cls.label: val}

        return {}

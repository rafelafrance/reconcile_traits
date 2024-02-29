from typing import Any, ClassVar

from reconcile.pylib.base import Base


class RecordNumber(Base):
    label: ClassVar[str] = "dwc:recordNumber"
    aliases: ClassVar[list[str]] = Base.get_aliases(
        label, "dwc:record dwc:recordId dwc:recordedNumber"
    )

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, str]:
        # Default to the GPT version
        if val := cls.search(other, cls.aliases):
            return {cls.label: val}
        return {}

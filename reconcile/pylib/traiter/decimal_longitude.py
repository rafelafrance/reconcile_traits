from typing import Any, ClassVar

from ..base import Base


class DecimalLongitude(Base):
    label: ClassVar[str] = "dwc:decimalLongitude"
    aliases: ClassVar[list[str]] = Base.get_aliases(
        label, "dwc:longitude dwc:verbatimLongitude"
    )

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, str]:
        if o_val := cls.search(other, cls.aliases):
            return {cls.label: o_val}
        return {}

from typing import Any, ClassVar

from reconcile.pylib.base import Base


class VerbatimCoordinateSystem(Base):
    label: ClassVar[str] = "dwc:verbatimCoordinateSystem"
    aliases: ClassVar[list[str]] = Base.get_aliases(label, "dwc:coordinateSystem")

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, str]:
        if o_val := cls.search(other, cls.aliases):
            return {cls.label: o_val}
        return {}

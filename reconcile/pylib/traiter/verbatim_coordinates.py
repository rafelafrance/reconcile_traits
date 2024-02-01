from typing import Any, ClassVar

from reconcile.pylib.base import Base


class VerbatimCoordinates(Base):
    label: ClassVar[str] = "dwc:verbatimCoordinates"
    aliases: ClassVar[list[str]] = Base.get_aliases(label, "dwc:coordinates")

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, str]:
        if o_val := cls.search(other, cls.aliases):
            return {cls.label: o_val}
        if t_val := traiter.get(cls.label):
            return {cls.label: t_val}
        return {}

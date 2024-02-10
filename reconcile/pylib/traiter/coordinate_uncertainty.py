from typing import Any, ClassVar

from reconcile.pylib.base import Base
from reconcile.pylib.darwin_core import SEP


class CoordinateUncertainty(Base):
    label: ClassVar[str] = "dwc:coordinateUncertaintyInMeters"
    aliases: ClassVar[list[str]] = Base.get_aliases(label, "")

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, str]:
        o_val = cls.search(other, cls.aliases)

        if isinstance(o_val, list):
            return {cls.label: SEP.join(o_val)}
        if o_val:
            return {cls.label: o_val}
        if t_val := traiter.get(cls.label):
            return {cls.label: t_val}
        return {}

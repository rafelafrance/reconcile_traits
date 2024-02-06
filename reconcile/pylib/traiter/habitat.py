from typing import Any, ClassVar

from ..base import Base


class Habitat(Base):
    label: ClassVar[str] = "dwc:habitat"
    aliases: ClassVar[list[str]] = Base.get_aliases(label)

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, Any]:
        if o_val := cls.search(other, cls.aliases):
            return {cls.label: o_val}
        return {}

from typing import Any, ClassVar

from ..base import Base


class AdminUnit(Base):
    country_lb: ClassVar[str] = "dwc:country"
    code_lb: ClassVar[str] = "dwc:countryCode"
    st_lb: ClassVar[str] = "dwc:stateProvince"
    co_lb: ClassVar[str] = "dwc:county"
    muni_lb: ClassVar[str] = "dwc:municipality"

    country_match: ClassVar[list[str]] = Base.get_aliases(country_lb)
    code_match: ClassVar[list[str]] = Base.get_aliases(code_lb)
    st_match: ClassVar[list[str]] = Base.get_aliases(
        st_lb, "dwc:locationState dwc:state dwc:province"
    )
    co_match: ClassVar[list[str]] = Base.get_aliases(co_lb)
    muni_match: ClassVar[list[str]] = Base.get_aliases(muni_lb)

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, str]:
        obj = {}

        if val := cls.search(other, cls.country_match):
            obj[cls.country_lb] = val

        if val := cls.search(other, cls.code_match):
            obj[cls.code_lb] = val

        if val := cls.search(other, cls.st_match):
            obj[cls.st_lb] = val

        if val := cls.search(other, cls.co_match):
            obj[cls.co_lb] = val

        if val := cls.search(other, cls.muni_match):
            obj[cls.muni_lb] = val

        return obj

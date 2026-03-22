from sqlmodel import Field, SQLModel
from datetime import date

class LicenseBase(SQLModel):
    organization: str = Field(index=None)
    disabled: bool = False
    start_date: date
    end_date: date

class License(LicenseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    check_sum: int

class LicensePublic(LicenseBase):
    id: int

class LicenseCreate(LicenseBase):
    check_sum: int

class LicenseUpdate(LicenseBase):
    organization: str | None = None
    disabled: bool | None = None
    start_date: date | None = None
    end_date: date | None = None
    check_sum: str | None = None
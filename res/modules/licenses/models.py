from sqlmodel import Field, SQLModel
from datetime import date

class OrganizationIn(SQLModel):
    name: str
    inn: str
    email: str
    tariff: str
    licenses: int
    expiry: str

class ChecksumIn(SQLModel):
    algorithm: str
    value: str

class HostIn(SQLModel):
    hostname: str
    os: str
    mac: str
    uuid: str
    comment: str

class LicenseFromFront(SQLModel):
    organization: OrganizationIn
    checksum: ChecksumIn
    host: HostIn

class LicenseBase(SQLModel):
    name: str = Field(index=None)
    inn: str
    email: str
    tariff: str
    disabled: bool = False
    hostname: str
    os: str
    mac: str
    uuid: str
    comment: str
    start_date: date
    end_date: date

class License(LicenseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    checksum: str


class LicensePublic(LicenseBase):
    id: int

class LicenseCreate(LicenseBase):
    checksum: str

class LicenseUpdate(LicenseBase):
    name: str = Field(index=None)
    inn: str
    email: str
    tariff: str
    disabled: bool = False
    hostname: str
    os: str
    mac: str
    uuid: str
    comment: str
    start_date: date
    end_date: date
    checksum: str
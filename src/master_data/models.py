from dataclasses import dataclass, field


@dataclass(frozen=True)
class Record:
    source: str
    ref: str
    kind: str
    name: str
    inn: str = ""
    kpp: str = ""
    sku: str = ""
    manufacturer_sku: str = ""
    brand: str = ""
    bank_account: str = ""
    phone: str = ""
    email: str = ""
    unit: str = ""
    pack_size: str = ""

    @property
    def key(self) -> str:
        return f"{self.source}:{self.ref}"


@dataclass(frozen=True)
class Provenance:
    value: str
    source: str
    observed_at: str
    verified: bool = False
    confidence: float = 1.0


@dataclass(frozen=True)
class Candidate:
    left: Record
    right: Record
    blocks: tuple[str, ...]


@dataclass
class Resolution:
    decision: str
    confidence: float
    features: dict[str, object]
    reasons: list[str] = field(default_factory=list)

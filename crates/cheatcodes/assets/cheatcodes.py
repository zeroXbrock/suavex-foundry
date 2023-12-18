import json
from enum import Enum
from types import SimpleNamespace


class Status(Enum):
    STABLE: str = "stable"
    EXPERIMENTAL: str = "experimental"
    DEPRECATED: str = "deprecated"
    REMOVED: str = "removed"


class Group(Enum):
    EVM: str = "evm"
    TESTING: str = "testing"
    SCRIPTING: str = "scripting"
    FILESYSTEM: str = "filesystem"
    ENVIRONMENT: str = "environment"
    STRING: str = "string"
    JSON: str = "json"
    UTILITIES: str = "utilities"


class Safety(Enum):
    UNSAFE: str = "unsafe"
    SAFE: str = "safe"

    def is_safe(self) -> bool:
        return self == Safety.SAFE


class Visibility(Enum):
    EXTERNAL: str = "external"
    PUBLIC: str = "public"
    INTERNAL: str = "internal"
    PRIVATE: str = "private"


class Mutability(Enum):
    PURE: str = "pure"
    VIEW: str = "view"
    NONE: str = ""


class Function:
    id: str
    description: str
    declaration: str
    visibility: Visibility
    mutability: Mutability
    signature: str
    selector: str
    selector_bytes: bytes

    def __init__(
        self,
        id: str,
        description: str,
        declaration: str,
        visibility: Visibility,
        mutability: Mutability,
        signature: str,
        selector: str,
        selector_bytes: bytes,
    ):
        self.id = id
        self.description = description
        self.declaration = declaration
        self.visibility = visibility
        self.mutability = mutability
        self.signature = signature
        self.selector = selector
        self.selector_bytes = selector_bytes


class Cheatcode:
    func: Function
    group: Group
    status: Status
    safety: Safety

    def __init__(self, func: Function, group: Group, status: Status, safety: Safety):
        self.func = func
        self.group = group
        self.status = status
        self.safety = safety


class Error:
    name: str
    description: str
    declaration: str

    def __init__(self, name: str, description: str, declaration: str):
        self.name = name
        self.description = description
        self.declaration = declaration


class Event:
    name: str
    description: str
    declaration: str

    def __init__(self, name: str, description: str, declaration: str):
        self.name = name
        self.description = description
        self.declaration = declaration


class EnumVariant:
    name: str
    description: str

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class Enum:
    name: str
    description: str
    variants: list[EnumVariant]

    def __init__(self, name: str, description: str, variants: list[EnumVariant]):
        self.name = name
        self.description = description
        self.variants = variants


class StructField:
    name: str
    ty: str
    description: str

    def __init__(self, name: str, ty: str, description: str):
        self.name = name
        self.ty = ty
        self.description = description


class Struct:
    name: str
    description: str
    fields: list[StructField]

    def __init__(self, name: str, description: str, fields: list[StructField]):
        self.name = name
        self.description = description
        self.fields = fields


class Cheatcodes:
    errors: list[Error]
    events: list[Event]
    enums: list[Enum]
    structs: list[Struct]
    cheatcodes: list[Cheatcode]

    def __init__(
        self,
        errors: list[Error],
        events: list[Event],
        enums: list[Enum],
        structs: list[Struct],
        cheatcodes: list[Cheatcode],
    ):
        self.errors = errors
        self.events = events
        self.enums = enums
        self.structs = structs
        self.cheatcodes = cheatcodes

    @staticmethod
    def from_json_file(file_path: str):
        with open(file_path, "r") as f:
            return json.load(f, object_hook=lambda d: SimpleNamespace(**d))


cheatcodes = Cheatcodes.from_json_file("crates/cheatcodes/assets/cheatcodes.json")
print(cheatcodes)

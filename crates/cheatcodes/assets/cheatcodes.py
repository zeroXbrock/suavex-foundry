import json
from enum import Enum as PyEnum


class Status(PyEnum):
    STABLE: str = "stable"
    EXPERIMENTAL: str = "experimental"
    DEPRECATED: str = "deprecated"
    REMOVED: str = "removed"


class Group(PyEnum):
    EVM: str = "evm"
    TESTING: str = "testing"
    SCRIPTING: str = "scripting"
    FILESYSTEM: str = "filesystem"
    ENVIRONMENT: str = "environment"
    STRING: str = "string"
    JSON: str = "json"
    UTILITIES: str = "utilities"


class Safety(PyEnum):
    UNSAFE: str = "unsafe"
    SAFE: str = "safe"


class Visibility(PyEnum):
    EXTERNAL: str = "external"
    PUBLIC: str = "public"
    INTERNAL: str = "internal"
    PRIVATE: str = "private"


class Mutability(PyEnum):
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

    @staticmethod
    def from_dict(d: dict) -> "Function":
        return Function(
            d["id"],
            d["description"],
            d["declaration"],
            Visibility(d["visibility"]),
            Mutability(d["mutability"]),
            d["signature"],
            d["selector"],
            bytes(d["selectorBytes"]),
        )


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

    @staticmethod
    def from_dict(d: dict) -> "Cheatcode":
        return Cheatcode(
            Function.from_dict(d["func"]),
            Group(d["group"]),
            Status(d["status"]),
            Safety(d["safety"]),
        )


class Error:
    name: str
    description: str
    declaration: str

    def __init__(self, name: str, description: str, declaration: str):
        self.name = name
        self.description = description
        self.declaration = declaration

    @staticmethod
    def from_dict(d: dict) -> "Error":
        return Error(**d)


class Event:
    name: str
    description: str
    declaration: str

    def __init__(self, name: str, description: str, declaration: str):
        self.name = name
        self.description = description
        self.declaration = declaration

    @staticmethod
    def from_dict(d: dict) -> "Event":
        return Event(**d)


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

    @staticmethod
    def from_dict(d: dict) -> "Enum":
        return Enum(
            d["name"],
            d["description"],
            list(map(lambda v: EnumVariant(**v), d["variants"])),
        )


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

    @staticmethod
    def from_dict(d: dict) -> "Struct":
        return Struct(
            d["name"],
            d["description"],
            list(map(lambda f: StructField(**f), d["fields"])),
        )


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
    def from_dict(d: dict) -> "Cheatcodes":
        return Cheatcodes(
            errors=[Error.from_dict(e) for e in d["errors"]],
            events=[Event.from_dict(e) for e in d["events"]],
            enums=[Enum.from_dict(e) for e in d["enums"]],
            structs=[Struct.from_dict(e) for e in d["structs"]],
            cheatcodes=[Cheatcode.from_dict(e) for e in d["cheatcodes"]],
        )

    @staticmethod
    def from_json(s) -> "Cheatcodes":
        return Cheatcodes.from_dict(json.loads(s))

    @staticmethod
    def from_json_file(file_path: str) -> "Cheatcodes":
        with open(file_path, "r") as f:
            return Cheatcodes.from_dict(json.load(f))

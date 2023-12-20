import json
from enum import Enum as PyEnum
from typing import Callable

VoidFn = Callable[[], None]


def main():
    pass


class Status(PyEnum):
    STABLE: str = "stable"
    EXPERIMENTAL: str = "experimental"
    DEPRECATED: str = "deprecated"
    REMOVED: str = "removed"

    def __lt__(self, other: "Group") -> bool:
        return self.value < other.value


class Group(PyEnum):
    EVM: str = "evm"
    TESTING: str = "testing"
    SCRIPTING: str = "scripting"
    FILESYSTEM: str = "filesystem"
    ENVIRONMENT: str = "environment"
    STRING: str = "string"
    JSON: str = "json"
    UTILITIES: str = "utilities"

    def __lt__(self, other: "Group") -> bool:
        return self.value < other.value


class Safety(PyEnum):
    UNSAFE: str = "unsafe"
    SAFE: str = "safe"

    def __lt__(self, other: "Group") -> bool:
        return self.value < other.value


class Visibility(PyEnum):
    EXTERNAL: str = "external"
    PUBLIC: str = "public"
    INTERNAL: str = "internal"
    PRIVATE: str = "private"

    def __str__(self):
        return self.value


class Mutability(PyEnum):
    PURE: str = "pure"
    VIEW: str = "view"
    NONE: str = ""

    def __str__(self):
        return self.value


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


class Item(PyEnum):
    ERROR: str = "error"
    EVENT: str = "event"
    ENUM: str = "enum"
    STRUCT: str = "struct"
    FUNCTION: str = "function"


class ItemOrder:
    _list: list[Item]

    def __init__(self, list: list[Item]) -> None:
        assert len(list) <= len(Item), "list must not contain more items than Item"
        assert len(list) == len(set(list)), "list must not contain duplicates"
        self._list = list
        pass

    def get_list(self) -> list[Item]:
        return self._list

    @staticmethod
    def default() -> "ItemOrder":
        return ItemOrder(
            [
                Item.ERROR,
                Item.EVENT,
                Item.ENUM,
                Item.STRUCT,
                Item.FUNCTION,
            ]
        )


class CheatcodesPrinter:
    buffer: str

    prelude: bool
    spdx_identifier: str
    solidity_requirement: str
    abicoder_v2: bool

    block_doc_style: bool

    indent_level: int
    _indent_str: str

    nl_str: str

    items_order: ItemOrder

    def __init__(
        self,
        buffer: str = "",
        prelude: bool = True,
        spdx_identifier: str = "UNLICENSED",
        solidity_requirement: str = "",
        abicoder_pragma: bool = False,
        block_doc_style: bool = False,
        indent_level: int = 0,
        indent_with: int | str = 4,
        nl_str: str = "\n",
        items_order: ItemOrder = ItemOrder.default(),
    ):
        self.prelude = prelude
        self.spdx_identifier = spdx_identifier
        self.solidity_requirement = solidity_requirement
        self.abicoder_v2 = abicoder_pragma
        self.block_doc_style = block_doc_style
        self.buffer = buffer
        self.indent_level = indent_level
        self.nl_str = nl_str

        if isinstance(indent_with, int):
            assert indent_with >= 0
            self._indent_str = " " * indent_with
        elif isinstance(indent_with, str):
            self._indent_str = indent_with
        else:
            assert False, "indent_with must be int or str"

        self.items_order = items_order

    def finish(self) -> str:
        ret = self.buffer.rstrip()
        self.buffer = ""
        return ret

    def p_contract(self, contract: Cheatcodes, name: str, inherits: str = ""):
        if self.prelude:
            self.p_prelude(contract)

        self._p_str("interface ")
        name = name.strip()
        if name != "":
            self._p_str(name)
            self._p_str(" ")
        if inherits != "":
            self._p_str("is ")
            self._p_str(inherits)
            self._p_str(" ")
        self._p_str("{")
        self._p_nl()
        self._with_indent(lambda: self._p_items(contract))
        self._p_str("}")
        self._p_nl()

    def _p_items(self, contract: Cheatcodes):
        for item in self.items_order.get_list():
            if item == Item.ERROR:
                self.p_errors(contract.errors)
            elif item == Item.EVENT:
                self.p_events(contract.events)
            elif item == Item.ENUM:
                self.p_enums(contract.enums)
            elif item == Item.STRUCT:
                self.p_structs(contract.structs)
            elif item == Item.FUNCTION:
                self.p_functions(contract.cheatcodes)
            else:
                assert False, f"unknown item {item}"

    def p_prelude(self, contract: Cheatcodes | None = None):
        self._p_str(f"// SPDX-License-Identifier: {self.spdx_identifier}")
        self._p_nl()

        if self.solidity_requirement != "":
            req = self.solidity_requirement
        elif contract and len(contract.errors) > 0:
            req = ">=0.8.4 <0.9.0"
        else:
            req = ">=0.6.0 <0.9.0"
        self._p_str(f"pragma solidity {req};")
        self._p_nl()

        if self.abicoder_v2:
            self._p_str("pragma experimental ABIEncoderV2;")
            self._p_nl()

        self._p_nl()

    def p_errors(self, errors: list[Error]):
        for error in errors:
            self._p_line(lambda: self.p_error(error))

    def p_error(self, error: Error):
        self._p_comment(error.description, doc=True)
        self._p_line(lambda: self._p_str(error.declaration))

    def p_events(self, events: list[Event]):
        for event in events:
            self._p_line(lambda: self.p_event(event))

    def p_event(self, event: Event):
        self._p_comment(event.description, doc=True)
        self._p_line(lambda: self._p_str(event.declaration))

    def p_enums(self, enums: list[Enum]):
        for enum in enums:
            self._p_line(lambda: self.p_enum(enum))

    def p_enum(self, enum: Enum):
        self._p_comment(enum.description, doc=True)
        self._p_line(lambda: self._p_str(f"enum {enum.name} {{"))
        self._with_indent(lambda: self.p_enum_variants(enum.variants))
        self._p_line(lambda: self._p_str("}"))

    def p_enum_variants(self, variants: list[EnumVariant]):
        for i, variant in enumerate(variants):
            self._p_indent()
            self._p_comment(variant.description)

            self._p_indent()
            self._p_str(variant.name)
            if i < len(variants) - 1:
                self._p_str(",")
            self._p_nl()

    def p_structs(self, structs: list[Struct]):
        for struct in structs:
            self._p_line(lambda: self.p_struct(struct))

    def p_struct(self, struct: Struct):
        self._p_comment(struct.description, doc=True)
        self._p_line(lambda: self._p_str(f"struct {struct.name} {{"))
        self._with_indent(lambda: self.p_struct_fields(struct.fields))
        self._p_line(lambda: self._p_str("}"))

    def p_struct_fields(self, fields: list[StructField]):
        for field in fields:
            self._p_line(lambda: self.p_struct_field(field))

    def p_struct_field(self, field: StructField):
        self._p_comment(field.description)
        self._p_indented(lambda: self._p_str(f"{field.ty} {field.name};"))

    def p_functions(self, cheatcodes: list[Cheatcode]):
        for cheatcode in cheatcodes:
            self._p_line(lambda: self.p_function(cheatcode.func))

    def p_function(self, func: Function):
        self._p_comment(func.description, doc=True)
        self._p_line(lambda: self._p_str(func.declaration))

    def _p_comment(self, s: str, doc: bool = False):
        s = s.strip()
        if s == "":
            return

        s = map(lambda line: line.lstrip(), s.split("\n"))
        if self.block_doc_style:
            self._p_str("/*")
            if doc:
                self._p_str("*")
            self._p_nl()
            for line in s:
                self._p_indent()
                self._p_str(" ")
                if doc:
                    self._p_str("* ")
                self._p_str(line)
                self._p_nl()
            self._p_indent()
            self._p_str(" */")
            self._p_nl()
        else:
            first_line = True
            for line in s:
                if not first_line:
                    self._p_indent()
                first_line = False

                if doc:
                    self._p_str("/// ")
                else:
                    self._p_str("// ")
                self._p_str(line)
                self._p_nl()

    def _with_indent(self, f: VoidFn):
        self._inc_indent()
        f()
        self._dec_indent()

    def _p_line(self, f: VoidFn):
        self._p_indent()
        f()
        self._p_nl()

    def _p_indented(self, f: VoidFn):
        self._p_indent()
        f()

    def _p_indent(self):
        for _ in range(self.indent_level):
            self._p_str(self._indent_str)

    def _p_nl(self):
        self._p_str(self.nl_str)

    def _p_str(self, txt: str):
        self.buffer += txt

    def _inc_indent(self):
        self.indent_level += 1

    def _dec_indent(self):
        self.indent_level -= 1


if __name__ == "__main__":
    main()

from typing import Optional, Union, Dict, List
from pygraphql import (
    Object,
    Field,
    ResolverField,
    Enum,
    Union as GraphQLUnion,
    Input,
    Schema
)


def test_model_definition():
    class Foo(Object):
        "description bar"
        a: str
        @Object.field
        def foo(self, a: int) -> Optional[str]:
            "description foo"
            pass

    assert Foo.__fields__ == {
        'a': Field(name='a', ftype=str, description=None),
        'foo': ResolverField(
            name='foo',
            ftype=Union[str, None],
            description='description foo', params={'a': int}
        )
    }
    assert Foo.__description__ == "description bar"

    try:
        class Foo(Object):
            @Object.field
            def foo(self, a: int) -> Dict:
                "description foo"
                pass
    except ValueError:
        return
    assert False  # never reached


def test_resolver_field_definition():
    class Foo(Object):
        "description bar"
        a: str
        @Object.field
        def foo(self, a: int) -> Optional[str]:
            "description foo"
            pass

    foo_field = Foo.__fields__['foo']
    assert foo_field.description == "description foo"
    assert foo_field.params['a'] == int


def test_field_definition():
    class Foo(Object):
        "description bar"
        a: Optional[str]

    assert Foo.__fields__['a'].ftype == Optional[str]


def test_model_literal():
    class Foo(Object):
        "description bar"
        a: str
        @Object.field
        def foo(self, a: int) -> Optional[List[str]]:
            "description foo"
            pass
    assert str(Foo) == '"""\ndescription bar\n"""\ntype Foo {\n  a: String!\n  "description foo"\n  foo(\n    a: Int!\n  ): [String!]\n}'


def test_enum_definition():
    class Foo(Enum):
        BAR = 1
        BAZ = 2
    assert str(Foo) == 'enum Foo {\n  BAR\n  BAZ\n}'


def test_union_definition():
    class Foo(Object):
        a: int

    class Bar(Object):
        a: str

    class FooBar(GraphQLUnion):
        members = (Foo, Bar)

    assert str(Foo) == '"""\nFoo(a: int)\n"""\ntype Foo {\n  a: Int!\n}'

    try:
        class FooInt(GraphQLUnion):
            members = (Foo, int)
    except RuntimeError:
        return
    assert False


def test_input_definition():
    class Foo(Input):
        a: str

    class Bar(Input):
        b: Foo

    class Query(Object):
        @Object.field
        def foo_a(self, a: Bar) -> Optional[str]:
            return 'test'

    class PySchema(Schema):
        query: Query

    assert str(PySchema) == '''"""
Query()
"""
type Query {
  fooA(
    a: Bar!
  ): String
}

"""
Bar(b: tests.test_definition.test_input_definition.<locals>.Foo)
"""
input Bar {
  b: Foo!
}

"""
Foo(a: str)
"""
input Foo {
  a: String!
}

"""
PySchema(query: tests.test_definition.test_input_definition.<locals>.Query)
"""
schema {
  query: Query!
}'''


def test_schema_definition():
    class Foo(Object):
        a: str

    class Bar(Object):
        a: int

    class FooBar(GraphQLUnion):
        members = (Foo, Bar)

    class Query(Object):
        @Object.field
        def foo_a(self, a: FooBar) -> Optional[str]:
            return 'test'

    class PySchema(Schema):
        query: Query

    assert str(PySchema) == '''"""
Query()
"""
type Query {
  fooA(
    a: FooBar!
  ): String
}

union FooBar =
  | Foo
  | Bar

"""
Foo(a: str)
"""
type Foo {
  a: String!
}

"""
Bar(a: int)
"""
type Bar {
  a: Int!
}

"""
PySchema(query: tests.test_definition.test_schema_definition.<locals>.Query)
"""
schema {
  query: Query!
}'''

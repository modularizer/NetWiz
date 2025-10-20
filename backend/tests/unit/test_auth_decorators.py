"""
Comprehensive tests for authentication decorators
"""

import asyncio

import pytest

from netwiz_backend.auth.decorators import (
    ADMIN,
    AUTH,
    OPTIONAL_AUTH,
    PUBLIC,
    DuplicateTagError,
    auth_tag,
    get_auth_level,
    get_tag,
    get_tags,
    is_admin_required,
    requires_auth,
    tag,
)


class TestDecoratorApplication:
    """Test decorator application to different function types"""

    def test_public_decorator_on_async_function(self):
        """Test @PUBLIC decorator on async function"""

        @PUBLIC
        async def async_func():
            return "async public"

        assert hasattr(async_func, "__auth_required__")
        assert hasattr(async_func, "__auth_level__")
        assert async_func.__auth_required__ is False
        assert async_func.__auth_level__ == "public"

    def test_public_decorator_on_sync_function(self):
        """Test @PUBLIC decorator on sync function"""

        @PUBLIC
        def sync_func():
            return "sync public"

        assert hasattr(sync_func, "__auth_required__")
        assert hasattr(sync_func, "__auth_level__")
        assert sync_func.__auth_required__ is False
        assert sync_func.__auth_level__ == "public"

    def test_auth_decorator_on_async_function(self):
        """Test @AUTH decorator on async function"""

        @AUTH
        async def async_func():
            return "async auth"

        assert hasattr(async_func, "__auth_required__")
        assert hasattr(async_func, "__auth_level__")
        assert async_func.__auth_required__ is True
        assert async_func.__auth_level__ == "user"

    def test_auth_decorator_on_sync_function(self):
        """Test @AUTH decorator on sync function"""

        @AUTH
        def sync_func():
            return "sync auth"

        assert hasattr(sync_func, "__auth_required__")
        assert hasattr(sync_func, "__auth_level__")
        assert sync_func.__auth_required__ is True
        assert sync_func.__auth_level__ == "user"

    def test_admin_decorator_on_async_function(self):
        """Test @ADMIN decorator on async function"""

        @ADMIN
        async def async_func():
            return "async admin"

        assert hasattr(async_func, "__auth_required__")
        assert hasattr(async_func, "__auth_level__")
        assert async_func.__auth_required__ is True
        assert async_func.__auth_level__ == "admin"

    def test_admin_decorator_on_sync_function(self):
        """Test @ADMIN decorator on sync function"""

        @ADMIN
        def sync_func():
            return "sync admin"

        assert hasattr(sync_func, "__auth_required__")
        assert hasattr(sync_func, "__auth_level__")
        assert sync_func.__auth_required__ is True
        assert sync_func.__auth_level__ == "admin"

    def test_optional_auth_decorator_on_async_function(self):
        """Test @OPTIONAL_AUTH decorator on async function"""

        @OPTIONAL_AUTH
        async def async_func():
            return "async optional"

        assert hasattr(async_func, "__auth_required__")
        assert hasattr(async_func, "__auth_level__")
        assert async_func.__auth_required__ is False
        assert async_func.__auth_level__ == "optional"

    def test_optional_auth_decorator_on_sync_function(self):
        """Test @OPTIONAL_AUTH decorator on sync function"""

        @OPTIONAL_AUTH
        def sync_func():
            return "sync optional"

        assert hasattr(sync_func, "__auth_required__")
        assert hasattr(sync_func, "__auth_level__")
        assert sync_func.__auth_required__ is False
        assert sync_func.__auth_level__ == "optional"


class TestDecoratorOnClassMethods:
    """Test decorators on different types of class methods"""

    def test_decorator_on_instance_method(self):
        """Test decorators on instance methods"""

        class TestClass:
            @PUBLIC
            def instance_method(self):
                return "instance public"

            @AUTH
            def instance_auth_method(self):
                return "instance auth"

            @ADMIN
            def instance_admin_method(self):
                return "instance admin"

        obj = TestClass()

        # Test instance method attributes
        assert hasattr(obj.instance_method, "__auth_required__")
        assert obj.instance_method.__auth_required__ is False
        assert obj.instance_method.__auth_level__ == "public"

        assert hasattr(obj.instance_auth_method, "__auth_required__")
        assert obj.instance_auth_method.__auth_required__ is True
        assert obj.instance_auth_method.__auth_level__ == "user"

        assert hasattr(obj.instance_admin_method, "__auth_required__")
        assert obj.instance_admin_method.__auth_required__ is True
        assert obj.instance_admin_method.__auth_level__ == "admin"

    def test_decorator_on_class_method(self):
        """Test decorators on class methods"""

        class TestClass:
            @classmethod
            @PUBLIC
            def class_method(cls):
                return "class public"

            @classmethod
            @AUTH
            def class_auth_method(cls):
                return "class auth"

            @classmethod
            @ADMIN
            def class_admin_method(cls):
                return "class admin"

        # Test class method attributes
        assert hasattr(TestClass.class_method, "__auth_required__")
        assert TestClass.class_method.__auth_required__ is False
        assert TestClass.class_method.__auth_level__ == "public"

        assert hasattr(TestClass.class_auth_method, "__auth_required__")
        assert TestClass.class_auth_method.__auth_required__ is True
        assert TestClass.class_auth_method.__auth_level__ == "user"

        assert hasattr(TestClass.class_admin_method, "__auth_required__")
        assert TestClass.class_admin_method.__auth_required__ is True
        assert TestClass.class_admin_method.__auth_level__ == "admin"

    def test_decorator_on_static_method(self):
        """Test decorators on static methods"""

        class TestClass:
            @staticmethod
            @PUBLIC
            def static_method():
                return "static public"

            @staticmethod
            @AUTH
            def static_auth_method():
                return "static auth"

            @staticmethod
            @ADMIN
            def static_admin_method():
                return "static admin"

        # Test static method attributes
        assert hasattr(TestClass.static_method, "__auth_required__")
        assert TestClass.static_method.__auth_required__ is False
        assert TestClass.static_method.__auth_level__ == "public"

        assert hasattr(TestClass.static_auth_method, "__auth_required__")
        assert TestClass.static_auth_method.__auth_required__ is True
        assert TestClass.static_auth_method.__auth_level__ == "user"

        assert hasattr(TestClass.static_admin_method, "__auth_required__")
        assert TestClass.static_admin_method.__auth_required__ is True
        assert TestClass.static_admin_method.__auth_level__ == "admin"


class TestDecoratorOnAsyncMethods:
    """Test decorators on async methods"""

    def test_decorator_on_async_instance_method(self):
        """Test decorators on async instance methods"""

        class TestClass:
            @PUBLIC
            async def async_instance_method(self):
                return "async instance public"

            @AUTH
            async def async_instance_auth_method(self):
                return "async instance auth"

            @ADMIN
            async def async_instance_admin_method(self):
                return "async instance admin"

        obj = TestClass()

        # Test async instance method attributes
        assert hasattr(obj.async_instance_method, "__auth_required__")
        assert obj.async_instance_method.__auth_required__ is False
        assert obj.async_instance_method.__auth_level__ == "public"

        assert hasattr(obj.async_instance_auth_method, "__auth_required__")
        assert obj.async_instance_auth_method.__auth_required__ is True
        assert obj.async_instance_auth_method.__auth_level__ == "user"

        assert hasattr(obj.async_instance_admin_method, "__auth_required__")
        assert obj.async_instance_admin_method.__auth_required__ is True
        assert obj.async_instance_admin_method.__auth_level__ == "admin"

    def test_decorator_on_async_class_method(self):
        """Test decorators on async class methods"""

        class TestClass:
            @classmethod
            @PUBLIC
            async def async_class_method(cls):
                return "async class public"

            @classmethod
            @AUTH
            async def async_class_auth_method(cls):
                return "async class auth"

            @classmethod
            @ADMIN
            async def async_class_admin_method(cls):
                return "async class admin"

        # Test async class method attributes
        assert hasattr(TestClass.async_class_method, "__auth_required__")
        assert TestClass.async_class_method.__auth_required__ is False
        assert TestClass.async_class_method.__auth_level__ == "public"

        assert hasattr(TestClass.async_class_auth_method, "__auth_required__")
        assert TestClass.async_class_auth_method.__auth_required__ is True
        assert TestClass.async_class_auth_method.__auth_level__ == "user"

        assert hasattr(TestClass.async_class_admin_method, "__auth_required__")
        assert TestClass.async_class_admin_method.__auth_required__ is True
        assert TestClass.async_class_admin_method.__auth_level__ == "admin"


class TestDecoratorInspection:
    """Test decorator inspection functions"""

    def test_requires_auth_function(self):
        """Test requires_auth inspection function"""

        @PUBLIC
        def public_func():
            pass

        @AUTH
        def auth_func():
            pass

        @ADMIN
        def admin_func():
            pass

        @OPTIONAL_AUTH
        def optional_func():
            pass

        def undecorated_func():
            pass

        # Test decorated functions
        assert requires_auth(public_func) is False
        assert requires_auth(auth_func) is True
        assert requires_auth(admin_func) is True
        assert requires_auth(optional_func) is False

        # Test undecorated function (should default to True for security)
        assert requires_auth(undecorated_func) is True

    def test_get_auth_level_function(self):
        """Test get_auth_level inspection function"""

        @PUBLIC
        def public_func():
            pass

        @AUTH
        def auth_func():
            pass

        @ADMIN
        def admin_func():
            pass

        @OPTIONAL_AUTH
        def optional_func():
            pass

        def undecorated_func():
            pass

        # Test decorated functions
        assert get_auth_level(public_func) == "public"
        assert get_auth_level(auth_func) == "user"
        assert get_auth_level(admin_func) == "admin"
        assert get_auth_level(optional_func) == "optional"

        # Test undecorated function (should default to 'user' for security)
        assert get_auth_level(undecorated_func) == "user"

    def test_is_admin_required_function(self):
        """Test is_admin_required inspection function"""

        @PUBLIC
        def public_func():
            pass

        @AUTH
        def auth_func():
            pass

        @ADMIN
        def admin_func():
            pass

        @OPTIONAL_AUTH
        def optional_func():
            pass

        def undecorated_func():
            pass

        # Test decorated functions
        assert is_admin_required(public_func) is False
        assert is_admin_required(auth_func) is False
        assert is_admin_required(admin_func) is True
        assert is_admin_required(optional_func) is False

        # Test undecorated function (should default to False)
        assert is_admin_required(undecorated_func) is False


class TestDecoratorFunctionality:
    """Test that decorated functions still work correctly"""

    def test_public_function_execution(self):
        """Test that @PUBLIC decorated functions execute correctly"""

        @PUBLIC
        def sync_func():
            return "sync result"

        @PUBLIC
        async def async_func():
            return "async result"

        # Test sync function
        result = sync_func()
        assert result == "sync result"

        # Test async function
        async def run_async():
            result = await async_func()
            assert result == "async result"

        asyncio.run(run_async())

    def test_auth_function_execution(self):
        """Test that @AUTH decorated functions execute correctly"""

        @AUTH
        def sync_func():
            return "sync auth result"

        @AUTH
        async def async_func():
            return "async auth result"

        # Test sync function
        result = sync_func()
        assert result == "sync auth result"

        # Test async function
        async def run_async():
            result = await async_func()
            assert result == "async auth result"

        asyncio.run(run_async())

    def test_admin_function_execution(self):
        """Test that @ADMIN decorated functions execute correctly"""

        @ADMIN
        def sync_func():
            return "sync admin result"

        @ADMIN
        async def async_func():
            return "async admin result"

        # Test sync function
        result = sync_func()
        assert result == "sync admin result"

        # Test async function
        async def run_async():
            result = await async_func()
            assert result == "async admin result"

        asyncio.run(run_async())

    def test_optional_auth_function_execution(self):
        """Test that @OPTIONAL_AUTH decorated functions execute correctly"""

        @OPTIONAL_AUTH
        def sync_func():
            return "sync optional result"

        @OPTIONAL_AUTH
        async def async_func():
            return "async optional result"

        # Test sync function
        result = sync_func()
        assert result == "sync optional result"

        # Test async function
        async def run_async():
            result = await async_func()
            assert result == "async optional result"

        asyncio.run(run_async())


class TestDecoratorWithArguments:
    """Test decorators with functions that have arguments"""

    def test_decorator_with_positional_args(self):
        """Test decorators on functions with positional arguments"""

        @PUBLIC
        def func_with_args(a, b, c):
            return a + b + c

        @AUTH
        async def async_func_with_args(x, y):
            return x * y

        # Test sync function with args
        result = func_with_args(1, 2, 3)
        assert result == 6
        assert hasattr(func_with_args, "__auth_required__")
        assert func_with_args.__auth_required__ is False

        # Test async function with args
        async def run_async():
            result = await async_func_with_args(4, 5)
            assert result == 20
            assert hasattr(async_func_with_args, "__auth_required__")
            assert async_func_with_args.__auth_required__ is True

        asyncio.run(run_async())

    def test_decorator_with_kwargs(self):
        """Test decorators on functions with keyword arguments"""

        @ADMIN
        def func_with_kwargs(name="default", age=0):
            return f"{name} is {age} years old"

        @OPTIONAL_AUTH
        async def async_func_with_kwargs(message="hello", count=1):
            return f"{message} {count}"

        # Test sync function with kwargs
        result = func_with_kwargs(name="Alice", age=25)
        assert result == "Alice is 25 years old"
        assert hasattr(func_with_kwargs, "__auth_required__")
        assert func_with_kwargs.__auth_required__ is True
        assert func_with_kwargs.__auth_level__ == "admin"

        # Test async function with kwargs
        async def run_async():
            result = await async_func_with_kwargs(message="hi", count=3)
            assert result == "hi 3"
            assert hasattr(async_func_with_kwargs, "__auth_required__")
            assert async_func_with_kwargs.__auth_required__ is False
            assert async_func_with_kwargs.__auth_level__ == "optional"

        asyncio.run(run_async())


class TestDecoratorChaining:
    """Test decorator chaining behavior"""

    def test_decorator_with_other_decorators(self):
        """Test decorators with other common decorators"""

        @PUBLIC
        @staticmethod
        def static_public_func():
            return "static public"

        @AUTH
        @classmethod
        def class_auth_func(cls):
            return "class auth"

        # Test static method
        assert hasattr(static_public_func, "__auth_required__")
        assert static_public_func.__auth_required__ is False
        assert static_public_func.__auth_level__ == "public"

        # Test class method
        assert hasattr(class_auth_func, "__auth_required__")
        assert class_auth_func.__auth_required__ is True
        assert class_auth_func.__auth_level__ == "user"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_decorator_on_lambda(self):
        """Test decorators on lambda functions"""

        # Create lambda functions first, then apply decorators
        lambda_func = lambda: "lambda public"  # noqa: E731
        lambda_auth_func = lambda x: x * 2  # noqa: E731

        # Apply decorators
        lambda_func = PUBLIC(lambda_func)
        lambda_auth_func = AUTH(lambda_auth_func)

        # Test lambda functions
        assert hasattr(lambda_func, "__auth_required__")
        assert lambda_func.__auth_required__ is False
        assert lambda_func.__auth_level__ == "public"

        assert hasattr(lambda_auth_func, "__auth_required__")
        assert lambda_auth_func.__auth_required__ is True
        assert lambda_auth_func.__auth_level__ == "user"

        # Test execution
        assert lambda_func() == "lambda public"
        assert lambda_auth_func(5) == 10

    def test_decorator_on_method_without_self(self):
        """Test decorators on methods that don't follow standard patterns"""

        class TestClass:
            @PUBLIC
            def method_without_self():
                return "no self"

        # Test method without self
        assert hasattr(TestClass.method_without_self, "__auth_required__")
        assert TestClass.method_without_self.__auth_required__ is False
        assert TestClass.method_without_self.__auth_level__ == "public"

        # Test execution
        result = TestClass.method_without_self()
        assert result == "no self"


class TestTaggingUtilities:
    """Test the generic tagging utilities"""

    def test_tag_decorator_basic(self):
        """Test basic tag decorator functionality"""

        @tag(test_tag="test_value", another_tag=42)
        def tagged_func():
            return "tagged"

        # Test that tags are applied
        assert hasattr(tagged_func, "__tagged__")
        assert tagged_func.__tagged__ is True
        assert hasattr(tagged_func, "__tags__")
        assert "test_tag" in tagged_func.__tags__
        assert "another_tag" in tagged_func.__tags__

        # Test tag values
        assert tagged_func.test_tag == "test_value"
        assert tagged_func.another_tag == 42

        # Test function still works
        result = tagged_func()
        assert result == "tagged"

    def test_tag_decorator_conflict_detection(self):
        """Test that tag decorator detects conflicts"""

        # Test that applying conflicting tag raises exception
        with pytest.raises(DuplicateTagError):

            @tag(conflict_tag="first_value")
            @tag(conflict_tag="second_value")
            def conflict_func2():
                return "conflict2"

    def test_get_tags_function(self):
        """Test get_tags utility function"""

        @tag(tag1="value1", tag2=123, tag3=True)
        def multi_tagged_func():
            return "multi"

        tags = get_tags(multi_tagged_func)

        assert tags == {"tag1": "value1", "tag2": 123, "tag3": True}

    def test_get_tag_function(self):
        """Test get_tag utility function"""

        @tag(single_tag="single_value")
        def single_tagged_func():
            return "single"

        # Test getting existing tag
        assert get_tag(single_tagged_func, "single_tag") == "single_value"

        # Test getting non-existent tag with default
        assert get_tag(single_tagged_func, "non_existent", "default") == "default"

        # Test getting non-existent tag without default
        assert get_tag(single_tagged_func, "non_existent") is None

    def test_auth_tag_decorator(self):
        """Test auth_tag decorator functionality"""

        @auth_tag("public")
        def public_func():
            return "public"

        @auth_tag("user")
        def user_func():
            return "user"

        @auth_tag("admin")
        def admin_func():
            return "admin"

        @auth_tag("optional")
        def optional_func():
            return "optional"

        # Test public function
        assert get_tag(public_func, "__auth_level__") == "public"
        assert get_tag(public_func, "__auth_required__") is False

        # Test user function
        assert get_tag(user_func, "__auth_level__") == "user"
        assert get_tag(user_func, "__auth_required__") is True

        # Test admin function
        assert get_tag(admin_func, "__auth_level__") == "admin"
        assert get_tag(admin_func, "__auth_required__") is True

        # Test optional function
        assert get_tag(optional_func, "__auth_level__") == "optional"
        assert get_tag(optional_func, "__auth_required__") is False

        # Test functions still work
        assert public_func() == "public"
        assert user_func() == "user"
        assert admin_func() == "admin"
        assert optional_func() == "optional"

    def test_auth_tag_conflict_detection(self):
        """Test that auth_tag detects conflicts"""

        # Test that applying conflicting auth tag raises exception
        with pytest.raises(DuplicateTagError):

            @auth_tag("public")
            @auth_tag("user")
            def conflict_func2():
                return "conflict2"

    def test_tag_with_async_functions(self):
        """Test tag decorator with async functions"""

        @tag(async_tag="async_value")
        async def async_tagged_func():
            return "async"

        # Test async function tags
        assert hasattr(async_tagged_func, "__tagged__")
        assert async_tagged_func.__tagged__ is True
        assert get_tag(async_tagged_func, "async_tag") == "async_value"

        # Test async function still works
        async def run_async():
            result = await async_tagged_func()
            assert result == "async"

        asyncio.run(run_async())

    def test_tag_with_class_methods(self):
        """Test tag decorator with class methods"""

        class TestClass:
            @tag(method_tag="method_value")
            def instance_method(self):
                return "instance"

            @classmethod
            @tag(class_tag="class_value")
            def class_method(cls):
                return "class"

            @staticmethod
            @tag(static_tag="static_value")
            def static_method():
                return "static"

        obj = TestClass()

        # Test instance method
        assert get_tag(obj.instance_method, "method_tag") == "method_value"
        assert obj.instance_method() == "instance"

        # Test class method
        assert get_tag(TestClass.class_method, "class_tag") == "class_value"
        assert TestClass.class_method() == "class"

        # Test static method
        assert get_tag(TestClass.static_method, "static_tag") == "static_value"
        assert TestClass.static_method() == "static"

    def test_tag_with_lambda_functions(self):
        """Test tag decorator with lambda functions"""

        # Create lambda function first, then apply tag
        lambda_func = lambda: "lambda"  # noqa: E731
        lambda_func = tag(lambda_tag="lambda_value")(lambda_func)

        # Test lambda function tags
        assert hasattr(lambda_func, "__tagged__")
        assert lambda_func.__tagged__ is True
        assert get_tag(lambda_func, "lambda_tag") == "lambda_value"

        # Test lambda function still works
        assert lambda_func() == "lambda"

    def test_tag_with_arguments(self):
        """Test tag decorator with functions that have arguments"""

        @tag(args_tag="args_value")
        def func_with_args(a, b, c):
            return a + b + c

        @tag(kwargs_tag="kwargs_value")
        async def async_func_with_kwargs(x=1, y=2):
            return x * y

        # Test sync function with args
        assert get_tag(func_with_args, "args_tag") == "args_value"
        result = func_with_args(1, 2, 3)
        assert result == 6

        # Test async function with kwargs
        assert get_tag(async_func_with_kwargs, "kwargs_tag") == "kwargs_value"

        async def run_async():
            result = await async_func_with_kwargs(x=4, y=5)
            assert result == 20

        asyncio.run(run_async())

    def test_tag_inspection_functions(self):
        """Test tag inspection with helper functions"""

        @tag(inspect_tag1="value1", inspect_tag2=42)
        def inspect_func():
            return "inspect"

        # Test get_tags
        tags = get_tags(inspect_func)
        assert tags == {"inspect_tag1": "value1", "inspect_tag2": 42}

        # Test get_tag with existing tag
        assert get_tag(inspect_func, "inspect_tag1") == "value1"
        assert get_tag(inspect_func, "inspect_tag2") == 42

        # Test get_tag with non-existent tag
        assert get_tag(inspect_func, "non_existent", "default") == "default"
        assert get_tag(inspect_func, "non_existent") is None

    def test_auth_tag_integration_with_existing_functions(self):
        """Test that auth_tag integrates with existing inspection functions"""

        @auth_tag("public")
        def public_func():
            return "public"

        @auth_tag("admin")
        def admin_func():
            return "admin"

        # Test that existing inspection functions work with auth_tag
        assert requires_auth(public_func) is False
        assert get_auth_level(public_func) == "public"
        assert is_admin_required(public_func) is False

        assert requires_auth(admin_func) is True
        assert get_auth_level(admin_func) == "admin"
        assert is_admin_required(admin_func) is True

    def test_tag_with_multiple_non_conflicting_tags(self):
        """Test applying multiple non-conflicting tags"""

        @tag(tag1="value1")
        @tag(tag2="value2")
        def multi_tag_func():
            return "multi"

        # Test that both tags are present
        assert get_tag(multi_tag_func, "tag1") == "value1"
        assert get_tag(multi_tag_func, "tag2") == "value2"

        # Test get_tags returns both
        tags = get_tags(multi_tag_func)
        assert tags == {"tag1": "value1", "tag2": "value2"}

        # Test function still works
        assert multi_tag_func() == "multi"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

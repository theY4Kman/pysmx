import pytest


@pytest.mark.parametrize('value', [True, False])
def test_bool_literal_return(value, compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        public bool:Test() {
            return %s;
        }
    ''' % ('true' if value else 'false'))
    rval = plugin.runtime.call_function_by_name('Test')
    assert rval is value


@pytest.mark.parametrize('integer', [
    0,
    1,
    2147483647,
    -2147483648,
])
def test_integer_literal_return(integer, compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        public Test() {
            return %d;
        }
    ''' % integer)
    assert plugin.runtime.call_function_by_name('Test') == integer


def test_float_literal_return(compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        public Float:Test() {
            return 12.0;
        }
    ''')
    rval = plugin.runtime.call_function_by_name('Test')
    assert rval == 12.0
    assert isinstance(rval, float)


def test_string_return(compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        String:Test() {
            new String:s[] = "hiss";
            return s;
        }
        public DontOptimizeOutTest() {
            Test();
        }
    ''')
    rval = plugin.runtime.call_function_by_name('Test')
    assert rval == 'hiss'

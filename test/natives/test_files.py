from ctypes import c_float, c_int32

import pytest


def test_read_line(compile_plugin):
    # language=SourcePawn
    plugin = compile_plugin('''
        new File:g_file;
        String:ReadLine() {
            new String:buffer[256];

            if (!g_file) {
                BuildPath(Path_SM, buffer, sizeof(buffer), "text_file.txt");
                g_file = OpenFile(buffer, "rt");

                if (!g_file) {
                    PrintToServer("Failed to open file!");
                    return buffer;
                }
            }

            g_file.ReadLine(buffer, sizeof(buffer));
            return buffer;
        }
        public DontOptimizeOutReadLine() {
            ReadLine();
        }
    ''')

    read_line = plugin.runtime.get_function_by_name('ReadLine')

    lines = []
    while True:
        line = read_line()
        if not line:
            break
        lines.append(line)

    expected = [
        'line 1\n',
        'line 2\n',
        'line 3\n',
    ]
    actual = lines
    assert expected == actual


@pytest.mark.parametrize(('ctype', 'sm_type', 'printf', 'elements'), [
    pytest.param(c_int32, 'int', '%d', [0x0f0f0f0f, 0x00f0f0f0, 0x01111111], id='int'),
    pytest.param(c_float, 'float', '%f', [3.14, 2.71, 1.41], id='float'),
])
def test_read(compile_plugin, tmp_path, ctype, sm_type, printf, elements):
    total_value = sum(element for element in elements)
    buf = b''.join(bytes(ctype(element)) for element in elements)

    binary_file = tmp_path / 'binary_file.bin'
    binary_file.write_bytes(buf)

    # language=SourcePawn
    plugin = compile_plugin('''
        new File:g_file;
        %(sm_type)s Read() {
            %(sm_type)s buffer[%(num_elements)d];

            if (!g_file) {
                g_file = OpenFile("%(file)s", "rb");

                if (!g_file) {
                    PrintToServer("Failed to open file!");
                    return -1;
                }
            }

            g_file.Read(buffer, %(num_elements)d, 4);
            g_file.Close();

            %(sm_type)s total = 0;
            for (int i = 0; i < sizeof(buffer); i++) {
                PrintToServer("buffer[%%d] = %(printf)s", i, buffer[i]);
                total += buffer[i];
            }

            return total;
        }
        public DontOptimizeOutRead() {
            Read();
        }
    ''' % {
        'num_elements': len(elements),
        # Escape backslashes in the path for testing under Windows
        'file': str(binary_file).replace('\\', '\\\\'),
        'sm_type': sm_type,
        'printf': printf,
    })

    expected = total_value
    actual = plugin.runtime.call_function_by_name('Read')
    assert expected == pytest.approx(actual)

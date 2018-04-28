# Defines all the SourcePawn opcodes and provides helpers
from __future__ import division

__all__ = ['sp_opcodes_list', 'opcodes']

# Legend for Statuses:
#
# DONE       -> code generation is done
# !GEN       -> code generation is deliberate skipped because:
#                 (default): compiler does not generate
#                DEPRECATED: this feature no longer exists/supported
#               UNSUPPORTED: this opcode is not supported
#                      TODO: done in case needed
# VERIFIED   -> code generation is checked as run-time working.  prefixes:
#                ! errors are not checked yet.
#                - non-inline errors are not checked yet.
#                ~ assumed checked because of related variation, but not actually checked

sp_opcodes_list = [
    'invalid',
    'load_pri',
    'load_alt',
    'load_s_pri',
    'load_s_alt',
    'lref_pri',
    'lref_alt',
    'lref_s_pri',
    'lref_s_alt',
    'load_i',
    'lodb_i',
    'const_pri',
    'const_alt',
    'addr_pri',
    'addr_alt',
    'stor_pri',
    'stor_alt',
    'stor_s_pri',
    'stor_s_alt',
    'sref_pri',
    'sref_alt',
    'sref_s_pri',
    'sref_s_alt',
    'stor_i',
    'strb_i',
    'lidx',
    'lidx_b',
    'idxaddr',
    'idxaddr_b',
    'align_pri',    # !GEN :TODO: - only used for pack access, drop support in compiler first
    'align_alt',    # !GEN :TODO: - only used for pack access, drop support in compiler first
    'lctrl',        # !GEN
    'sctrl',        # !GEN
    'move_pri',
    'move_alt',
    'xchg',
    'push_pri',
    'push_alt',
    'push_r',       # !GEN DEPRECATED
    'push_c',
    'push',
    'push_s',
    'pop_pri',
    'pop_alt',
    'stack',
    'heap',
    'proc',
    'ret',          # !GEN
    'retn',
    'call',
    'call_pri',     # !GEN
    'jump',
    'jrel',         # !GEN
    'jzer',
    'jnz',
    'jeq',
    'jneq',
    'jless',        # !GEN
    'jleq',         # !GEN
    'jgrtr',        # !GEN
    'jgeq',         # !GEN
    'jsless',
    'jsleq',
    'jsgrtr',
    'jsgeq',
    'shl',
    'shr',
    'sshr',
    'shl_c_pri',
    'shl_c_alt',
    'shr_c_pri',
    'shr_c_alt',
    'smul',
    'sdiv',
    'sdiv_alt',
    'umul',         # !GEN
    'udiv',         # !GEN
    'udiv_alt',     # !GEN
    'add',
    'sub',
    'sub_alt',
    'dand',
    'dor',
    'xor',
    'dnot',
    'neg',
    'invert',
    'add_c',
    'smul_c',
    'zero_pri',
    'zero_alt',
    'zero',
    'zero_s',
    'sign_pri',
    'sign_alt',
    'eq',
    'neq',
    'less',         # !GEN
    'leq',          # !GEN
    'grtr',         # !GEN
    'geq',          # !GEN
    'sless',
    'sleq',
    'sgrtr',
    'sgeq',
    'eq_c_pri',
    'eq_c_alt',
    'inc_pri',
    'inc_alt',
    'inc',
    'inc_s',
    'inc_i',
    'dec_pri',
    'dec_alt',
    'dec',
    'dec_s',
    'dec_i',
    'movs',
    'cmps',         # !GEN
    'fill',
    'halt',
    'bounds',
    'sysreq_pri',   # !GEN
    'sysreq_c',
    'file',         # !GEN DEPRECATED
    'line',         # !GEN DEPRECATED
    'symbol',       # !GEN DEPRECATED
    'srange',       # !GEN DEPRECATED
    'jump_pri',     # !GEN
    'switch_',
    'casetbl',
    'swap_pri',
    'swap_alt',
    'push_adr',
    'nop',
    'sysreq_n',
    'symtag',       # !GEN DEPRECATED
    'dbreak',
    'push2_c',
    'push2',
    'push2_s',
    'push2_adr',
    'push3_c',
    'push3',
    'push3_s',
    'push3_adr',
    'push4_c',
    'push4',
    'push4_s',
    'push4_adr',
    'push5_c',
    'push5',
    'push5_s',
    'push5_adr',
    'load_both',
    'load_s_both',
    'const_',
    'const_s',
    'sysreq_d',     # !GEN UNSUPPORT
    'sysreq_nd',    # !GEN UNSUPPORT
    'tracker_push_c',
    'tracker_pop_setheap',
    'genarray',
    'genarray_z',
    'stradjust_pri',
    'stackadjust',
    'endproc',
    'fabs',
    'float_',
    'floatadd',
    'floatsub',
    'floatmul',
    'floatdiv',
    'rnd_to_nearest',
    'rnd_to_floor',
    'rnd_to_ceil',
    'rnd_to_zero',
    'floatcmp'
]

"""
  'invalid',
  'load_pri',
  'load_alt',
  'load_s_pri',
  'load_s_alt',
  'lref_pri',
  'lref_alt',
  'lref_s_pri',
  'lref_s_alt',
  'load_i',
  'lodb_i',
  'const_pri',
  'const_alt',
  'addr_pri',
  'addr_alt',
  'stor_pri',
  'stor_alt',
  'stor_s_pri',
  'stor_s_alt',
  'sref_pri',
  'sref_alt',
  'sref_s_pri',
  'sref_s_alt',
  'stor_i',
  'strb_i',
  'lidx',
  'lidx_b',
  'idxaddr',
  'idxaddr_b',
  'align_pri',
  'align_alt',
  'lctrl',
  'sctrl',
  'move_pri',
  'move_alt',
  'xchg',
  'push_pri',
  'push_alt',
  'push_r',
  'push_c',
  'push',
  'push_s',
  'pop_pri',
  'pop_alt',
  'stack',
  'heap',
  'proc',
  'ret',
  'retn',
  'call',
  'call_pri',
  'jump',
  'jrel',
  'jzer',
  'jnz',
  'jeq',
  'jneq',
  'jless',
  'jleq',
  'jgrtr',
  'jgeq',
  'jsless',
  'jsleq',
  'jsgrtr',
  'jsgeq',
  'shl',
  'shr',
  'sshr',
  'shl_c_pri',
  'shl_c_alt',
  'shr_c_pri',
  'shr_c_alt',
  'smul',
  'sdiv',
  'sdiv_alt',
  'umul',
  'udiv',
  'udiv_alt',
  'add',
  'sub',
  'sub_alt',
  'and',
  'or',
  'xor',
  'not',
  'neg',
  'invert',
  'add_c',
  'smul_c',
  'zero_pri',
  'zero_alt',
  'zero',
  'zero_s',
  'sign_pri',
  'sign_alt',
  'eq',
  'neq',
  'less',
  'leq',
  'grtr',
  'geq',
  'sless',
  'sleq',
  'sgrtr',
  'sgeq',
  'eq_c_pri',
  'eq_c_alt',
  'inc_pri',
  'inc_alt',
  'inc',
  'inc_s',
  'inc_i',
  'dec_pri',
  'dec_alt',
  'dec',
  'dec_s',
  'dec_i',
  'movs',
  'cmps',
  'fill',
  'halt',
  'bounds',
  'sysreq_pri',
  'sysreq_c',
  'file',    # obsolete
  'line',    # obsolete
  'symbol',  # obsolete
  'srange',  # obsolete
  'jump_pri',
  'switch',
  'casetbl',
  'swap_pri',
  'swap_alt',
  'push_adr',
  'nop',
  'sysreq_n',
  'symtag',  # obsolete
  'break',
  'push2_c',
  'push2',
  'push2_s',
  'push2_adr',
  'push3_c',
  'push3',
  'push3_s',
  'push3_adr',
  'push4_c',
  'push4',
  'push4_s',
  'push4_adr',
  'push5_c',
  'push5',
  'push5_s',
  'push5_adr',
  'load_both',
  'load_s_both',
  'const',
  'const_s',

  'sysreq_d',
  'sysreq_nd',

  'heap_i',
  'push_h_c',
  'genarray',
"""

class SourcePawnOpcodes(object):
    def __init__(self):
        self._op_to_name = {}
        self._name_to_op = {}

        for opcode,name in enumerate(sp_opcodes_list):
            self._op_to_name[opcode] = name
            self._name_to_op[name] = opcode

    def __getitem__(self, item):
        return self._op_to_name[item]

    def get(self, k, d=None):
        return self._op_to_name.get(k, d)

    def __getattr__(self, item):
        try:
            return self._name_to_op[item]
        except KeyError:
            raise AttributeError('There is no "%s" opcode' % item)

opcodes = SourcePawnOpcodes()

cdef extern from "vendor/include/sp_vm_api.h":
    cdef cppclass ISourcePawnEngine2:
        const char *GetVersionString()

    cdef cppclass ISourcePawnEnvironment:
        ISourcePawnEngine2 *APIv2()

    cdef cppclass ISourcePawnFactory:
        ISourcePawnEnvironment *NewEnvironment()

cdef extern ISourcePawnFactory *GetSourcePawnFactory(int apiVersion)

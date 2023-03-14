from __future__ import annotations

from enum import IntEnum
from typing import Callable

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.handles import SourceModHandle
from smx.sourcemod.natives.base import (
    MethodMap,
    Pointer,
    SourceModNativesMixin,
    WritableString,
    native,
)


SQLTxnSuccess = Callable
SQLTxnFailure = Callable
SQLConnectCallback = Callable
SQLQueryCallback = Callable
SQLTCallback = Callable


class DBResult(IntEnum):
    DBVal_Error = 0
    DBVal_TypeMismatch = 1
    DBVal_Null = 2
    DBVal_Data = 3


class DBBindType(IntEnum):
    DBBind_Int = 0
    DBBind_Float = 1
    DBBind_String = 2


class DBPriority(IntEnum):
    DBPrio_High = 0
    DBPrio_Normal = 1
    DBPrio_Low = 2


class DBDriver:
    pass


class DBResultSet:
    pass


class Transaction:
    pass


class DBStatement:
    pass


class Database:
    pass


class DBDriverMethodMap(MethodMap):
    @native
    def Find(self, name: str) -> SourceModHandle[DBDriver]:
        raise SourcePawnUnboundNativeError

    @native
    def GetIdentifier(self, this: SourceModHandle[DBDriver], ident: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetProduct(self, this: SourceModHandle[DBDriver], product: WritableString) -> None:
        raise SourcePawnUnboundNativeError


class DBResultSetMethodMap(MethodMap):
    @native
    def FetchMoreResults(self, this: SourceModHandle[DBResultSet]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FieldNumToName(self, this: SourceModHandle[DBResultSet], field: int, name: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def FieldNameToNum(self, this: SourceModHandle[DBResultSet], name: str, field: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FetchRow(self, this: SourceModHandle[DBResultSet]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Rewind(self, this: SourceModHandle[DBResultSet]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FetchString(self, this: SourceModHandle[DBResultSet], field: int, buffer: WritableString, result: Pointer[DBResult]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def FetchFloat(self, this: SourceModHandle[DBResultSet], field: int, result: Pointer[DBResult]) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def FetchInt(self, this: SourceModHandle[DBResultSet], field: int, result: Pointer[DBResult]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsFieldNull(self, this: SourceModHandle[DBResultSet], field: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def FetchSize(self, this: SourceModHandle[DBResultSet], field: int) -> int:
        raise SourcePawnUnboundNativeError


class TransactionMethodMap(MethodMap):
    @native
    def AddQuery(self, this: SourceModHandle[Transaction], query: str, data: int) -> int:
        raise SourcePawnUnboundNativeError


class DBStatementMethodMap(MethodMap):
    @native
    def BindInt(self, this: SourceModHandle[DBStatement], param: int, number: int, signed: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BindFloat(self, this: SourceModHandle[DBStatement], param: int, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def BindString(self, this: SourceModHandle[DBStatement], param: int, value: str, copy: bool) -> None:
        raise SourcePawnUnboundNativeError


class DatabaseMethodMap(MethodMap):
    @native
    def Connect(self, callback: SQLConnectCallback, name: str, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetCharset(self, this: SourceModHandle[Database], charset: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Escape(self, this: SourceModHandle[Database], string: str, buffer: WritableString, written: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Format(self, this: SourceModHandle[Database], buffer: WritableString, format_: str, *args) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def IsSameConnection(self, this: SourceModHandle[Database], other: SourceModHandle[Database]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def Query(self, this: SourceModHandle[Database], callback: SQLQueryCallback, query: str, data: int, prio: DBPriority) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def Execute(self, this: SourceModHandle[Database], txn: SourceModHandle[Transaction], on_success: SQLTxnSuccess, on_error: SQLTxnFailure, data: int, priority: DBPriority) -> None:
        raise SourcePawnUnboundNativeError


class DbiNatives(SourceModNativesMixin):
    DBDriver = DBDriverMethodMap()
    DBResultSet = DBResultSetMethodMap()
    Transaction = TransactionMethodMap()
    DBStatement = DBStatementMethodMap()
    Database = DatabaseMethodMap()

    @native
    def SQL_Connect(self, confname: str, persistent: bool, error: WritableString) -> SourceModHandle[Database]:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_ConnectCustom(self, keyvalues: SourceModHandle, error: WritableString, persistent: bool) -> SourceModHandle[Database]:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_ConnectEx(self, driver: SourceModHandle, host: str, user: str, pass_: str, database: str, error: WritableString, persistent: bool, port: int, max_timeout: int) -> SourceModHandle:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_CheckConfig(self, name: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_GetDriver(self, name: str) -> SourceModHandle[DBDriver]:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_ReadDriver(self, database: SourceModHandle, ident: str, ident_length: int) -> SourceModHandle[DBDriver]:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_GetDriverIdent(self, driver: SourceModHandle, ident: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_GetDriverProduct(self, driver: SourceModHandle, product: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_SetCharset(self, database: SourceModHandle, charset: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_GetAffectedRows(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_GetInsertId(self, hndl: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_GetError(self, hndl: SourceModHandle, error: WritableString) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_EscapeString(self, database: SourceModHandle, string: str, buffer: WritableString, written: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FormatQuery(self, database: SourceModHandle, buffer: WritableString, format_: str, *args) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FastQuery(self, database: SourceModHandle, query: str, len_: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_Query(self, database: SourceModHandle, query: str, len_: int) -> SourceModHandle[DBResultSet]:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_PrepareQuery(self, database: SourceModHandle, query: str, error: WritableString) -> SourceModHandle[DBStatement]:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FetchMoreResults(self, query: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_HasResultSet(self, query: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_GetRowCount(self, query: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_GetFieldCount(self, query: SourceModHandle) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FieldNumToName(self, query: SourceModHandle, field: int, name: WritableString) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FieldNameToNum(self, query: SourceModHandle, name: str, field: Pointer[int]) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FetchRow(self, query: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_MoreRows(self, query: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_Rewind(self, query: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FetchString(self, query: SourceModHandle, field: int, buffer: WritableString, result: Pointer[DBResult]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FetchFloat(self, query: SourceModHandle, field: int, result: Pointer[DBResult]) -> float:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FetchInt(self, query: SourceModHandle, field: int, result: Pointer[DBResult]) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_IsFieldNull(self, query: SourceModHandle, field: int) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_FetchSize(self, query: SourceModHandle, field: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_BindParamInt(self, statement: SourceModHandle, param: int, number: int, signed: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_BindParamFloat(self, statement: SourceModHandle, param: int, value: float) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_BindParamString(self, statement: SourceModHandle, param: int, value: str, copy: bool) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_Execute(self, statement: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_LockDatabase(self, database: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_UnlockDatabase(self, database: SourceModHandle) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_IsSameConnection(self, hndl1: SourceModHandle, hndl2: SourceModHandle) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_TConnect(self, callback: SQLTCallback, name: str, data: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_TQuery(self, database: SourceModHandle, callback: SQLTCallback, query: str, data: int, prio: DBPriority) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_CreateTransaction(self) -> SourceModHandle[Transaction]:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_AddQuery(self, txn: SourceModHandle[Transaction], query: str, data: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def SQL_ExecuteTransaction(self, db: SourceModHandle, txn: SourceModHandle[Transaction], on_success: SQLTxnSuccess, on_error: SQLTxnFailure, data: int, priority: DBPriority) -> None:
        raise SourcePawnUnboundNativeError

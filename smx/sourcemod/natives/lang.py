from __future__ import annotations

from smx.exceptions import SourcePawnUnboundNativeError
from smx.sourcemod.natives.base import SourceModNativesMixin, native


class LangNatives(SourceModNativesMixin):
    @native
    def LoadTranslations(self, file: str) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetGlobalTransTarget(self, client: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetClientLanguage(self, client: int) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetServerLanguage(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetLanguageCount(self) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetLanguageInfo(self, language: int, code: str, code_len: int, name: str, name_len: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def SetClientLanguage(self, client: int, language: int) -> None:
        raise SourcePawnUnboundNativeError

    @native
    def GetLanguageByCode(self, code: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def GetLanguageByName(self, name: str) -> int:
        raise SourcePawnUnboundNativeError

    @native
    def TranslationPhraseExists(self, phrase: str) -> bool:
        raise SourcePawnUnboundNativeError

    @native
    def IsTranslatedForLanguage(self, phrase: str, language: int) -> bool:
        raise SourcePawnUnboundNativeError

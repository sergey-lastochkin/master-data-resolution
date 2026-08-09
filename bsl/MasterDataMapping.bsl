// Illustrative configuration-mapped adapter, not a standalone 1C module.
// НайтиCanonicalID and ЗаписатьCanonicalMapping must be mapped to target storage.
Функция ПрименитьСопоставление(SourceRef, CanonicalID) Экспорт
    Текущее = НайтиCanonicalID(SourceRef);
    Если ЗначениеЗаполнено(Текущее) Тогда
        Если Текущее = CanonicalID Тогда Возврат Текущее; КонецЕсли;
        ВызватьИсключение "Mapping conflict";
    КонецЕсли;
    ЗаписатьCanonicalMapping(SourceRef, CanonicalID);
    Возврат CanonicalID;
КонецФункции

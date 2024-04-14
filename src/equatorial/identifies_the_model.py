try:
    import unzip_requirements
except ImportError:
    pass

try:
    import logging
    import fitz
    from typing import Dict, Any
    from src.functions import treatTextField, treatDateField
except Exception as e:
    print(f"Error importing libraries {e}")

logger = logging.getLogger(__name__)


class IdentifiesTheModel(object):
    def __init__(self, dataDoc, dataToSave: Dict[str, Any]) -> None:
        self.__dataDoc = dataDoc
        self.__dataToSave = dataToSave

    async def processSync(self) -> str:
        isFileEquatorial = False
        isFileEnel = False
        qtdLinesNotImage = 0
        qtdLines = 0
        existDate = False
        try:
            with fitz.open(stream=self.__dataDoc, filetype='pdf') as doc:
                for numberPage, page in enumerate(doc):
                    dataPage = page.get_text("blocks", sort=True)
                    dataPage.sort(key=lambda x: x[-2])
                    for numberLine, dataLine in enumerate(dataPage):
                        # if numberPage == 10:
                        # print(dataLine)
                        qtdLines += 1
                        try:
                            dataValue = treatTextField(dataLine[4])

                            if dataValue.find('EQUATORIAL') >= 0:
                                isFileEquatorial = True

                            if dataValue.find('ENEL DISTRIBUICAO') >= 0:
                                isFileEnel = True

                            if dataValue.find('<IMAGE:') < 0:
                                qtdLinesNotImage += 1

                            dataValueSplitSpace = dataValue.split(' ')
                            if existDate is False:
                                for value in dataValueSplitSpace:
                                    valueAsDate1 = treatDateField(value)
                                    if valueAsDate1 is not None:
                                        existDate = True
                        except Exception:
                            pass

        except Exception as e:
            logger.exception(e)

        if (qtdLinesNotImage == 0 or existDate is False) and qtdLines > 0:
            self.__dataToSave['typeLog'] = 'warning'
            self.__dataToSave['messageLog'] = 'WARNING_OCR'
            self.__dataToSave[
                'messageLogToShowUser'] = 'Não foi identificado texto no documento.'
            return 'ocr'

        if isFileEquatorial is True:
            return 'model01'
        if isFileEnel is True:
            return 'model02'

        return ''

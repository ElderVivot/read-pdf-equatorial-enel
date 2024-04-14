try:
    import unzip_requirements
except ImportError:
    pass

try:
    import unicodedata
    import logging
    import re
    import datetime
    from typing import Any, List
except Exception as e:
    print("Error importing libraries", e)

logger = logging.getLogger(__name__)


def minimalizeSpaces(text: str):
    _result = text
    while ("  " in _result):
        _result = _result.replace("  ", " ")
    _result = _result.strip()
    return _result


def removeCharSpecials(text: str):
    nfkd = unicodedata.normalize('NFKD', text).encode(
        'ASCII', 'ignore').decode('ASCII')
    textFormated = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub('[^a-zA-Z0-9.!+:><=[)|?$(/*,\-_\n\r \\\]', '', textFormated)


def searchPositionFieldForName(header, nameField=''):
    nameField = treatTextField(nameField)
    try:
        return header[nameField]
    except Exception:
        return None


def analyzeIfFieldHasPositionInFileEnd(data, positionInFile, positionInFileEnd):
    try:
        if positionInFileEnd <= 0:
            return data[positionInFile]
        else:
            return ''.join(data[positionInFile:positionInFileEnd])
    except Exception:
        return ""


def returnDataInDictOrArray(data: Any, arrayStructureDataReturn: List[Any], valueDefault='') -> Any:
    """
    :data: vector, matrix ou dict with data -> example: {"name": "Obama", "adress": {"zipCode": "1234567"}}
    :arrayStructureDataReturn: array in order with position of vector/matriz or name property of dict to \
    return -> example: ['adress', 'zipCode'] -> return is '1234567'
    """
    try:
        dataAccumulated = ''
        for i in range(len(arrayStructureDataReturn)):
            if i == 0:
                dataAccumulated = data[arrayStructureDataReturn[i]]
            else:
                dataAccumulated = dataAccumulated[arrayStructureDataReturn[i]]
        return dataAccumulated
    except Exception:
        return valueDefault


def treatDecimalField(value, numberOfDecimalPlaces=2, decimalSeparator=','):
    if type(value) == float:
        return value
    try:
        value = str(value)
        value = re.sub('[^0-9.,-]', '', value)
        if decimalSeparator == '.' and value.find(',') >= 0 and value.find('.') >= 0:
            value = value.replace(',', '')
        elif value.find(',') >= 0 and value.find('.') >= 0:
            value = value.replace('.', '')

        if value.find(',') >= 0:
            value = value.replace(',', '.')

        if value.find('.') < 0:
            value = int(value)

        return float(value)
    except Exception:
        return float(0)


def treatDecimalFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', row='main', positionInFileEnd=0):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :param row: este serve pra caso não seja um pagamento que esteja na linha principal (que não tem cabeçalho, então pegar apenas pelo número do campo). O valor 'main' quer dizer que tá numa linha que pode ter cabeçalho
    :return: retorna um campo como decimal
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            if row == 'main':
                return treatDecimalField(data[searchPositionFieldForName(fieldsHeader, nameFieldHeader)])
            else:
                return treatDecimalField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd))
        except Exception:
            try:
                return treatDecimalField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd))
            except Exception:
                return float(0)
    else:
        try:
            return treatDecimalField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd))
        except Exception:
            return float(0)


def treatDateField(valorCampo, formatoData=1):
    """
    :param valorCampo: Informar o campo string que será transformado para DATA
    :param formatoData: 1 = 'DD/MM/YYYY' ; 2 = 'YYYY-MM-DD' ; 3 = 'YYYY/MM/DD' ; 4 = 'DDMMYYYY' ; 5 = 'DDMMYY'
    :return: retorna como uma data. Caso não seja uma data válida irá retornar None
    """
    if type(valorCampo) == 'datetime.date' or type(valorCampo) == 'datetime.datetime':
        return valorCampo

    if isinstance(valorCampo, datetime.datetime):
        return valorCampo.date()

    valorCampo = str(valorCampo).strip()

    lengthField = 10  # tamanho padrão da data são 10 caracteres, só muda se não tiver os separados de dia, mês e ano

    if formatoData == 1:
        formatoDataStr = "%d/%m/%Y"
    elif formatoData == 2:
        formatoDataStr = "%Y-%m-%d"
    elif formatoData == 3:
        formatoDataStr = "%Y/%m/%d"
    elif formatoData == 4:
        formatoDataStr = "%d%m%Y"
        lengthField = 8
    elif formatoData == 5:
        formatoDataStr = "%d/%m/%Y"
        valorCampo = valorCampo[0:6] + '20' + valorCampo[6:]

    try:
        return datetime.datetime.strptime(valorCampo[:lengthField], formatoDataStr)
    except ValueError:
        return None


def treatDateFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', formatoData=1, row='main', positionInFileEnd=0):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :param formatoData: 1 = 'DD/MM/YYYY' ; 2 = 'YYYY-MM-DD (opcional)
    :param row: este serve pra caso não seja um pagamento que esteja na linha principal (que não tem cabeçalho, então pegar apenas pelo número do campo). O valor 'main' quer dizer que tá numa linha que pode ter cabeçalho
    :return: retorna um campo como decimal
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            if row == 'main':
                return treatDateField(data[searchPositionFieldForName(fieldsHeader, nameFieldHeader)], formatoData)
            else:
                return treatDateField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), formatoData)
        except Exception:
            try:
                return treatDateField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), formatoData)
            except Exception:
                return None
    else:
        try:
            return treatDateField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), formatoData)
        except Exception:
            return None


def treatTextField(value: str):
    try:
        return minimalizeSpaces(removeCharSpecials(value.strip().upper()))
    except Exception:
        return ""


def treatTextFieldInVector(data, numberOfField=0, fieldsHeader=[], nameFieldHeader='', positionInFileEnd=0, keepTextOriginal=True):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :return: retorna um campo como texto, retirando acentos, espaços excessivos, etc
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            value = data[searchPositionFieldForName(fieldsHeader, nameFieldHeader)]
            return treatTextField(value) if keepTextOriginal is True else value
        except Exception:
            try:
                value = analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd)
                return treatTextField(value) if keepTextOriginal is True else value
            except Exception:
                return ""
    else:
        try:
            value = analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd)
            return treatTextField(value) if keepTextOriginal is True else value
        except Exception:
            return ""


def treatNumberField(value, isInt=False):
    if type(value) == int:
        return value
    try:
        value = re.sub("[^0-9]", '', value)
        if value == "":
            return 0
        else:
            if isInt is True:
                try:
                    return int(value)
                except Exception:
                    return 0
            return value
    except Exception:
        return 0


def treatNumberFieldInVector(data, numberOfField=-1, fieldsHeader=[], nameFieldHeader='', isInt=False, positionInFileEnd=0):
    """
    :param data: Informar o array de dados que quer ler
    :param numberOfField: numero do campo na planilha (opcional)
    :param fieldsHeader: linha do cabeçalho armazenado num vetor (opcional)
    :param nameFieldHeader: nome do cabeçalho que é pra buscar (opcional)
    :return: retorna um campo apenas como número
    """
    if len(fieldsHeader) > 0 and nameFieldHeader is not None and nameFieldHeader != "":
        try:
            return treatNumberField(data[searchPositionFieldForName(fieldsHeader, nameFieldHeader)], isInt)
        except Exception:
            try:
                return treatNumberField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), isInt)
            except Exception:
                return 0
    else:
        try:
            return treatNumberField(analyzeIfFieldHasPositionInFileEnd(data, numberOfField, positionInFileEnd), isInt)
        except Exception:
            return 0


def formatDate(valueDate: datetime.date, format='%Y-%m-%d'):
    try:
        if str(type(valueDate)).find('datetime') >= 0:
            return valueDate.strftime(format)
    except Exception:
        return valueDate
    return valueDate


def removeAnArrayFromWithinAnother(arraySet=[]):
    newArray = []
    try:
        for array in arraySet:
            if array is None:
                continue
            for vector in array:
                if len(vector) == 0:
                    continue
                newArray.append(vector)
    except Exception:
        pass
    return newArray


def returnBankForNumber(numberBank):
    numberBankOriginal = numberBank
    numberBank = treatNumberField(numberBank, True)
    nameBank = ""
    if numberBank == 1:
        nameBank = 'BRASIL'
    elif numberBank == 3:
        nameBank = 'AMAZONIA'
    elif numberBank == 237:
        nameBank = 'BRADESCO'
    elif numberBank == 104:
        nameBank = 'CEF'
    elif numberBank == 756:
        nameBank = 'SICOOB'
    elif numberBank == 748:
        nameBank = 'SICRED'
    elif numberBank == 33:
        nameBank = 'SANTANDER'
    elif numberBank == 341:
        nameBank = 'ITAU'
    elif numberBank == 743:
        nameBank = 'SEMEAR'
    elif numberBank == 422:
        nameBank = 'SAFRA'
    elif numberBank == 637:
        nameBank = 'SOFISA'
    elif numberBank == 4:
        nameBank = 'NORDESTE'
    elif numberBank == 218:
        nameBank = 'BS2'
    elif numberBank == 634:
        nameBank = 'TRIANGULO'
    elif numberBank == 41:
        nameBank = 'BANRISUL'
    elif numberBank == 70:
        nameBank = 'BRB'
    elif numberBank == 82:
        nameBank = 'TOPAZIO'
    elif numberBank == 260:
        nameBank = 'NUBANK'
    elif numberBank == 336:
        nameBank = 'C6'
    else:
        nameBank = str(numberBankOriginal)

    return nameBank


def returnBankForName(nameBank):
    nameBank = str(nameBank)
    if nameBank.count('BRASIL') > 0:
        nameBank = 'BRASIL'
    elif nameBank.count('BRADESCO') > 0:
        nameBank = 'BRADESCO'
    elif (nameBank.count('CAIXA') > 0 and (nameBank.count('ECON') > 0 or nameBank.count('AG.') > 0 or nameBank.count('FEDERAL') > 0)) or nameBank.count('CEF') > 0:
        nameBank = 'CEF'
    elif nameBank.count('SICOOB') > 0:
        nameBank = 'SICOOB'
    elif nameBank.count('SICRED') > 0:
        nameBank = 'SICRED'
    elif nameBank.count('SANTANDER') > 0:
        nameBank = 'SANTANDER'
    elif nameBank.count('ITAU') > 0:
        nameBank = 'ITAU'
    elif nameBank.count('SAFRA') > 0:
        nameBank = 'SAFRA'
    elif nameBank.count('DINHEIRO') > 0:
        nameBank = 'DINHEIRO'
    else:
        nameBank = nameBank

    return nameBank


def returnMonthByName(nameMonth: str):
    nameMonth = str(nameMonth)
    if nameMonth.find('JAN') >= 0:
        return 1
    elif nameMonth.find('FEV') >= 0:
        return 2
    elif nameMonth.find('MAR') >= 0:
        return 3
    elif nameMonth.find('ABR') >= 0:
        return 4
    elif nameMonth.find('MAI') >= 0:
        return 5
    elif nameMonth.find('JUN') >= 0:
        return 6
    elif nameMonth.find('JUL') >= 0:
        return 7
    elif nameMonth.find('AGO') >= 0:
        return 8
    elif nameMonth.find('SET') >= 0:
        return 9
    elif nameMonth.find('OUT') >= 0:
        return 10
    elif nameMonth.find('NOV') >= 0:
        return 11
    elif nameMonth.find('DEZ') >= 0:
        return 12
    else:
        return None


def roundValueDataPage(dataPage):
    newDataPage = []
    dataPage.sort(key=lambda x: (x[1], x[0]))
    for numberLine, dataLine in enumerate(dataPage):
        nextLine = returnDataInDictOrArray(dataPage, [numberLine + 1])

        # update yLine because round not exact
        yThisLine = dataLine[1]
        yNextLine = returnDataInDictOrArray(nextLine, [1], 0)
        if yThisLine + 1 == yNextLine:
            yThisLine += 1

        # update yLine when is equal nextYLine, because date is first line in process
        dataNextLine = returnDataInDictOrArray(nextLine, [4], '')
        dataNextLineField01 = minimalizeSpaces(returnDataInDictOrArray(dataNextLine.split('\n'), [0]))
        if yThisLine == yNextLine and dataNextLineField01.count('/') == 2:
            yThisLine += 1

        tupleResult = (round(dataLine[0]), yThisLine, round(dataLine[2]), round(dataLine[3]), dataLine[4], dataLine[5], dataLine[6])
        newDataPage.append(tupleResult)
    newDataPage.sort(key=lambda x: (x[1], x[0]))
    return newDataPage


def transformAmountDecimalComma(value: float):
    if value >= 0:
        return str(value).replace('.', ',')
    else:
        value *= -1
        return str(value).replace('.', ',')

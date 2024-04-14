try:
    import unzip_requirements
except ImportError:
    pass

try:
    import datetime
    import logging
    from typing import Dict, Any
    from src.functions import treatDateField, treatTextField, returnDataInDictOrArray, minimalizeSpaces, treatDecimalField, formatDate, treatNumberField, transformAmountDecimalComma
    from src.save_data import SaveData
except Exception as e:
    print(f"Error importing libraries {e}")

logger = logging.getLogger(__name__)


class ProcessModel01(object):
    def __init__(self, dataToSave: Dict[str, Any], dataTxt, nameFile) -> None:
        self.__dataToSave = dataToSave
        self.__dataTxt = dataTxt
        self.__nameFile = nameFile

    async def processAsync(self):
        dataToSave = {}

        UCEnergia = ''
        tipoFornecimento = ''
        cnpj = ''
        endereco = ''
        bairro = ''
        cep = ''
        cidade = ''
        competence = ''
        dueDate = None
        amountInvoice = 0
        qtdKw = 0
        amountInvoiceKw = 0
        qtdKwCredito = 0
        amountInvoiceKwCredito = 0
        contribuicaoPublica = 0
        amountBandeiraVermelha = 0
        UCBaseGeracao = ''
        percentBaseGeracao = 0
        creditoRecebidoKW = 0
        saldoCreditoRecebidoKW = 0
        cadastradoPraReceberCredito = True

        try:
            for idx, line in enumerate(self.__dataTxt):
                numberLine = line['numberLine']
                dataValue = line['dataLine']
                dataValueNextLine = returnDataInDictOrArray(self.__dataTxt, [idx + 1, 'dataLine'])
                dataValueTwoNextLine = returnDataInDictOrArray(self.__dataTxt, [idx + 2, 'dataLine'])
                try:
                    dataValueSplitSpace = dataValue.split(' ')

                    field01 = minimalizeSpaces(returnDataInDictOrArray(dataValueSplitSpace, [0]))
                    field02 = minimalizeSpaces(returnDataInDictOrArray(dataValueSplitSpace, [1]))
                    field03 = minimalizeSpaces(returnDataInDictOrArray(dataValueSplitSpace, [2]))

                    if dataValue.find('TIPO DE FORNECIMENTO:') >= 0 and tipoFornecimento == '':
                        positionFind = dataValue.find('TIPO DE FORNECIMENTO:')
                        lenght = len('TIPO DE FORNECIMENTO:')
                        positionStart = positionFind + lenght
                        tipoFornecimento = treatTextField(dataValue[positionStart:])

                    if dataValue.find('CNPJ/CPF:') >= 0 and cnpj == '':
                        positionFind = dataValue.find('CNPJ/CPF:')
                        lenght = len('CNPJ/CPF:')
                        positionStart = positionFind + lenght
                        cnpj = treatNumberField(dataValue[positionStart:])
                        endereco = ' '.join(dataValueNextLine.split(' ')[0:-4])
                        bairro = dataValueTwoNextLine

                    if dataValue.find('CEP:') >= 0 and cnpj != '':
                        cep = treatNumberField(dataValueSplitSpace[1])
                        cidade = ' '.join(dataValueSplitSpace[2:-2])

                    if dataValue.find('HTTPS://') >= 0 and UCEnergia == '':
                        UCEnergia = treatTextField(field01)

                    if (dataValue.find('JAN/') >= 0 or dataValue.find('FEV/') >= 0 or dataValue.find('MAR/') >= 0 or dataValue.find('ABR/') >= 0 or dataValue.find('MAI/') >= 0
                            or dataValue.find('JUN/') >= 0 or dataValue.find('JUL/') >= 0 or dataValue.find('AGO/') >= 0 or dataValue.find('SET/') >= 0 or dataValue.find('OUT/') >= 0
                            or dataValue.find('NOV/') >= 0 or dataValue.find('DEZ/') >= 0) and amountInvoice == 0:
                        competence = field01
                        dueDate = formatDate(treatDateField(field02), '%d/%m/%Y')
                        amountInvoice = treatDecimalField(field03)

                    if dataValue.find('ENERGIA ATIVA FORNECIDA') >= 0:
                        positionFind = dataValue.find('ENERGIA ATIVA FORNECIDA')
                        lenght = len('ENERGIA ATIVA FORNECIDA')
                        positionStart = positionFind + lenght
                        textEnergiaAtiva = treatTextField(dataValue[positionStart:])
                        textEnergiaAtivaSplit = textEnergiaAtiva.split(' ')
                        qtdKw = treatDecimalField(textEnergiaAtivaSplit[1])
                        amountInvoiceKw = treatDecimalField(textEnergiaAtivaSplit[3])

                    if dataValue.find('VALOR MIN. FATURAVEL CUSTO DISP') >= 0:
                        positionFind = dataValue.find('VALOR MIN. FATURAVEL CUSTO DISP')
                        lenght = len('VALOR MIN. FATURAVEL CUSTO DISP')
                        positionStart = positionFind + lenght
                        textValorMinFaturavel = treatTextField(dataValue[positionStart:])
                        textValorMinFaturavelSplit = textValorMinFaturavel.split(' ')
                        qtdKw = treatDecimalField(textValorMinFaturavelSplit[1])
                        amountInvoiceKw = treatDecimalField(textValorMinFaturavelSplit[3])

                    if dataValue.find('CONSUMO') >= 0 and dataValue.find('KWH') >= 0 and (qtdKw == 0 or amountInvoiceKw == 0) and dataValue.find('CONSUMO') < 5:
                        # print(dataValue)
                        cadastradoPraReceberCredito = False
                        positionFind = dataValue.find('CONSUMO')
                        lenght = len('CONSUMO')
                        positionStart = positionFind + lenght
                        textConsumo = treatTextField(dataValue[positionStart:])
                        textConsumoSplit = textConsumo.split(' ')
                        if textConsumoSplit[1] == 'KWH':
                            qtdKw = treatDecimalField(textConsumoSplit[2])
                            amountInvoiceKw = treatDecimalField(textConsumoSplit[4])
                        else:
                            qtdKw = treatDecimalField(textConsumoSplit[1])
                            amountInvoiceKw = treatDecimalField(textConsumoSplit[3])

                    if dataValue.find('ADC BANDEIRA VERMELHA') >= 0 and amountBandeiraVermelha == 0:
                        positionFind = dataValue.find('ADC BANDEIRA VERMELHA')
                        lenght = len('ADC BANDEIRA VERMELHA')
                        positionStart = positionFind + lenght
                        textBandeiraVermelha = treatTextField(dataValue[positionStart:])
                        textBandeiraVermelhaSplit = textBandeiraVermelha.split(' ')
                        if textBandeiraVermelhaSplit[1] == 'KWH':
                            amountBandeiraVermelha = treatDecimalField(textBandeiraVermelhaSplit[4])
                        elif textBandeiraVermelhaSplit[0] == 'KWH':
                            amountBandeiraVermelha = treatDecimalField(textBandeiraVermelhaSplit[3])
                        else:
                            amountBandeiraVermelha = treatDecimalField(textBandeiraVermelhaSplit[2])

                    if dataValue.find('ENERGIA INJETADA') >= 0:
                        positionFind = dataValue.find('ENERGIA INJETADA')
                        lenght = len('ENERGIA INJETADA')
                        positionStart = positionFind + lenght
                        textEnergiaInjetada = treatTextField(dataValue[positionStart:])
                        textEnergiaInjetadaSplit = textEnergiaInjetada.split(' ')
                        qtdKwCredito = treatDecimalField(textEnergiaInjetadaSplit[1])
                        amountInvoiceKwCredito = treatDecimalField(textEnergiaInjetadaSplit[3])

                    if dataValue.find('CONTRIB. ILUM. PUBLICA - MUNICIPAL') >= 0:
                        positionFind = dataValue.find('CONTRIB. ILUM. PUBLICA - MUNICIPAL')
                        lenght = len('CONTRIB. ILUM. PUBLICA - MUNICIPAL')
                        positionStart = positionFind + lenght
                        textContribPublic = treatTextField(dataValue[positionStart:])
                        textContribPublicSplit = textContribPublic.split(' ')
                        contribuicaoPublica = treatDecimalField(textContribPublicSplit[0])

                    if dataValue.find('CREDITO RECEBIDO KWH:') >= 0:
                        positionFind = dataValue.find('CREDITO RECEBIDO KWH:')
                        lenght = len('CREDITO RECEBIDO KWH:')
                        positionStart = positionFind + lenght
                        positionEnd = dataValue.find('SALDO KWH:')
                        textCreditoRecebido = treatTextField(dataValue[positionStart:positionEnd])
                        creditoRecebidoKW = treatDecimalField(textCreditoRecebido.split('=')[1][:-1])

                    if dataValue.find('SALDO KWH:') >= 0:
                        positionFind = dataValue.find('SALDO KWH:')
                        lenght = len('SALDO KWH:')
                        positionStart = positionFind + lenght
                        positionEnd = dataValue.find('SALDO A EXPIRAR EM 30 DIAS')
                        textSaldoCreditoRecebido = treatTextField(dataValue[positionStart:positionEnd])
                        saldoCreditoRecebidoKW = treatDecimalField(textSaldoCreditoRecebido.split('=')[1][:-1])

                    if dataValue.find('CADASTRO RATEIO GERACAO:') >= 0:
                        positionFind = dataValue.find('CADASTRO RATEIO GERACAO:')
                        lenght = len('CADASTRO RATEIO GERACAO:')
                        positionStart = positionFind + lenght
                        textCadastroRateioGeracao = treatTextField(dataValue[positionStart:])
                        UCBaseGeracao = treatNumberField(textCadastroRateioGeracao.split('=')[0])
                        percentBaseGeracao = treatDecimalField(textCadastroRateioGeracao.split('=')[1])

                    if field01 == 'TOTAL':
                        # dataToSave = {
                        #     "UCEnergia": UCEnergia,
                        #     "tipoFornecimento": tipoFornecimento,
                        #     "cnpj": cnpj,
                        #     "endereco": endereco,
                        #     "bairro": bairro,
                        #     "cep": cep,
                        #     "cidade": cidade,
                        #     "competence": competence,
                        #     "dueDate": dueDate,
                        #     "amountInvoice": amountInvoice,
                        #     "qtdKw": qtdKw,
                        #     "amountInvoiceKw": amountInvoiceKw,
                        #     "qtdKwCredito": qtdKwCredito,
                        #     "amountInvoiceKwCredito": amountInvoiceKwCredito,
                        #     "contribuicaoPublica": contribuicaoPublica,
                        #     "UCBaseGeracao": UCBaseGeracao,
                        #     "percentBaseGeracao": percentBaseGeracao,
                        #     "creditoRecebidoKW": creditoRecebidoKW,
                        #     "saldoCreditoRecebidoKW": saldoCreditoRecebidoKW,
                        # }
                        # print(dataToSave)

                        amountInvoice = transformAmountDecimalComma(amountInvoice)
                        qtdKw = transformAmountDecimalComma(qtdKw)
                        amountInvoiceKw = transformAmountDecimalComma(amountInvoiceKw)
                        qtdKwCredito = transformAmountDecimalComma(qtdKwCredito)
                        amountInvoiceKwCredito = transformAmountDecimalComma(amountInvoiceKwCredito)
                        contribuicaoPublica = transformAmountDecimalComma(contribuicaoPublica)
                        amountBandeiraVermelha = transformAmountDecimalComma(amountBandeiraVermelha)
                        percentBaseGeracao = transformAmountDecimalComma(percentBaseGeracao)
                        creditoRecebidoKW = transformAmountDecimalComma(creditoRecebidoKW)
                        saldoCreditoRecebidoKW = transformAmountDecimalComma(saldoCreditoRecebidoKW)

                        lineToWrite = f"'{UCEnergia};{tipoFornecimento};'{cnpj};{endereco};{bairro};{cep};{cidade};{competence};{dueDate};{amountInvoice};{qtdKw};{amountInvoiceKw};{qtdKwCredito};{amountInvoiceKwCredito};{contribuicaoPublica};{amountBandeiraVermelha};'{UCBaseGeracao};{percentBaseGeracao};{creditoRecebidoKW};{saldoCreditoRecebidoKW};{cadastradoPraReceberCredito};{self.__nameFile}\n"
                        with open('data/result.csv', 'a+') as f:
                            f.write(lineToWrite)

                        cadastradoPraReceberCredito = False

                except Exception as e:
                    print('erro ao processar linha ', numberLine)
                    logger.exception(e)

        except Exception as e:
            self.__dataToSave['typeLog'] = 'error'
            self.__dataToSave['messageLog'] = str(e)
            self.__dataToSave['messageLogToShowUser'] = 'Erro ao processar, entre em contato com suporte'
            saveData = SaveData(self.__dataToSave)
            await saveData.saveData()
            logger.exception(e)

        return self.__dataToSave

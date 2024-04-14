try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    import io
    import logging
    import asyncio
    from src.equatorial.identifies_the_model import IdentifiesTheModel
    from src.equatorial.model01 import ProcessModel01
    from src.equatorial.model02 import ProcessModel02
    from src.convert_txt import ConvertTxt
    from src.save_data import SaveData
    from src.read_txt import readTxt
except Exception as e:
    print(f"Error importing libraries {e}")

logger = logging.getLogger(__name__)

API_HOST_SERVERLESS = os.environ.get('API_HOST_SERVERLESS')
API_HOST_DB_RELATIONAL = os.environ.get('API_HOST_DB_RELATIONAL')


class ReadLinesAndProcessed(object):
    def __init__(self) -> None:
        self.__dataToSave = {}

    async def __readLinesAndProcessed(self, fileData: str, fileRead: str):
        try:
            convertTxt = ConvertTxt()
            pdfResult = convertTxt.pdfToText(fileData)
            dataTxt = readTxt(pdfResult)

            identifiesTheModel = IdentifiesTheModel(fileData, self.__dataToSave)
            self.__dataToSave['modelFile'] = await identifiesTheModel.processSync()

            if self.__dataToSave['modelFile'] == 'model01':
                processModel = ProcessModel01(self.__dataToSave, dataTxt, fileRead)
                self.__dataToSave = await processModel.processAsync()

            if self.__dataToSave['modelFile'] == 'model02':
                processModel = ProcessModel02(self.__dataToSave, dataTxt, fileRead)
                self.__dataToSave = await processModel.processAsync()

        except Exception as e:
            self.__dataToSave['typeLog'] = 'error'
            self.__dataToSave['messageLog'] = str(e)
            self.__dataToSave['messageLogToShowUser'] = 'Erro ao processar, entre em contato com suporte'
            saveData = SaveData(self.__dataToSave)
            await saveData.saveData()
            logger.exception(e)

    def executeJobMainAsync(self, pathFiles):
        try:
            lineToWrite = f"Cod UC;Tipo Padrao;CNPJ;Endereco;Bairro;CEP;Cidade/UF;Competencia;Vencimento;Valor Fatura;Qtd KW Mes;Valor Fatura KW;Qtd KW Credito;Valor Deduzido Fatura;Valor Cont Publica;Bandeira Vermelha;Cod UC Geracao;Percentual Geracao;Credito Recebido KW;Saldo Credito KW;Cadastrado pra Receber Credito;Arquivo\n"
            with open('data/result.csv', 'w+') as fileWrite:
                fileWrite.write(lineToWrite)

            for fileRead in os.listdir(pathFiles):
                if str(fileRead).find('.pdf') > 0:
                    print('- Lendo arquivo', fileRead)
                    try:
                        with open(f'{pathFiles}/{fileRead}', 'rb') as f:
                            fileContent = f.read()
                            fileBytesIO = io.BytesIO(fileContent)
                            asyncio.run(self.__readLinesAndProcessed(fileBytesIO, fileRead))
                    except Exception as e:
                        print(e)

        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    main = ReadLinesAndProcessed()
    main.executeJobMainAsync('')

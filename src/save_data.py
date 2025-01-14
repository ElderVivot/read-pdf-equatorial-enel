try:
    import unzip_requirements
except ImportError:
    pass

try:
    import os
    import gzip
    import base64
    from aiohttp import ClientSession
    from datetime import datetime
    from typing import Dict, Any
    import json
    from src.functions import formatDate
except Exception as e:
    print(f"Error importing libraries {e}")

API_HOST_SERVERLESS = os.environ.get('API_HOST_SERVERLESS')
API_HOST_DB_RELATIONAL = os.environ.get('API_HOST_DB_RELATIONAL')


class SaveData(object):
    def __init__(self, dataToSave: Dict[str, Any], zipData=False) -> None:
        self.__dataToSave = dataToSave
        self.__dataToSave['startPeriod'] = formatDate(self.__dataToSave['startPeriod'])
        self.__dataToSave['endPeriod'] = formatDate(self.__dataToSave['endPeriod'])
        self.__zipData = zipData
        print('zipData', self.__zipData)

    async def __put(self, session: ClientSession, url: str, data: Any, headers: Dict[str, str]):
        async with session.put(url, json=data, headers=headers) as response:
            data = await response.json()
            return data, response.status

    async def saveData(self, ):
        try:
            async with ClientSession() as session:
                if self.__zipData is False:
                    response, statusCode = await self.__put(
                        session,
                        f"{API_HOST_SERVERLESS}/lanc-contabeis-extract-bank",
                        data=json.loads(json.dumps(self.__dataToSave)),
                        headers={}
                    )
                    if statusCode >= 400:
                        raise Exception(statusCode, response)
                else:
                    dataJson = json.dumps(self.__dataToSave)
                    dataBytes = bytes(dataJson, 'utf-8')
                    dataCompress = gzip.compress(dataBytes)
                    dataEncoded = base64.b64encode(dataCompress)

                    response, statusCode = await self.__put(
                        session,
                        f"{API_HOST_SERVERLESS}/lanc-contabeis-extract-bank-zip",
                        data=json.loads(json.dumps({"data": dataEncoded.decode()})),
                        headers={}
                    )
                    if statusCode >= 400:
                        raise Exception(statusCode, response)
                print('Salvo no banco de dados')
        except Exception as e:
            print('Error ao salvar dado dynamodb')
            print(e)
            self.__dataToSave['typeLog'] = 'error'
            self.__dataToSave['messageLog'] = str(e)
            self.__dataToSave['messageLogToShowUser'] = 'Erro ao salvar resultado do processamento, entre em contato com o suporte'

        await self.__saveDataApiRelational()

    async def __saveDataApiRelational(self):
        try:
            async with ClientSession() as session:
                response, statusCode = await self.__put(
                    session,
                    f"{API_HOST_DB_RELATIONAL}/lanc_contabil_extract_bank/{self.__dataToSave['id']}",
                    data={
                        "idLancContabilExtractBank": self.__dataToSave['id'],
                        "idCompanie": self.__dataToSave['idCompanie'],
                        "numberBank": self.__dataToSave['numberBank'],
                        "startPeriod": self.__dataToSave['startPeriod'],
                        "endPeriod": self.__dataToSave['endPeriod'],
                        "urlFile": self.__dataToSave['urlFile'],
                        "typeLog": self.__dataToSave['typeLog'],
                        "messageLog": self.__dataToSave['messageLog'],
                        "messageLogToShowUser": self.__dataToSave['messageLogToShowUser'],
                        "messageError": ""
                    },
                    headers={"TENANT": self.__dataToSave['tenant']}
                )
                if statusCode >= 400:
                    raise Exception(statusCode, response)
                print('Salvo no banco de dados relacional')

                return response
        except Exception as e:
            print('Error ao salvar dado banco relacional')
            print(e)

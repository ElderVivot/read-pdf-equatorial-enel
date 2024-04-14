from src.functions import treatTextField


def readTxt(dataTxt):
    newDataDoc = []
    numberLine = 0
    for line in dataTxt.split('\n'):
        try:
            dataValue = treatTextField(line)
            numberLine += 1
            newDataDoc.append({
                "numberLine": numberLine,
                "dataLine": dataValue
            })
        except Exception as e:
            print(e)

    return newDataDoc

def getTenant(urlFile: str):
    try:
        return urlFile.split('/')[-3]
    except Exception:
        return ''


def getIdCompanie(urlFile: str):
    try:
        return urlFile.split('/')[-2]
    except Exception:
        return ''


def getId(urlFile: str):
    try:
        return urlFile.split('/')[-1].split('.')[0]
    except Exception:
        return urlFile

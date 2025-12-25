from googleapiclient.discovery import build


def get_service(api_key: str):
    service: object = build(
        "youtube",
        "v3",
        developerKey=api_key,
    )
    return service

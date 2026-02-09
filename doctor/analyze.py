from docker import from_env

def connect():
    return from_env()

def system_df(client) -> dict:
    """
    Uses Docker Engine's /system/df endpoint (same data as `docker system df`)
    """
    return client.api.df()

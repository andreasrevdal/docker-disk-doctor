from docker import from_env

def connect():
    return from_env()

def system_df(client):
    return client.api.df()

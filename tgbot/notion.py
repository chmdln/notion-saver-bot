import os 
from notion_client import AsyncClient 


from dotenv import find_dotenv, load_dotenv 
load_dotenv(find_dotenv())
client= AsyncClient(auth=os.getenv('NOTION_TOKEN'))
database_id = os.getenv('DATABASE_ID') 



def safe_get(data, dot_chained_keys):
    keys = dot_chained_keys.split('.')
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return None
    return data


async def get_db_rows(database_id): 
    db_rows = await client.databases.query(database_id=database_id)
    return db_rows



async def add_data(client, database_id, url, title, category, priority, timestamp):
    await client.pages.create(
        **{
            "parent": {
                "database_id": database_id
            },
            'properties': {
                'URL': {'url': url},
                'Title': {'title': [{'text': {'content': title}}]},
                'Category': {'select': {'name': category}}, 
                'Priority': {"select": {"name": priority}}, 
                'Timestamp': {"date": {"start": timestamp}}
            }
        }
    )



    

                

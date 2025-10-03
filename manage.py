import click
import uvicorn

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('.env', usecwd=True))

@click.group()
def cli():
    pass

@cli.command()
def runserver():
    return uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True, proxy_headers=True)

if __name__ == '__main__':
    cli()
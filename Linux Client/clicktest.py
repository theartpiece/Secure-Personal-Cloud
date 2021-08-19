#! /home/jatin/iitb/third_sem/cs251/project/env_SPC/bin/python
import click
import rstatus, lstatus, sync, lsync 

@click.group()
def cli():
    pass

@click.command()
def initdb():
    click.echo('Initialized the database')
    rstatus.rstatus()

@click.command()
def dropdb():
    click.echo('Dropped the database')
    lstatus.lstatus()

cli.add_command(initdb)
cli.add_command(dropdb)

if __name__ == '__main__':
    cli()
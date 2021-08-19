import click,os
import rstatus, lstatus, rsync, lsync, set_root, initialise, set_server_ip, user_config, enc_dec
 
@click.group()
def cli():
	"""SPC is remote file storage system where you have control over the encryption schema. For more details type man SPC"""
	pass

@cli.group()
def observe():
	"""use 'set' to set the observing directory, 'show' to display it."""
	pass

@cli.group()
def server():
	"""use 'set' for  setting the <ip address:port number>, use 'show' to show the current IP."""
	pass

@cli.group()
def schedule():
	"""set reminder for syncing after regular intervals set by user"""
	pass


@cli.group()
def en_de():
	'''for specification and manipulation of encryption schema'''
	pass

@cli.group()
def config():
	"""use 'edit' for editing metainformation and 'show' to display."""
	pass

@cli.command()
@click.option('--l/--r', default=True)
def status(l):
	"""show status of file tracking. use --r for remote status and --l for local status."""
	if l:
		lstatus.lstatus()
	else:
		rstatus.rstatus()

@cli.command()
def add():
	"""Sync your files with the local database. Add files to staging area."""
	lsync.lsync()

@cli.command()
def sync():
	"""sync with remote directory."""
	rsync.sync()


@observe.command()
@click.argument('path',nargs=1)
def set(path):
	set_root.set(path)

@observe.command()
def show():
	"""Show current version of SPC"""
	set_root.show()


@cli.command()
def init():
	"""Initialise tracking tools and database."""
	initialise.initialise()

@cli.command()
def version():
	'''Shoe current version'''
	click.echo('  SPC [version 1.0.4]')


@server.command()
@click.argument('address',nargs=1)
def set(address):
	set_server_ip.set(address)

@server.command()
def show():
	set_server_ip.show()


@config.command()
def edit():
	user_config.edit()

@config.command()
def show():
	user_config.show()

@en_de.command()
def list():
	''' list encryption schema used. '''
	enc_dec.list()

@en_de.command()
def update():
	''' update encryption schema used.'''
	enc_dec.update()

@en_de.command()
def dump():
	''' dump encryption schema to file. '''
	enc_dec.dump()


@schedule.command()
def start():
    os.system('bash scheduleSync.sh')

@schedule.command()
def stop():
    os.system('bash removeScheduler.sh')


if __name__ == '__main__':
    cli()
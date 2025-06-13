import click
from flask.cli import with_appcontext
from app import db
from app.models.user import User
from app.routes.auth import validate_email, validate_password

@click.command('create-admin')
@click.option('--email', prompt='Admin email', help='Email for the admin user')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password for the admin user')
@with_appcontext
def create_admin(email, password):
    """Create the first admin user."""
    # Validate email
    if not validate_email(email):
        click.echo('Error: Invalid email format')
        return

    # Validate password
    is_valid_password, password_error = validate_password(password)
    if not is_valid_password:
        click.echo(f'Error: {password_error}')
        return

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        click.echo('Error: User with this email already exists')
        return

    # Create admin user
    admin = User(email=email, is_admin=True)
    admin.set_password(password)

    try:
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Successfully created admin user: {email}')
    except Exception as e:
        db.session.rollback()
        click.echo('Error: Failed to create admin user')
        click.echo(str(e)) 
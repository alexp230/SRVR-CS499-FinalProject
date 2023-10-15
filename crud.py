"""
This file is used to create, read, update, and delete data from the database for testing purposes.
It is not used in the final version of the project.
"""
from main import db, app, User

# Create a new user object
new_user = User(name="John Doe", email="johndoe@example.com", password="password123", address="123 Main St", subscriptionType="basic")

with app.app_context():
    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    # Query the user within the same app context
    user = User.query.filter_by(name='John Doe').first()
    print(User.query.all())

    for user in User.query.all():
        print(f"Deleted {user.name} from the database.")
        db.session.delete(user)
        db.session.commit()
    print(User.query.all())

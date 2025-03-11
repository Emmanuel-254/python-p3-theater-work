import argparse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Set up the base for SQLAlchemy
Base = declarative_base()

# Define the Role class (which corresponds to the 'roles' table)
class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    character_name = Column(String)

    # Relationship: Role -> Audition (One-to-Many)
    auditions = relationship('Audition', back_populates='role')

    def __repr__(self):
        return f"<Role(character_name='{self.character_name}')>"

    # Method to get all the actors for a role
    def actors(self):
        return [audition.actor for audition in self.auditions]

    # Method to get all the locations for a role
    def locations(self):
        return [audition.location for audition in self.auditions]

    # Method to get the lead actor (first hired audition)
    def lead(self):
        hired_auditions = [audition for audition in self.auditions if audition.hired]
        return hired_auditions[0] if hired_auditions else "no actor has been hired for this role"

    # Method to get the understudy (second hired audition)
    def understudy(self):
        hired_auditions = [audition for audition in self.auditions if audition.hired]
        return hired_auditions[1] if len(hired_auditions) > 1 else "no actor has been hired for understudy for this role"

# Define the Audition class (which corresponds to the 'auditions' table)
class Audition(Base):
    __tablename__ = 'auditions'
    
    id = Column(Integer, primary_key=True)
    actor = Column(String)
    location = Column(String)
    phone = Column(Integer)
    hired = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey('roles.id'))

    # Relationship: Audition -> Role (Many-to-One)
    role = relationship('Role', back_populates='auditions')

    def __repr__(self):
        return f"<Audition(actor='{self.actor}', location='{self.location}', hired={self.hired})>"

    # Method to call back the actor (hire them)
    def call_back(self):
        self.hired = True

# Create an SQLite database (in-memory for this example)
engine = create_engine('sqlite:///theater_company.db', echo=True)

# Create the tables in the database (if they don't already exist)
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# CLI Functions
def add_role():
    role_name = input("Enter the role character name: ")
    role = Role(character_name=role_name)
    session.add(role)
    session.commit()
    print(f"Role {role_name} added successfully!")

def add_audition():
    role_name = input("Enter the role character name: ")
    role = session.query(Role).filter_by(character_name=role_name).first()
    if role:
        actor = input("Enter actor name: ")
        location = input("Enter audition location: ")
        phone = int(input("Enter phone number: "))
        audition = Audition(actor=actor, location=location, phone=phone, role=role)
        session.add(audition)
        session.commit()
        print(f"Audition for {actor} added to role {role_name}!")
    else:
        print(f"No role found with name {role_name}.")

def view_roles():
    roles = session.query(Role).all()
    for role in roles:
        print(f"Role: {role.character_name}")
        print(f"Actors: {role.actors()}")
        print(f"Locations: {role.locations()}")
        print(f"Lead: {role.lead()}")
        print(f"Understudy: {role.understudy()}")

def main():
    parser = argparse.ArgumentParser(description='Theater Company Audition CLI')
    parser.add_argument('action', choices=['add_role', 'add_audition', 'view_roles'], help='Action to perform')

    args = parser.parse_args()

    if args.action == 'add_role':
        add_role()

    elif args.action == 'add_audition':
        add_audition()

    elif args.action == 'view_roles':
        view_roles()

if __name__ == '__main__':
    main()

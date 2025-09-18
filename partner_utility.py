import argparse
import logging
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import models, auth
from app.config import settings

logging.basicConfig(level=logging.INFO)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

def create_partner(username, password, role, partner_name):
    """Creates a new partner in the database with a specific role."""
    db = SessionLocal()
    try:
        existing_partner = db.query(models.Partner).filter(models.Partner.username == username).first()
        if existing_partner:
            logging.warning(f"Partner with username '{username}' already exists.")
            return

        hashed_password = auth.get_password_hash(password)
        new_partner = models.Partner(
            username=username,
            hashed_password=hashed_password,
            partner_name=partner_name,
            role=role
        )
        db.add(new_partner)
        db.commit()
        logging.info(f"Successfully created partner '{username}' with role '{role}'.")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new KaziLeo partner.")
    parser.add_argument("username", help="The username for the new partner.")
    parser.add_argument("password", help="The password for the new partner.")
    parser.add_argument("--role", choices=['tvet', 'employer'], default='employer', help="The role of the partner (tvet or employer).")
    parser.add_argument("--name", required=True, help="The official display name of the partner organization.")
    args = parser.parse_args()

    create_partner(args.username, args.password, args.role, args.name)


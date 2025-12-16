import secrets
import sys

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import APIKey


def create_api_key() -> str:
    return secrets.token_urlsafe(32)


def add_key(db: Session, key: str | None = None) -> str:
    if key is None:
        key = create_api_key()

    existing_key = db.query(APIKey).filter(APIKey.key == key).first()
    if existing_key:
        print(f"Error: API key already exists: {key}")
        sys.exit(1)

    db_key = APIKey(key=key, is_active=True)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    print(f"API key added successfully: {key}")
    print(f"  Status: {'Active' if db_key.is_active else 'Inactive'}")
    print(f"  Created: {db_key.created_at}")
    return key


def list_keys(db: Session) -> None:
    keys = db.query(APIKey).all()
    if not keys:
        print("No API keys found.")
        return

    print(f"Found {len(keys)} API key(s):")
    for key in keys:
        status = "Active" if key.is_active else "Inactive"
        print(f"  - {key.key}")
        print(f"    ID: {key.id}")
        print(f"    Status: {status}")
        print(f"    Created: {key.created_at}")


def deactivate_key(db: Session, key: str) -> None:
    db_key = db.query(APIKey).filter(APIKey.key == key).first()
    if not db_key:
        print(f"Error: API key not found: {key}")
        sys.exit(1)

    db_key.is_active = False
    db.commit()
    print(f"API key deactivated successfully: {key}")


def activate_key(db: Session, key: str) -> None:
    db_key = db.query(APIKey).filter(APIKey.key == key).first()
    if not db_key:
        print(f"Error: API key not found: {key}")
        sys.exit(1)

    db_key.is_active = True
    db.commit()
    print(f"API key activated successfully: {key}")


def delete_key(db: Session, key: str) -> None:
    db_key = db.query(APIKey).filter(APIKey.key == key).first()
    if not db_key:
        print(f"Error: API key not found: {key}")
        sys.exit(1)

    db.delete(db_key)
    db.commit()
    print(f"API key deleted successfully: {key}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_api_keys.py add [key]        # Add a new API key")
        print("  python manage_api_keys.py list             # List all API keys")
        print("  python manage_api_keys.py activate <key>   # Activate an API key")
        print("  python manage_api_keys.py deactivate <key> # Deactivate an API key")
        print("  python manage_api_keys.py delete <key>     # Delete an API key")
        sys.exit(1)

    command = sys.argv[1]
    db = SessionLocal()

    try:
        if command == "add":
            key = sys.argv[2] if len(sys.argv) > 2 else None
            add_key(db, key)
        elif command == "list":
            list_keys(db)
        elif command == "activate":
            if len(sys.argv) < 3:
                print("Error: Please provide the API key to activate")
                sys.exit(1)
            activate_key(db, sys.argv[2])
        elif command == "deactivate":
            if len(sys.argv) < 3:
                print("Error: Please provide the API key to deactivate")
                sys.exit(1)
            deactivate_key(db, sys.argv[2])
        elif command == "delete":
            if len(sys.argv) < 3:
                print("Error: Please provide the API key to delete")
                sys.exit(1)
            delete_key(db, sys.argv[2])
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

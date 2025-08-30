# test_cli.py
import asyncio
from sqlalchemy.orm import Session
from app import crud, services, whatsapp_client # Import the client
from app.database import SessionLocal, engine, Base

# --- IMPORTANT: Activate Mock Mode ---
# This tells the whatsapp_client to print messages instead of sending them.
whatsapp_client.MOCK_MODE = True

# This ensures the database tables are created if they don't exist
Base.metadata.create_all(bind=engine)

async def main():
    """
    A command-line interface to test the KaziLeo bot's logic
    without needing a live WhatsApp connection.
    """
    print("--- KaziLeo Command-Line Tester ---")
    print("Type 'exit' to end the session.")
    
    # Use a consistent phone number for the test session
    test_phone_number = "cli_user_123"
    test_user_name = "Test User"
    
    # Get a database session
    db: Session = SessionLocal()
    
    # Get or create the user session
    session, is_new = crud.get_or_create_session(db, phone_number=test_phone_number, user_name=test_user_name)
    
    print(f"\n[System] Starting session for user: {test_user_name} (New User: {is_new})")
    print("-" * 20)

    # Send an initial "hi" to start the conversation
    print("KaziLeo:")
    await services.process_message(db, session, "hi", is_new_user=is_new)
    crud.update_session(db, session)

    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            print("[System] Ending session. Goodbye!")
            break
            
        print("\nKaziLeo:")
        # Process the user's message using our existing services logic
        await services.process_message(db, session, user_input, is_new_user=False)
        
        # IMPORTANT: We must update the session after each message to save the state
        crud.update_session(db, session)

    db.close()

if __name__ == "__main__":
    asyncio.run(main())

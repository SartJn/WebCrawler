import os
from dotenv import load_dotenv
from bot import InfoBot
from crawler import EnhancedWebCrawler

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
    
    if not all([BOT_TOKEN, GOOGLE_API_KEY, SEARCH_ENGINE_ID]):
        raise ValueError("Missing required API keys in environment variables")
    
    # Initialize crawler
    crawler = EnhancedWebCrawler(
        google_api_key=GOOGLE_API_KEY,
        search_engine_id=SEARCH_ENGINE_ID
    )
    
    # Initialize and run bot
    bot = InfoBot(BOT_TOKEN, crawler)
    print("Bot is running...")
    bot.run()

if __name__ == "__main__":
    main()
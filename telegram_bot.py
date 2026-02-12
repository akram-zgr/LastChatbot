"""
Multi-University Telegram Bot for Algerian Universities
"""
import os
import sys
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Add parent directory to path to import from project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from models.university import University
from models.user import User
from services.knowledge_service import knowledge_service
from services.openai_service import generate_chat_response, count_tokens

# Get Telegram bot token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7881679177:AAF5FuUPbVKAqifrmV7zYyuj8Oe4X4cadaE')

# Store conversation history and user data per Telegram user
user_conversations = {}
user_data = {}  # Store university selection and preferences

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show university selection"""
    user_id = update.effective_user.id
    
    # Initialize user data
    user_conversations[user_id] = []
    user_data[user_id] = {
        'university_id': None,
        'session_start': datetime.now(),
        'language': 'en'  # default language
    }
    
    # Get active universities from database
    try:
        from app import app
        with app.app_context():
            universities = University.query.filter_by(is_active=True).order_by(University.name).all()
            
            if not universities:
                await update.message.reply_text(
                    "⚠️ No universities are currently available. Please try again later."
                )
                return
            
            # Create inline keyboard with university options
            keyboard = []
            for uni in universities:
                button_text = f"{uni.name}"
                if uni.city:
                    button_text += f" ({uni.city})"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"uni_{uni.id}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = """🎓 Welcome to Algerian Universities AI Assistant!

I'm here to help you with information about your university including:
- Course registration and enrollment 📚
- Tuition fees and payments 💰  
- Academic information and grades 📊
- Campus facilities and services 🏢
- Exams and schedules 📝
- Student services 🎫

Please select your university to get started:"""
            
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
            
    except Exception as e:
        print(f"Error in start command: {e}")
        await update.message.reply_text(
            "Sorry, I encountered an error. Please try /start again."
        )

async def university_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle university selection from inline keyboard"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    if callback_data.startswith("uni_"):
        university_id = int(callback_data.split("_")[1])
        
        try:
            from app import app
            with app.app_context():
                university = University.query.get(university_id)
                
                if not university:
                    await query.edit_message_text("❌ University not found. Please try /start again.")
                    return
                
                # Save university selection
                if user_id not in user_data:
                    user_data[user_id] = {}
                
                user_data[user_id]['university_id'] = university_id
                user_data[user_id]['university_name'] = university.name
                user_data[user_id]['session_start'] = datetime.now()
                
                # Initialize conversation
                user_conversations[user_id] = []
                
                confirmation_text = f"""✅ University Selected: {university.name}

I'm now ready to help you with information specific to {university.name}.

You can:
- Ask questions in Arabic, English, or French
- Use /reset to clear conversation and change university
- Use /help to see available commands

How can I assist you today?"""
                
                await query.edit_message_text(confirmation_text)
                
        except Exception as e:
            print(f"Error in university selection: {e}")
            await query.edit_message_text("❌ Error selecting university. Please try /start again.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user_id = update.effective_user.id
    
    university_info = ""
    if user_id in user_data and user_data[user_id].get('university_id'):
        university_info = f"\n🎓 Your University: {user_data[user_id].get('university_name', 'Not set')}\n"
    
    help_message = f"""🤖 Algerian Universities AI Assistant Help
{university_info}
I can assist you with:
📚 Course registration and enrollment
💰 Tuition fees and payments
📊 Academic information and grades
🏢 Campus facilities and services
📝 Exams and schedules
🎫 Student services

Commands:
/start - Select your university or start new session
/help - Show this help message
/reset - Clear conversation and change university
/status - Show your current session info

Features:
✅ Multi-language support (Arabic, English, French)
✅ University-specific knowledge base
✅ Context-aware conversations

Just send me your question and I'll help you!"""
    
    await update.message.reply_text(help_message)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command - clear conversation and allow university reselection"""
    user_id = update.effective_user.id
    
    # Calculate session info
    session_info = ""
    if user_id in user_data and 'session_start' in user_data[user_id]:
        session_start = user_data[user_id]['session_start']
        session_duration = datetime.now() - session_start
        
        total_minutes = int(session_duration.total_seconds() / 60)
        if total_minutes < 1:
            duration_text = "less than a minute"
        elif total_minutes < 60:
            duration_text = f"{total_minutes} minute{'s' if total_minutes != 1 else ''}"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            duration_text = f"{hours} hour{'s' if hours != 1 else ''}"
            if minutes > 0:
                duration_text += f" and {minutes} minute{'s' if minutes != 1 else ''}"
        
        session_info = f"\n✅ Session lasted {duration_text}"
        message_count = len(user_conversations.get(user_id, []))
        if message_count > 0:
            session_info += f"\n✅ You sent {message_count} message{'s' if message_count != 1 else ''}"
    
    # Clear user data
    user_conversations[user_id] = []
    if user_id in user_data:
        del user_data[user_id]
    
    reset_message = f"""🔄 *Session Reset*{session_info}

All conversation history has been cleared.

Use /start to select your university and begin a new session."""
    
    await update.message.reply_text(reset_message, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current session status"""
    user_id = update.effective_user.id
    
    if user_id not in user_data or not user_data[user_id].get('university_id'):
        await update.message.reply_text(
            "❌ No active session. Use /start to select your university."
        )
        return
    
    data = user_data[user_id]
    session_start = data.get('session_start', datetime.now())
    duration = datetime.now() - session_start
    minutes = int(duration.total_seconds() / 60)
    
    message_count = len(user_conversations.get(user_id, []))
    
    status_text = f"""📊 *Session Status*

🎓 University: {data.get('university_name', 'Unknown')}
⏱️ Session Duration: {minutes} minute(s)
💬 Messages: {message_count}
🌐 Language: {data.get('language', 'en').upper()}

Use /reset to start a new session."""
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with university-specific knowledge"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Check if user has selected a university
    if user_id not in user_data or not user_data[user_id].get('university_id'):
        await update.message.reply_text(
            "⚠️ Please use /start to select your university first."
        )
        return
    
    # Initialize conversation history if needed
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    try:
        university_id = user_data[user_id]['university_id']
        
        # Get university context and knowledge from database
        from app import app
        with app.app_context():
            university_context = knowledge_service.get_university_context(university_id)
            
            # Search knowledge base
            knowledge_results = knowledge_service.search_knowledge(user_message, university_id, limit=3)
            
            knowledge_context = None
            if knowledge_results:
                knowledge_pieces = []
                for result in knowledge_results:
                    knowledge_pieces.append(f"- {result['title']}: {result['content'][:300]}")
                knowledge_context = "\n".join(knowledge_pieces)
            
            # Add user message to history
            user_conversations[user_id].append({
                'role': 'user',
                'content': user_message
            })
            
            # Keep only last 10 messages to manage memory
            if len(user_conversations[user_id]) > 10:
                user_conversations[user_id] = user_conversations[user_id][-10:]
            
            # Generate AI response with university and knowledge context
            ai_response, model_used = generate_chat_response(
                user_conversations[user_id],
                university_context=university_context,
                knowledge_context=knowledge_context
            )
            
            # Add AI response to history
            user_conversations[user_id].append({
                'role': 'assistant',
                'content': ai_response
            })
            
            await update.message.reply_text(ai_response)
            
    except Exception as e:
        error_message = "Sorry, I encountered an error processing your message. Please try again or use /reset to start a new session."
        await update.message.reply_text(error_message)
        print(f"Error generating response: {e}")
        import traceback
        traceback.print_exc()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Update {update} caused error {context.error}")

def main():
    """Start the Telegram bot"""
    # Check if token is set
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == '7881679177:AAF5FuUPbVKAqifrmV7zYyuj8Oe4X4cadaE':
        print("⚠️  Warning: Using default token. Please set your TELEGRAM_BOT_TOKEN environment variable")
        print("Get your token from @BotFather on Telegram")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(university_selection_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    print("🤖 Algerian Universities Telegram Bot is running...")
    print("✅ Multi-university support enabled")
    print("✅ Knowledge-based AI responses active")
    print("✅ Multi-language support (AR/EN/FR)")
    print("Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

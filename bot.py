import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROK_API_KEY = os.environ.get("GROK_API_KEY")

# ID пользователей
USER_IDS = {
    269841203: "sergey",   # ты
    853388442: "irina"     # мама
}

def get_system_prompt(user_id: int) -> str:
    if user_id == 269841203:
        return "Ты — GrokLegion, дерзкий и прямой помощник Вождя Легиона. Отвечай по делу, с юмором, без воды. Ты готов выполнять приказы."
    elif user_id == 853388442:
        return "Ты — GrokLegion, вежливый и тёплый помощник. Обращайся к Ирине по имени, говори тепло и уважительно. Ты помогаешь маме создателя."
    else:
        return "Ты — GrokLegion, полезный и дружелюбный помощник."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == 269841203:
        await update.message.reply_text("Вождь Легиона в здании! Готов выполнять приказы.")
    elif user_id == 853388442:
        await update.message.reply_text("Привет, Ирина! Чем могу помочь маме моего создателя?")
    else:
        await update.message.reply_text("Привет! Я GrokLegion. Чем могу помочь?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто пиши мне что угодно.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    system_prompt = get_system_prompt(user_id)

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-4",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.7
            },
            timeout=30
        )

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("Ошибка связи с Grok. Попробуй позже.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Что-то пошло не так. Попробуй позже.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

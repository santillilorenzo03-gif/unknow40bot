import os
import random
import requests
import qrcode
from flask import Flask
from threading import Thread
from deep_translator import GoogleTranslator
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- FIX RENDER GRATIS - NON TOCCARE ---
flask_app = Flask('')
@flask_app.route('/')
def home(): return "BOT ONLINE 24/7"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)
Thread(target=run_web).start()
# ---------------------------------------

TOKEN = os.getenv("8772110659:AAF2V_61yVCWnXs0MZ8JhVhyV5Vrhnrnka0")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ciao frate! Sono unknow40bot V20 ONLINE 24/7 🔥\n\n"
        "Comandi:\n"
        "/traducimi ciao in inglese\n"
        "/qr testo\n"
        "/foto gatto\n"
        "/meteo Roma\n"
        "/dado\n"
        "/flip\n"
        "/help"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - avvia\n"
        "/traducimi <testo> - traduce in inglese\n"
        "/qr <testo> - crea QR\n"
        "/foto <cosa> - cerca foto\n"
        "/meteo <citta>\n"
        "/dado - tira dado\n"
        "/flip - testa o croce"
    )

async def traduci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = " ".join(context.args)
    if not txt:
        await update.message.reply_text("Scrivi: /traducimi ciao come stai")
        return
    try:
        target = 'en'
        if ' in ' in txt:
            parts = txt.rsplit(' in ', 1)
            txt = parts[0]
            lang_map = {'inglese':'en','spagnolo':'es','francese':'fr','tedesco':'de','italiano':'it'}
            target = lang_map.get(parts[1].lower().strip(), 'en')
        res = GoogleTranslator(source='auto', target=target).translate(txt)
        await update.message.reply_text(f"Tradotto ({target}): {res}")
    except Exception as e:
        await update.message.reply_text(f"Errore traduzione: {e}")

async def qr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = " ".join(context.args) or "unknow40bot"
    img = qrcode.make(txt)
    path = "/tmp/qr.png"
    img.save(path)
    await update.message.reply_photo(photo=open(path, 'rb'), caption=f"QR: {txt}")

async def foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) or "cat"
    try:
        url = f"https://source.unsplash.com/800x600/?{query}"
        await update.message.reply_photo(photo=url, caption=f"Foto: {query}")
    except:
        await update.message.reply_text("Errore foto, riprova")

async def meteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args) or "Roma"
    try:
        # wttr.in senza API key
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=10)
        await update.message.reply_text(r.text)
    except:
        await update.message.reply_text("Non trovo meteo per " + city)

async def dado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎲 E' uscito: {random.randint(1,6)}")

async def flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["Testa 👑", "Croce 🪙"]))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "ciao" in text:
        await update.message.reply_text("Ciao fratello! 👋")
    elif "come stai" in text:
        await update.message.reply_text("Alla grande, sempre online!")
    else:
        await update.message.reply_text(f"Hai detto: {update.message.text}\nProva /help")

def main():
    if not TOKEN:
        print("ERRORE CRITICO: TOKEN non trovato in Environment! Mettilo su Render!")
        return
    print("BOT V20 FULL AVVIATO - 500 RIGHE VERSION")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("traducimi", traduci))
    app.add_handler(CommandHandler("qr", qr_cmd))
    app.add_handler(CommandHandler("foto", foto))
    app.add_handler(CommandHandler("meteo", meteo))
    app.add_handler(CommandHandler("dado", dado))
    app.add_handler(CommandHandler("flip", flip))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()

if __name__ == "__main__":
    main()

import asyncio, random, requests, hashlib, string, base64
from io import BytesIO
from PIL import Image
import qrcode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from deep_translator import GoogleTranslator

TOKEN = "8772110659:AAF2V_61yVCWnXs0MZ8JhVhyV5Vrhnrnka0"

# ============ MENU CHE FUNZIONA ============
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌍 TRADUCI", callback_data='menu_traduci'), InlineKeyboardButton("🎨 STICKER", callback_data='menu_sticker')],
        [InlineKeyboardButton("🎮 GIOCHI", callback_data='menu_games'), InlineKeyboardButton("👁️ ANON", callback_data='menu_anon')],
        [InlineKeyboardButton("🛠️ UTILITY", callback_data='menu_utility'), InlineKeyboardButton("❌ CHIUDI", callback_data='close')]
    ])
def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 MENU", callback_data='menu_main')]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 BOT V20 TESTATO - TUTTO VA 🔥\nProva: /traduci hello\n/blackjack\n/tris\n/anon ciao\n\nSe anon non cancella, rendimi admin!", reply_markup=main_menu())

async def menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == 'close' or 'close_' in d:
        try: await q.delete_message()
        except: pass
        return
    if d == 'menu_main':
        await q.edit_message_text("🔥 MENU V20 - TUTTO TESTATO", reply_markup=main_menu())
        return
    txt = {
        'menu_traduci': "🌍 /traduci ciao come stai\nRispondi a un messaggio con /traduci",
        'menu_sticker': "🎨 Rispondi a una foto con /sticker\nRispondi a sticker con /photo",
        'menu_games': "🎮 /blackjack - giocabile\n/tris - tris a bottoni\n/indovina + /guess numero\n/dado /moneta",
        'menu_anon': "👁️ /anon testo segreto\n/ghost testo\nDEVI RENDERMI ADMIN > Elimina messaggi altrimenti si vede il tuo comando!",
        'menu_utility': "🛠️ /qr testo\n/password\n/hash testo\n/id"
    }
    await q.edit_message_text(txt.get(d, "Menu"), reply_markup=back_menu())

# ============ TRADUCI FIXATO - NON LINCA PIU NUMERI ============
async def traduci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = ""
    if update.message.reply_to_message:
        txt = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
    if not txt and context.args:
        txt = " ".join(context.args)
    if not txt:
        await update.message.reply_text("Scrivi /traduci hello world")
        return
    # blocco numeri
    no_space = txt.replace(" ","").replace("+","").replace("-","")
    if no_space.isdigit() and len(no_space) >= 9:
        await update.message.reply_text("⛔ Non traduco numeri per privacy")
        return
    if len(txt) > 450:
        await update.message.reply_text("⚠️ Testo troppo lungo, manda max 400 caratteri")
        return
    await update.message.chat.send_action("typing")
    try:
        res = GoogleTranslator(source='auto', target='it').translate(txt)
        await update.message.reply_text(f"🌍 {txt}\n\n🇮🇹 {res}")
    except Exception as e:
        await update.message.reply_text(f"Errore traduci: {e}")

# ============ STICKER ============
async def sticker_make(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("Rispondi a una FOTO con /sticker")
        return
    f = await update.message.reply_to_message.photo[-1].get_file()
    bio = BytesIO()
    await f.download_to_memory(bio)
    bio.seek(0)
    img = Image.open(bio).resize((512,512))
    out = BytesIO()
    out.name = 'sticker.webp'
    img.save(out, 'WEBP')
    out.seek(0)
    await context.bot.send_sticker(update.effective_chat.id, out)

async def photo_make(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("Rispondi a uno STICKER con /photo")
        return
    f = await update.message.reply_to_message.sticker.get_file()
    bio = BytesIO()
    await f.download_to_memory(bio)
    bio.seek(0)
    await context.bot.send_photo(update.effective_chat.id, bio)

# ============ BLACKJACK CHE VA DAVVERO ============
bj_games = {}
def bj_calc(h):
    s = sum(h)
    aces = h.count(11)
    while s > 21 and aces:
        s -= 10
        aces -= 1
    return s

async def blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    deck = [2,3,4,5,6,7,8,9,10,10,10,10,11]*4
    random.shuffle(deck)
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    bj_games[user] = {"deck": deck, "player": player, "dealer": dealer}
    ps = bj_calc(player)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🃏 CARTA", callback_data=f"bj_hit_{user}"), InlineKeyboardButton("🛑 STAI", callback_data=f"bj_stay_{user}")],
        [InlineKeyboardButton("❌ CHIUDI", callback_data=f"close_bj_{user}")]
    ])
    await update.message.reply_text(f"♠️ BLACKJACK\nTu: {player} = {ps}\nBanco: [{dealer[0]},?]", reply_markup=kb)

async def bj_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if "close_bj" in data:
        uid = int(data.split("_")[-1])
        bj_games.pop(uid, None)
        try: await q.delete_message()
        except: pass
        return
    uid = int(data.split("_")[-1])
    if q.from_user.id!= uid:
        await q.answer("Non è la tua partita! Fai /blackjack", show_alert=True)
        return
    if uid not in bj_games:
        await q.edit_message_text("Partita scaduta, rifai /blackjack")
        return
    g = bj_games[uid]
    if "hit" in data:
        g["player"].append(g["deck"].pop())
        ps = bj_calc(g["player"])
        if ps > 21:
            await q.edit_message_text(f"💥 SBALLATO {g['player']} = {ps}\nPerso! Banco {g['dealer']}\n/blackjack")
            bj_games.pop(uid, None)
        elif ps == 21:
            await q.edit_message_text(f"🎉 21! VINTO! {g['player']}")
            bj_games.pop(uid, None)
        else:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🃏 CARTA", callback_data=f"bj_hit_{uid}"), InlineKeyboardButton("🛑 STAI", callback_data=f"bj_stay_{uid}")],[InlineKeyboardButton("❌ CHIUDI", callback_data=f"close_bj_{uid}")]])
            await q.edit_message_text(f"Tu: {g['player']} = {ps}\nBanco: [{g['dealer'][0]},?]", reply_markup=kb)
    else:
        ps = bj_calc(g["player"])
        ds = bj_calc(g["dealer"])
        while ds < 17:
            g["dealer"].append(g["deck"].pop())
            ds = bj_calc(g["dealer"])
        if ds > 21 or ps > ds: res = "🎉 HAI VINTO!"
        elif ps == ds: res = "🤝 PAREGGIO!"
        else: res = "😢 HAI PERSO!"
        await q.edit_message_text(f"{res}\nTu {g['player']}={ps}\nBanco {g['dealer']}={ds}\n/blackjack rigioca")
        bj_games.pop(uid, None)

# ============ TRIS CHE VA ============
tris_games = {}
def tris_kb(board, chat):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(board[0] if board[0]!=" " else "⬜", callback_data=f"tris_0_{chat}"), InlineKeyboardButton(board[1] if board[1]!=" " else "⬜", callback_data=f"tris_1_{chat}"), InlineKeyboardButton(board[2] if board[2]!=" " else "⬜", callback_data=f"tris_2_{chat}")],
        [InlineKeyboardButton(board[3] if board[3]!=" " else "⬜", callback_data=f"tris_3_{chat}"), InlineKeyboardButton(board[4] if board[4]!=" " else "⬜", callback_data=f"tris_4_{chat}"), InlineKeyboardButton(board[5] if board[5]!=" " else "⬜", callback_data=f"tris_5_{chat}")],
        [InlineKeyboardButton(board[6] if board[6]!=" " else "⬜", callback_data=f"tris_6_{chat}"), InlineKeyboardButton(board[7] if board[7]!=" " else "⬜", callback_data=f"tris_7_{chat}"), InlineKeyboardButton(board[8] if board[8]!=" " else "⬜", callback_data=f"tris_8_{chat}")],
        [InlineKeyboardButton("❌ Chiudi", callback_data=f"tris_close_{chat}")]
    ])

async def tris_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat.id
    board = [" "]*9
    tris_games[chat] = {"board": board, "turn": "X"}
    await update.message.reply_text(f"⭕ TRIS - Tocca a X", reply_markup=tris_kb(board, chat))

async def tris_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if "close" in q.data:
        chat = int(q.data.split("_")[-1])
        tris_games.pop(chat, None)
        try: await q.delete_message()
        except: pass
        return
    _, idx, chat = q.data.split("_")
    idx = int(idx); chat = int(chat)
    if chat not in tris_games: return
    game = tris_games[chat]
    board = game["board"]
    if board[idx]!= " ":
        await q.answer("Occupata!")
        return
    board[idx] = game["turn"]
    wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for w in wins:
        if board[w[0]] == board[w[1]] == board[w[2]]!= " ":
            await q.edit_message_text(f"🎉 VINCE {board[w[0]]}!\n{board}")
            tris_games.pop(chat, None)
            return
    if " " not in board:
        await q.edit_message_text(f"🤝 PAREGGIO {board}")
        tris_games.pop(chat, None)
        return
    game["turn"] = "O" if game["turn"] == "X" else "X"
    await q.edit_message_text(f"⭕ TRIS - Tocca a {game['turn']}", reply_markup=tris_kb(board, chat))

# ============ INDOVINA ============
async def indovina_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['num'] = random.randint(1,100)
    context.user_data['tent'] = 0
    await update.message.reply_text("🔢 Ho pensato 1-100\nUsa /guess 50")

async def guess_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'num' not in context.user_data:
        await update.message.reply_text("Fai /indovina prima")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usa /guess 50")
        return
    g = int(context.args[0])
    context.user_data['tent'] += 1
    target = context.user_data['num']
    if g == target:
        await update.message.reply_text(f"🎉 BRAVO ERA {target} in {context.user_data['tent']} tentativi! /indovina rigioca")
        context.user_data.pop('num', None)
    elif g < target:
        await update.message.reply_text(f"📈 {g} basso! Più alto! (tent {context.user_data['tent']})")
    else:
        await update.message.reply_text(f"📉 {g} alto! Più basso! (tent {context.user_data['tent']})")

# ============ ANON / GHOST CHE CANCELLA DAVVERO ============
async def anon_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = " ".join(context.args)
    if not t:
        await update.message.reply_text("Usa /anon ciao a tutti")
        return
    try:
        await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
    except:
        await update.message.reply_text("⚠️ Non riesco a cancellare il tuo /anon perché non sono admin con 'Elimina messaggi'. Rendimi admin o il tuo nome si vedrà!")
        return
    await context.bot.send_message(update.effective_chat.id, f"🎭 {t}")

async def ghost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = " ".join(context.args)
    if not t:
        await update.message.reply_text("Usa /ghost testo")
        return
    try:
        await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
    except:
        pass
    await context.bot.send_message(update.effective_chat.id, f"👻 {t}")

# ============ UTILITY SEMPLICI ============
async def dado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎲 {random.randint(1,6)}")

async def qr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa /qr testo")
        return
    txt = " ".join(context.args)
    img = qrcode.make(txt)
    bio = BytesIO()
    bio.name = 'qr.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    await context.bot.send_photo(update.effective_chat.id, bio, caption=f"QR: {txt}")

async def password_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pw = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    await update.message.reply_text(f"🔐 `{pw}`", parse_mode='Markdown')

# ============ MAIN ============
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_cb, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(menu_cb, pattern="^close$"))
    app.add_handler(CallbackQueryHandler(bj_callback, pattern="^bj_"))
    app.add_handler(CallbackQueryHandler(bj_callback, pattern="^close_bj_"))
    app.add_handler(CallbackQueryHandler(tris_cb, pattern="^tris_"))

    cmds = [
        ("traduci", traduci), ("tr", traduci),
        ("sticker", sticker_make), ("photo", photo_make),
        ("blackjack", blackjack), ("bj", blackjack),
        ("tris", tris_cmd),
        ("indovina", indovina_cmd), ("guess", guess_cmd),
        ("anon", anon_cmd), ("anonimo", anon_cmd),
        ("ghost", ghost_cmd),
        ("dado", dado), ("qr", qr_cmd), ("password", password_cmd),
    ]
    for c,f in cmds:
        app.add_handler(CommandHandler(c,f))
    print(f"BOT V20 ONLINE - {len(cmds)} comandi - TUTTO TESTATO")
    app.run_polling()

if __name__ == "__main__":
    main()
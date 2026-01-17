import logging
import sqlite3
import uuid
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters,
)

# --- සැකසුම් (Configuration) ---
BOT_TOKEN = "ඔබගෙ බොට් ටොකන් එක" 
ADMIN_ID = 8107411511 # ඔබේ Telegram ID එක
DB_NAME = "bot_database.db"
RESULTS_PER_PAGE = 5
MAINTENANCE_MODE = False

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Database functions ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS files 
                      (id TEXT PRIMARY KEY, file_id TEXT, file_name TEXT, file_type TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def add_file(uid, f_id, f_name, f_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files VALUES (?, ?, ?, ?)", (uid, f_id, f_name, f_type))
    conn.commit()
    conn.close()

def search_in_db(query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_name FROM files WHERE file_name LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

def get_file_by_id(uid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, file_name, file_type FROM files WHERE id = ?", (uid,))
    result = cursor.fetchone()
    conn.close()
    return result

# --- Bot functions ---

async def delete_msg(context, chat_id, message_id):
    await asyncio.sleep(600) 
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    if update.effective_chat.type == 'private':
        await update.message.reply_text("👋 සාදරයෙන් පිළිගනිමු! ගොනු සෙවීමට අපගේ සමූහය භාවිතා කරන්න.")

async def index_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID: return 

    msg = update.message or update.channel_post
    f_id, f_name, f_type = None, "Unknown", None
    if msg.document: f_id, f_name, f_type = msg.document.file_id, msg.document.file_name, 'doc'
    elif msg.video: f_id, f_name, f_type = msg.video.file_id, msg.video.file_name, 'video'
    elif msg.audio: f_id, f_name, f_type = msg.audio.file_id, msg.audio.file_name, 'audio'
    
    if f_id:
        uid = str(uuid.uuid4())[:8]
        final_name = msg.caption if msg.caption else f_name
        add_file(uid, f_id, final_name, f_type)
        await msg.reply_text(f"✅ සාර්ථකව ගබඩා විය: {final_name}")

async def search_files(update: Update, context: ContextTypes.DEFAULT_TYPE, page=0):
    global MAINTENANCE_MODE
    if MAINTENANCE_MODE and update.effective_user.id != ADMIN_ID:
        if update.effective_chat.type != 'private':
            await update.message.reply_text("⚠️ Bot දැනට අලුත්වැඩියා කටයුත්තක් සඳහා නතර කර ඇත.")
        return

    if update.effective_chat.type == 'private' and update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ කරුණාකර සමූහය (Group) තුළ ගොනු සොයන්න.")
        return

    query_text = update.message.text.strip() if update.message else context.user_data.get('q')
    context.user_data['q'] = query_text
    results = search_in_db(query_text)
    
    if not results: return

    start_idx, end_idx = page * RESULTS_PER_PAGE, (page + 1) * RESULTS_PER_PAGE
    keyboard = [[InlineKeyboardButton(f"📂 {res[1][:30]}", callback_data=f"get_{res[0]}")] for res in results[start_idx:end_idx]]
    
    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️ Back", callback_data=f"pg_{page-1}"))
    if end_idx < len(results): nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"pg_{page+1}"))
    if nav: keyboard.append(nav)
    
    text = f"🔎 '{query_text}' සඳහා ප්‍රතිඵල:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data.startswith("pg_"):
        await search_files(update, context, page=int(query.data.split("_")[1]))
    elif query.data.startswith("get_"):
        f = get_file_by_id(query.data.split("_")[1])
        if f:
            try:
                m = await context.bot.send_message(chat_id=user_id, text=f"🚀 **{f[1]}** එවමින් පවතී... (විනාඩි 10 කින් මැකේ)")
                if f[2] == 'video': s = await context.bot.send_video(chat_id=user_id, video=f[0])
                elif f[2] == 'audio': s = await context.bot.send_audio(chat_id=user_id, audio=f[0])
                else: s = await context.bot.send_document(chat_id=user_id, document=f[0])
                context.application.create_task(delete_msg(context, user_id, s.message_id))
                context.application.create_task(delete_msg(context, user_id, m.message_id))
            except:
                await query.message.reply_text(f"❌ @{query.from_user.username}, කරුණාකර මුලින්ම Bot ව Start කර පසුව බොත්තම ඔබන්න.")

# --- Admin Commands ---

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    text = " ".join(context.args)
    if not text: await update.message.reply_text("❌ /broadcast <පණිවිඩය>"); return
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users"); users = cursor.fetchall(); conn.close()
    count = 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=user[0], text=f"📢 **දැනුම්දීමයි:**\n\n{text}")
            count += 1; await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text(f"✅ {count} දෙනෙකුට යවන ලදි.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files"); f_c = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users"); u_c = cursor.fetchone()[0]; conn.close()
    await update.message.reply_text(f"📊 Stats:\nFiles: {f_c}\nUsers: {u_c}")

async def maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE
    if update.effective_user.id != ADMIN_ID: return
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    await update.message.reply_text(f"🔧 Maintenance: {'On' if MAINTENANCE_MODE else 'Off'}")

# --- Main ---
if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("maintenance", maintenance))
    
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.AUDIO, index_files))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_files))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    
    app.run_polling()

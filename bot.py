import telebot
from telebot import types
import time

BOT_TOKEN = "8136102305:AAEZAdYZ0JU015UmUIBdCFNj51knjNyixeE"
OWNER_ID = 1821873324

bot = telebot.TeleBot(BOT_TOKEN)
allowed_users = set([OWNER_ID])
admins = set([OWNER_ID])
report_accounts = []
report_delay = 10
reports_count = 0
report_reasons = {
    "porn": "إباحية",
    "violence": "عنف",
    "spam": "سبام",
    "other": "أخرى"
}
user_report_state = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, "البوت غير مفعل لديك راسل هنا حتى يتم تفعيله @isabos")
        return
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("أرسل تبليغ"),
               types.KeyboardButton("عدد التبليغات"),
               types.KeyboardButton("إدارة الحسابات"),
               types.KeyboardButton("تحديد وقت البلاغ"),
               types.KeyboardButton("طلب مساعدة"))
    bot.send_message(message.chat.id, "أهلاً بك في بوت التبليغات", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in allowed_users:
        bot.reply_to(message, "البوت غير مفعل لديك راسل هنا حتى يتم تفعيله @isabos")
        return

    if text == "أرسل تبليغ":
        if not report_accounts:
            bot.send_message(message.chat.id, "لا يوجد حسابات لإرسال البلاغات.")
            return
        markup = types.InlineKeyboardMarkup()
        for key, val in report_reasons.items():
            markup.add(types.InlineKeyboardButton(val, callback_data=f"report_{key}"))
        bot.send_message(message.chat.id, "اختر سبب التبليغ:", reply_markup=markup)

    elif text == "عدد التبليغات":
        bot.send_message(message.chat.id, f"عدد البلاغات المرسلة: {reports_count}")

    elif text == "إدارة الحسابات":
        if user_id not in admins:
            bot.send_message(message.chat.id, "هذا الخيار للأدمن فقط.")
            return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("إضافة حساب", callback_data="add_account"))
        markup.add(types.InlineKeyboardButton("حذف حساب", callback_data="remove_account"))
        bot.send_message(message.chat.id, "اختر العملية:", reply_markup=markup)

    elif text == "تحديد وقت البلاغ":
        if user_id not in admins:
            bot.send_message(message.chat.id, "هذا الخيار للأدمن فقط.")
            return
        bot.send_message(message.chat.id, f"الوقت الحالي بين البلاغات: {report_delay} ثانية
أرسل الوقت الجديد:")
        user_report_state[user_id] = {"action": "set_delay"}

    elif text == "طلب مساعدة":
        bot.send_message(message.chat.id, "للمساعدة راسل @isabos")

    else:
        if user_id in user_report_state:
            state = user_report_state[user_id]
            action = state.get("action")
            if action == "set_delay":
                try:
                    new_delay = int(text)
                    global report_delay
                    report_delay = new_delay
                    bot.send_message(message.chat.id, f"تم تعيين الوقت: {new_delay} ثانية.")
                except:
                    bot.send_message(message.chat.id, "يرجى إرسال رقم صحيح.")
                user_report_state.pop(user_id)
            elif action == "await_report_text":
                reason = state.get("reason")
                send_report(reason, text.strip())
                user_report_state.pop(user_id)
            elif action == "await_add_account":
                acc = text.strip()
                if acc not in report_accounts:
                    report_accounts.append(acc)
                    bot.send_message(message.chat.id, f"تمت إضافة الحساب: {acc}")
                else:
                    bot.send_message(message.chat.id, "الحساب موجود مسبقاً.")
                user_report_state.pop(user_id)
            elif action == "await_remove_account":
                acc = text.strip()
                if acc in report_accounts:
                    report_accounts.remove(acc)
                    bot.send_message(message.chat.id, f"تم حذف الحساب: {acc}")
                else:
                    bot.send_message(message.chat.id, "الحساب غير موجود.")
                user_report_state.pop(user_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.from_user.id
    data = call.data

    if user_id not in allowed_users:
        bot.answer_callback_query(call.id, "غير مصرح لك", show_alert=True)
        return

    if data.startswith("report_"):
        reason = data.split("_")[1]
        user_report_state[user_id] = {"action": "await_report_text", "reason": reason}
        bot.send_message(user_id, "أرسل نص التبليغ:")
    elif data == "add_account":
        user_report_state[user_id] = {"action": "await_add_account"}
        bot.send_message(user_id, "أرسل اسم الحساب:")
    elif data == "remove_account":
        user_report_state[user_id] = {"action": "await_remove_account"}
        bot.send_message(user_id, "أرسل الحساب المطلوب حذفه:")

def send_report(reason_key, report_text):
    global reports_count
    for acc in report_accounts:
        try:
            bot.send_message(OWNER_ID, f"من {acc} | سبب: {report_reasons.get(reason_key)}
{report_text}")
            time.sleep(report_delay)
            reports_count += 1
        except Exception as e:
            bot.send_message(OWNER_ID, f"خطأ من {acc}: {e}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google import genai
import Secrets


# Cliente de Gemini
client = genai.Client(api_key=Secrets.APIKEY)

threadsList = []
class Threads:
    def __init__(self, id):
        self.id = id
        self.chats = []
        threadsList.append(self)

    def sizeControler(self):
        if len(self.chats) > 1020:
            del self.chats[:20]

    def addChat(self,user,text):
        self.chats.append((user,text))

    

async def save(update, context):
    if update.message and update.message.text:
        chatId=update.message.chat_id
        exist=False
        #Si no existe el hilo lo crea y después guarda el mensaje
        for thread in threadsList:
            if chatId == thread.id:
                exist=True
                thread.addChat(update.message.from_user.full_name,update.message.text)
                thread.sizeControler()

        if exist == False:
            newThread=Threads(chatId)
            newThread.addChat(update.message.from_user.full_name,update.message.text)

        

async def test(update, context):
    await update.message.reply_text("Test funcionando ✅")

#Limpia el texto antes de mandarlo a Gemini, quita el nombre de usaurio si se repite y signos simbolos
def cleanUsers(chat):
    user=chat[0][0]
    text=f"{user}: "
    for i in range(len(chat)):
        if chat[i][0] == user:
            text += " " + chat[i][1]
        else:
            text += "\n" + chat[i][0] + ": " + chat[i][1]
            user= chat[i][0]
    return text

# Generar resumen con Gemini
async def recap(update, context):
    nChats = int(context.args[0]) if context.args else 20
    for thread in threadsList:
        if thread.id == update.message.chat_id:
       
            model = genai.GenerativeModel("gemini-2.5-flash")

            # Generar contenido
            response = model.generate_content("Quiero evitar leer todos estos chats, resumelos muy brevemente: "+cleanUsers(thread.chats[-nChats:]))
                
            await update.message.reply_text(response.text)
    

def main():
    app = Application.builder().token(Secrets.TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save))
    app.add_handler(CommandHandler("recap", recap))
    app.add_handler(CommandHandler("test", test))

    print("Bot iniciado")
    app.run_polling()

if __name__ == "__main__":
    main()
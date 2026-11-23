# AKIRKY KAT - TOLUK BOT (1-kod + Render WEB fix)
# Un, subtitr, montaj, 10 seriya - baary bir file'da
import os, threading, asyncio, textwrap
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- RENDER UCHUN WEB SERVER (bekir Web Service ochup kalbasyn) ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("Akirky Kat Bot ishтеп жатат!".encode("utf-8"))
    def log_message(self, *a):
        pass

def start_web():
    try:
        port = int(os.environ.get("PORT", 10000))
        HTTPServer(("0.0.0.0", port), Handler).serve_forever()
    except Exception as e:
        print("web error:", e)

threading.Thread(target=start_web, daemon=True).start()
print("Web server started")

# --- BOT ---
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, BufferedInputFile

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("BOT_TOKEN jok! Render Environment'ge salysh kerek")
    while True:
        asyncio.run(asyncio.sleep(3600))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 10 SERIYA - AKIRKY KAT
EPISODES = {
1: ("1-серия: Табылган кат", "Айдай апасынын эски сандыгынан ачылбаган кат табат. Кат 20 жыл мурун жазылган. Анын ичинде бир гана сап бар: 'Мени кечир, мен кайтып келем'. Айдайдын колу титирейт. Ким жазган бул катты? Эмне учун апасы аны жашырган?"),
2: ("2-серия: Жоголгон адам", "Каттагы ат - 20 жыл мурун жоголгон адамдыкы. Айылдагылар ал жонундо суйлоодон коркушат. Айдай чон атасынан сурайт, бирок ал унчукпай калат. Сыры бар экени билинип турат."),
3: ("3-серия: Унчукпаган айыл", "Айдай кошуналардан сураштыра баштайт. Баары 'билбейм' дешет, бирок коздору качып турат. Тункусу Айдайдын эшигинин алдына бир оо эски сурот коюлуп кетет."),
4: ("4-серия: Тунку конок", "Тунку саат 3то эшик тыкылдайт. Айдай коркуп эшикти ачат - эч ким жок. Болгону жерде дагы бир кат жатат. 'Эртен кечинде эски копурого кел. Жалгыз кел.'"),
5: ("5-серия: Чындык ачылат", "Айдай копурого барат. Ал жерде аны бала кезиндеги досу Нурлан кутуп турат. Ал: 'Сенин атан тируу. Ал сени 20 жылдан бери издеп журот' - дейт."),
6: ("6-серия: Эски сурот", "Нурлан эски сурот корсотет. Андагы адам Айдайга абдан окшош. Бул анын атасы экени аныкталат. Апасы эмне учун аны атасы олду деп айткан?"),
7: ("7-серия: Шаарга сапар", "Айдай чындыкты билуу учун шаарга кетет. Ал жерде атасынын иштеген жерин табат. Бирок ал жерде аны башка аял тосуп алат - 'Сен кимсин?' деп сурайт."),
8: ("8-серия: Экинчи бет", "Акыркы каттын экинчи бети табылды. Анда бүт чындык жазылган: апасы Айдайды коргоо учун аны алыстатып жиберген. Атасы жаман адам эмес, жагдай курмандыгы болгон."),
9: ("9-серия: Чечим", "Айдай атасы менен жолугат. 20 жылдык сагыныч, ый, суроолор... Атасы: 'Мени кечире аласынбы?' деп сурайт. Айдай эмне деп жооп берет?"),
10: ("10-серия: ФИНАЛ - Акыркы кат", "Баары чечилди. Айдай атасын кечирет. Уй-було кайра биригет. Бирок акыркы сапта дагы бир сыр бар: сандыкта дагы бир ачылбаган кат бар экен... 2-СЕЗОН БОЛОБУ?"),
}

def make_kb():
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    row = []
    for i in range(1, 11):
        row.append(types.InlineKeyboardButton(text=f"{i}-серия", callback_data=f"ep_{i}"))
        if len(row) == 2:
            kb.inline_keyboard.append(row); row = []
    if row: kb.inline_keyboard.append(row)
    return kb

def make_cover(ep_num, title):
    """Suröt jaso - Pillow menen"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (1080, 1920), (20, 20, 35))
        d = ImageDraw.Draw(img)
        # fon
        for y in range(0, 1920, 4):
            d.line([(0, y), (1080, y)], fill=(20+ y//80, 20, 35+ y//60))
        d.rectangle([60, 500, 1020, 1250], outline=(255, 180, 0), width=6)
        d.text((90, 560), "AKIRKY KAT", fill=(255, 180, 0))
        d.text((90, 680), f"{ep_num}-SERIYA", fill=(255, 255, 255))
        wrapped = textwrap.wrap(title, width=22)
        yy = 820
        for line in wrapped:
            d.text((90, yy), line, fill=(255, 255, 255)); yy += 90
        d.text((90, 1150), "YouTube Shorts | Drama", fill=(180, 180, 180))
        path = f"/tmp/cover_{ep_num}.jpg"
        img.save(path)
        return path
    except Exception as e:
        print("cover error", e); return None

def make_srt(ep_num, text):
    """Subtitr .srt format"""
    lines = textwrap.wrap(text, width=40)
    srt = ""
    t = 0
    for i, line in enumerate(lines[:8]):
        srt += f"{i+1}\n00:00:{t:02d},000 --> 00:00:{t+2:02d},000\n{line}\n\n"
        t += 2
    path = f"/tmp/sub_{ep_num}.srt"
    open(path, "w", encoding="utf-8").write(srt)
    return path

async def make_voice(ep_num, text):
    """Un - edge-tts menen, bolboso otskorup ketet"""
    try:
        import edge_tts
        path = f"/tmp/voice_{ep_num}.mp3"
        communicate = edge_tts.Communicate(text[:900], "ky-KG-AigulNeural")
        await communicate.save(path)
        return path
    except Exception as e:
        print("voice error", e); return None

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Салам! 👋 Мен **Акыркы Кат** ботумун.\n\n🎬 10 серия - драма\n🎙️ Үн + субтитр + монтаж\n\nСерия танда 👇", reply_markup=make_kb(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("ep_"))
async def show_ep(c: types.CallbackQuery):
    n = int(c.data.split("_")[1])
    title, text = EPISODES.get(n, ("?", "?"))
    await c.answer("Даярдалып жатат...")
    full = f"🎬 АКЫРКЫ КАТ | {title}\n\n{text}\n\n---\nКийинки серияны басып улант 👇"
    # 1. Surot
    cover = make_cover(n, title)
    if cover:
        await c.message.answer_photo(FSInputFile(cover), caption=full, reply_markup=make_kb())
    else:
        await c.message.answer(full, reply_markup=make_kb())
    # 2. Un
    voice = await make_voice(n, text)
    if voice:
        await c.message.answer_voice(FSInputFile(voice), caption=f"🎙️ {title} - үнү")
    # 3. Subtitr
    srt = make_srt(n, text)
    await c.message.answer_document(FSInputFile(srt), caption=f"📝 {title} - субтитр (.srt) - Montaj учун")

@dp.message(Command("help"))
async def help_cmd(m: types.Message):
    await m.answer("/start - баштоо\nСерияны танда - үн + сүрөт + субтитр келет")

async def main():
    print("Akirky Kat Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

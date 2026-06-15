import os
import re
import math
import asyncio
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ATOMIC_MASS = {
    "H": 1.008,
    "He": 4.003,
    "Li": 6.94,
    "Be": 9.012,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "Na": 22.990,
    "Mg": 24.305,
    "Al": 26.982,
    "Si": 28.085,
    "P": 30.974,
    "S": 32.06,
    "Cl": 35.45,
    "K": 39.098,
    "Ca": 40.078,
    "Fe": 55.845,
    "Cu": 63.546,
    "Zn": 65.38,
    "Ag": 107.868,
    "I": 126.904,
    "Ba": 137.327,
    "Au": 196.967
}


def molar_mass(formula: str) -> float:
    pattern = r'([A-Z][a-z]?)(\d*)'
    matches = re.findall(pattern, formula)

    if not matches:
        raise ValueError("Invalid chemical formula")

    mass = 0.0
    for element, count in matches:
        if element not in ATOMIC_MASS:
            raise ValueError(f"Unknown element: {element}")
        count = int(count) if count else 1
        mass += ATOMIC_MASS[element] * count

    return round(mass, 3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧪 ChemBot\n\n"
        "Available Commands:\n"
        "/mw H2SO4\n"
        "/ph 0.001\n"
        "/molarity 5 40 250\n"
        "/dilute 1 100 0.1\n"
        "/percent 10 250\n"
        "/help"
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧪 ChemBot Commands\n\n"
        "1) Molecular Weight\n"
        "/mw H2SO4\n\n"
        "2) pH\n"
        "/ph 0.001\n\n"
        "3) Molarity\n"
        "/molarity mass_g molar_mass_gmol volume_ml\n"
        "Example: /molarity 5 40 250\n\n"
        "4) Dilution\n"
        "/dilute M1 V1 M2\n"
        "Example: /dilute 1 100 0.1\n\n"
        "5) Percent Solution\n"
        "/percent grams volume_ml"
    )
    await update.message.reply_text(text)


async def mw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Usage: /mw H2SO4")
            return

        formula = context.args[0].strip()
        result = molar_mass(formula)

        await update.message.reply_text(
            f"🧪 Compound: {formula}\n\n⚖️ Molar Mass = {result} g/mol"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def ph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Usage: /ph 0.001")
            return

        h = float(context.args[0])
        if h <= 0:
            raise ValueError("Concentration must be greater than 0")

        result = -math.log10(h)
        await update.message.reply_text(f"🧪 pH = {round(result, 3)}")
    except Exception:
        await update.message.reply_text("Usage: /ph 0.001")


async def molarity_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 3:
            await update.message.reply_text("Usage: /molarity 5 40 250")
            return

        mass = float(context.args[0])          # grams
        molar_mass_value = float(context.args[1])  # g/mol
        volume_ml = float(context.args[2])     # mL

        if molar_mass_value <= 0 or volume_ml <= 0:
            raise ValueError("Molar mass and volume must be greater than 0")

        moles = mass / molar_mass_value
        volume_l = volume_ml / 1000
        M = moles / volume_l

        await update.message.reply_text(f"🧪 Molarity = {round(M, 4)} M")
    except Exception:
        await update.message.reply_text("Usage: /molarity 5 40 250")


async def dilute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 3:
            await update.message.reply_text("Usage: /dilute 1 100 0.1")
            return

        M1 = float(context.args[0])
        V1 = float(context.args[1])
        M2 = float(context.args[2])

        if M2 <= 0:
            raise ValueError("Final molarity must be greater than 0")

        V2 = (M1 * V1) / M2
        await update.message.reply_text(f"🧪 Final Volume = {round(V2, 3)} mL")
    except Exception:
        await update.message.reply_text("Usage: /dilute 1 100 0.1")


async def percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /percent 10 250")
            return

        grams = float(context.args[0])
        volume = float(context.args[1])

        if volume <= 0:
            raise ValueError("Volume must be greater than 0")

        result = (grams / volume) * 100
        await update.message.reply_text(f"🧪 Percent Solution = {round(result, 3)} % (w/v)")
    except Exception:
        await update.message.reply_text("Usage: /percent 10 250")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Add it in Render environment variables.")

    # Safe for Python 3.14 too
    asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mw", mw))
    app.add_handler(CommandHandler("ph", ph))
    app.add_handler(CommandHandler("molarity", molarity_cmd))
    app.add_handler(CommandHandler("dilute", dilute))
    app.add_handler(CommandHandler("percent", percent))

    print("ChemBot Running...")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()

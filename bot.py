import os
import re
import math
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Atomic masses
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


def molar_mass(formula):
    pattern = r'([A-Z][a-z]?)(\d*)'
    matches = re.findall(pattern, formula)

    mass = 0

    for element, count in matches:
        if element not in ATOMIC_MASS:
            raise ValueError(f"Unknown element: {element}")

        count = int(count) if count else 1
        mass += ATOMIC_MASS[element] * count

    return round(mass, 3)


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🧪 ChemBot

Available Commands:

/mw H2SO4
/ph 0.001
/molarity 5 40 250
/dilute 1 100 0.1
/percent 10 250
/help
"""
    await update.message.reply_text(text)


# HELP
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🧪 Commands

1. Molecular Weight
/mw H2SO4

2. pH
/ph 0.001

3. Molarity
/molarity mass(g) molarmass volume(mL)

Example:
/molarity 5 40 250

4. Dilution
/dilute M1 V1 M2

Example:
/dilute 1 100 0.1

5. Percent Solution
/percent grams volume_ml
"""
    await update.message.reply_text(text)


# MOLECULAR WEIGHT
async def mw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        formula = context.args[0]
        result = molar_mass(formula)

        await update.message.reply_text(
            f"🧪 Compound: {formula}\n\n⚖️ Molar Mass = {result} g/mol"
        )

    except Exception as e:
        await update.message.reply_text(
            f"Error: {str(e)}"
        )


# PH
async def ph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        h = float(context.args[0])

        if h <= 0:
            raise ValueError("Concentration must be > 0")

        result = -math.log10(h)

        await update.message.reply_text(
            f"🧪 pH = {round(result,3)}"
        )

    except Exception:
        await update.message.reply_text(
            "Usage:\n/ph 0.001"
        )


# MOLARITY
async def molarity_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mass = float(context.args[0])
        molar_mass_value = float(context.args[1])
        volume_ml = float(context.args[2])

        moles = mass / molar_mass_value
        volume_l = volume_ml / 1000

        M = moles / volume_l

        await update.message.reply_text(
            f"🧪 Molarity = {round(M,4)} M"
        )

    except Exception:
        await update.message.reply_text(
            "Usage:\n/molarity 5 40 250"
        )


# DILUTION
async def dilute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        M1 = float(context.args[0])
        V1 = float(context.args[1])
        M2 = float(context.args[2])

        V2 = (M1 * V1) / M2

        await update.message.reply_text(
            f"🧪 Final Volume = {round(V2,3)} mL"
        )

    except Exception:
        await update.message.reply_text(
            "Usage:\n/dilute 1 100 0.1"
        )


# PERCENT
async def percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        grams = float(context.args[0])
        volume = float(context.args[1])

        result = (grams / volume) * 100

        await update.message.reply_text(
            f"🧪 Percent Solution = {round(result,3)} % (w/v)"
        )

    except Exception:
        await update.message.reply_text(
            "Usage:\n/percent 10 250"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mw", mw))
    app.add_handler(CommandHandler("ph", ph))
    app.add_handler(CommandHandler("molarity", molarity_cmd))
    app.add_handler(CommandHandler("dilute", dilute))
    app.add_handler(CommandHandler("percent", percent))

    print("ChemBot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()

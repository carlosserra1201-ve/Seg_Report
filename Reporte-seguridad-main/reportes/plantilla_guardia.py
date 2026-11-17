import urllib.parse
from datetime import datetime
import zoneinfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# Estados de la conversación
(
    TIPO_GUARDIA,
    CANT_TITULARES, NOMBRES_TITULARES,
    CANT_ESPECIALES, NOMBRES_ESPECIALES,
    TIENE_LIBRES, CANT_LIBRES, NOMBRES_LIBRES,
    TIENE_AUSENTES, CANT_AUSENTES, NOMBRES_AUSENTES,
    TIENE_VACACIONES, CANT_VACACIONES, NOMBRES_VACACIONES,
    TIENE_PERMISOS, CANT_PERMISOS, NOMBRES_PERMISOS,
    COORD_JDML, POS_TRANSPORTE_JDML, POS_PROVEEDORES_JDML, POS_QUINTA_JDML, POS_PISO2_JDML, POS_CTRL_PCM_JDML, POS_CTRL_CORTIJOS_JDML,
    POS_PISO4_CSP, POS_EMERGENCIA_CSP, POS_REVISION_CSP, POS_SOTANO5_CSP,
    NOVEDADES
) = range(29)

DÍAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

def obtener_saludo_y_fecha():
    tz = zoneinfo.ZoneInfo("America/Caracas")
    ahora = datetime.now(tz)
    hora = ahora.hour

    if 5 <= hora < 12:
        saludo = "*Buenos días.*"
    elif 12 <= hora < 19:
        saludo = "*Buenas tardes.*"
    else:
        saludo = "*Buenas noches.*"
    
    dia_nombre = DÍAS[ahora.weekday()]
    mes_nombre = MESES[ahora.month - 1]
    fecha_str = f"*{dia_nombre}, {ahora.day} de {mes_nombre}*"
    return saludo, fecha_str, ahora.weekday()

# --- INICIO Y TIPO DE GUARDIA ---

async def iniciar_plantilla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.message if update.message else update.callback_query.message
    if update.callback_query:
        await update.callback_query.answer()

    # Limpiar datos previos
    context.user_data['titulares'] = []
    context.user_data['especiales'] = []
    context.user_data['libres'] = []
    context.user_data['ausentes'] = []
    context.user_data['vacaciones'] = []
    context.user_data['permisos'] = []

    keyboard = [
        [InlineKeyboardButton("☀️ Diurna", callback_data="guardia_Diurna")],
        [InlineKeyboardButton("🌙 Nocturna", callback_data="guardia_Nocturna")]
    ]
    await msg_obj.reply_text(
        "*REPORTE DE PLANTILLA*\n\nSeleccione el tipo de guardia:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return TIPO_GUARDIA

async def seleccionar_tipo_guardia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tipo = query.data.replace("guardia_", "")
    context.user_data['tipo_guardia'] = tipo

    await query.message.reply_text(
        f"🛡️ *Seguridad Interna PCM* ({tipo})\n"
        "Indique la *cantidad de Operadores Titulares* presentes en la guardia (en números):",
        parse_mode="Markdown"
    )
    return CANT_TITULARES

# --- 1. SEGURIDAD INTERNA PCM ---

async def recibir_cant_titulares(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if not texto.isdigit():
        await update.message.reply_text("Por favor, ingrese un número válido:")
        return CANT_TITULARES
    
    cant = int(texto)
    context.user_data['cant_titulares'] = cant
    if cant == 0:
        return await pedir_cant_especiales(update)
    
    context.user_data['idx_titular'] = 1
    await update.message.reply_text("Escriba el Nombre y Apellido del *Titular 1*:", parse_mode="Markdown")
    return NOMBRES_TITULARES

async def recibir_nombre_titular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text.strip()
    context.user_data['titulares'].append(nombre)
    idx = context.user_data['idx_titular'] + 1
    
    if idx <= context.user_data['cant_titulares']:
        context.user_data['idx_titular'] = idx
        await update.message.reply_text(f"Escriba el Nombre y Apellido del *Titular {idx}*:", parse_mode="Markdown")
        return NOMBRES_TITULARES
    else:
        return await pedir_cant_especiales(update)

async def pedir_cant_especiales(update: Update):
    msg_obj = update.message if update.message else update.callback_query.message
    await msg_obj.reply_text("Indique la *cantidad de personal en Guardias Especiales* (en números):", parse_mode="Markdown")
    return CANT_ESPECIALES

async def recibir_cant_especiales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if not texto.isdigit():
        await update.message.reply_text("Por favor, ingrese un número válido:")
        return CANT_ESPECIALES
    
    cant = int(texto)
    context.user_data['cant_especiales'] = cant
    if cant == 0:
        return await preguntar_libres(update)
    
    context.user_data['idx_especial'] = 1
    await update.message.reply_text("Escriba el Nombre y Apellido de la *Guardia Especial 1*:", parse_mode="Markdown")
    return NOMBRES_ESPECIALES

async def recibir_nombre_especial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text.strip()
    context.user_data['especiales'].append(nombre)
    idx = context.user_data['idx_especial'] + 1
    
    if idx <= context.user_data['cant_especiales']:
        context.user_data['idx_especial'] = idx
        await update.message.reply_text(f"Escriba el Nombre y Apellido de la *Guardia Especial {idx}*:", parse_mode="Markdown")
        return NOMBRES_ESPECIALES
    else:
        return await preguntar_libres(update)

# --- LIBRES ---

async def preguntar_libres(update: Update):
    msg_obj = update.message if update.message else update.callback_query.message
    keyboard = [
        [InlineKeyboardButton("Sí", callback_data="libres_si")],
        [InlineKeyboardButton("No", callback_data="libres_no")]
    ]
    await msg_obj.reply_text("¿Hay *personal Libre*?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return TIENE_LIBRES

async def respuesta_tiene_libres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "libres_si":
        await query.message.reply_text("Indique la *cantidad de personal Libre* (en números):", parse_mode="Markdown")
        return CANT_LIBRES
    else:
        return await preguntar_ausentes(query.message)

async def recibir_cant_libres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if not texto.isdigit() or int(texto) <= 0:
        await update.message.reply_text("Por favor, ingrese un número mayor a 0:")
        return CANT_LIBRES
    
    context.user_data['cant_libres'] = int(texto)
    context.user_data['idx_libre'] = 1
    await update.message.reply_text("Escriba el Nombre y Apellido del *Personal Libre 1*:", parse_mode="Markdown")
    return NOMBRES_LIBRES

async def recibir_nombre_libre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text.strip()
    context.user_data['libres'].append(nombre)
    idx = context.user_data['idx_libre'] + 1
    
    if idx <= context.user_data['cant_libres']:
        context.user_data['idx_libre'] = idx
        await update.message.reply_text(f"Escriba el Nombre y Apellido del *Personal Libre {idx}*:", parse_mode="Markdown")
        return NOMBRES_LIBRES
    else:
        return await preguntar_ausentes(update.message)

# --- AUSENTES ---

async def preguntar_ausentes(message):
    keyboard = [
        [InlineKeyboardButton("Sí", callback_data="aus_si")],
        [InlineKeyboardButton("No", callback_data="aus_no")]
    ]
    await message.reply_text("¿Hay *personal Ausente*?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return TIENE_AUSENTES

async def respuesta_tiene_ausentes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "aus_si":
        await query.message.reply_text("Indique la *cantidad de personal Ausente* (en números):", parse_mode="Markdown")
        return CANT_AUSENTES
    else:
        return await preguntar_vacaciones(query.message)

async def recibir_cant_ausentes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if not texto.isdigit() or int(texto) <= 0:
        await update.message.reply_text("Por favor, ingrese un número mayor a 0:")
        return CANT_AUSENTES
    
    context.user_data['cant_ausentes'] = int(texto)
    context.user_data['idx_ausente'] = 1
    await update.message.reply_text("Escriba el Nombre y Apellido del *Personal Ausente 1*:", parse_mode="Markdown")
    return NOMBRES_AUSENTES

async def recibir_nombre_ausente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text.strip()
    context.user_data['ausentes'].append(nombre)
    idx = context.user_data['idx_ausente'] + 1
    
    if idx <= context.user_data['cant_ausentes']:
        context.user_data['idx_ausente'] = idx
        await update.message.reply_text(f"Escriba el Nombre y Apellido del *Personal Ausente {idx}*:", parse_mode="Markdown")
        return NOMBRES_AUSENTES
    else:
        return await preguntar_vacaciones(update.message)

# --- VACACIONES ---

async def preguntar_vacaciones(message):
    keyboard = [
        [InlineKeyboardButton("Sí", callback_data="vac_si")],
        [InlineKeyboardButton("No", callback_data="vac_no")]
    ]
    await message.reply_text("¿Hay *personal de Vacaciones*?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return TIENE_VACACIONES

async def respuesta_tiene_vacaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "vac_si":
        await query.message.reply_text("Indique la *cantidad de personal de Vacaciones* (en números):", parse_mode="Markdown")
        return CANT_VACACIONES
    else:
        return await preguntar_permisos(query.message)

async def recibir_cant_vacaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if not texto.isdigit() or int(texto) <= 0:
        await update.message.reply_text("Por favor, ingrese un número mayor a 0:")
        return CANT_VACACIONES
    
    context.user_data['cant_vacaciones'] = int(texto)
    context.user_data['idx_vacacion'] = 1
    await update.message.reply_text("Escriba el Nombre y Apellido del *Personal de Vacaciones 1*:", parse_mode="Markdown")
    return NOMBRES_VACACIONES

async def recibir_nombre_vacacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text.strip()
    context.user_data['vacaciones'].append(nombre)
    idx = context.user_data['idx_vacacion'] + 1
    
    if idx <= context.user_data['cant_vacaciones']:
        context.user_data['idx_vacacion'] = idx
        await update.message.reply_text(f"Escriba el Nombre y Apellido del *Personal de Vacaciones {idx}*:", parse_mode="Markdown")
        return NOMBRES_VACACIONES
    else:
        return await preguntar_permisos(update.message)

# --- PERMISOS ---

async def preguntar_permisos(message):
    keyboard = [
        [InlineKeyboardButton("Sí", callback_data="perm_si")],
        [InlineKeyboardButton("No", callback_data="perm_no")]
    ]
    await message.reply_text("¿Hay *personal de Permiso*?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return TIENE_PERMISOS

async def respuesta_tiene_permisos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "perm_si":
        await query.message.reply_text("Indique la *cantidad de personal de Permiso* (en números):", parse_mode="Markdown")
        return CANT_PERMISOS
    else:
        return await pedir_coord_jdml(query.message)

async def recibir_cant_permisos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    if not texto.isdigit() or int(texto) <= 0:
        await update.message.reply_text("Por favor, ingrese un número mayor a 0:")
        return CANT_PERMISOS
    
    context.user_data['cant_permisos'] = int(texto)
    context.user_data['idx_permiso'] = 1
    await update.message.reply_text("Escriba el Nombre y Apellido del *Personal de Permiso 1*:", parse_mode="Markdown")
    return NOMBRES_PERMISOS

async def recibir_nombre_permiso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text.strip()
    context.user_data['permisos'].append(nombre)
    idx = context.user_data['idx_permiso'] + 1
    
    if idx <= context.user_data['cant_permisos']:
        context.user_data['idx_permiso'] = idx
        await update.message.reply_text(f"Escriba el Nombre y Apellido del *Personal de Permiso {idx}*:", parse_mode="Markdown")
        return NOMBRES_PERMISOS
    else:
        return await pedir_coord_jdml(update.message)

# --- 2. EMPRESA JDML ---

async def pedir_coord_jdml(message):
    await message.reply_text("🛡️ *EMPRESA JDML*\n\nEscriba el Nombre y Apellido del *Coordinador*:", parse_mode="Markdown")
    return COORD_JDML

async def recibir_coord_jdml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['coord_jdml'] = update.message.text.strip()
    await update.message.reply_text("Escriba el Nombre y Apellido en *Transporte*:", parse_mode="Markdown")
    return POS_TRANSPORTE_JDML

async def recibir_transporte_jdml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['transporte_jdml'] = update.message.text.strip()
    
    # Si es guardia Diurna, pedimos Proveedores; si es Nocturna, pasamos directo a Quinta Fides
    if context.user_data.get('tipo_guardia') == "Diurna":
        await update.message.reply_text("Escriba el Nombre y Apellido en *Proveedores*:", parse_mode="Markdown")
        return POS_PROVEEDORES_JDML
    else:
        await update.message.reply_text("Escriba el Nombre y Apellido en *Quinta Fides*:", parse_mode="Markdown")
        return POS_QUINTA_JDML

async def recibir_proveedores_jdml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['proveedores_jdml'] = update.message.text.strip()
    await update.message.reply_text("Escriba el Nombre y Apellido en *Quinta Fides*:", parse_mode="Markdown")
    return POS_QUINTA_JDML

async def recibir_quinta_jdml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['quinta_jdml'] = update.message.text.strip()
    
    # Si es Diurna, continuamos con las posiciones diurnas restantes de JDML
    if context.user_data.get('tipo_guardia') == "Diurna":
        await update.message.reply_text("

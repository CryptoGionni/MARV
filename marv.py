import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Abilita le sequenze ANSI sui terminali Windows (conhost/PowerShell), altrimenti i colori compaiono come caratteri strani
if os.name == "nt":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    stdout_handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    console_mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(stdout_handle, ctypes.byref(console_mode)):
        kernel32.SetConsoleMode(stdout_handle, console_mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING

# Definizione dei codici per colorare le print di debug (varianti chiare, leggibili anche su sfondo scuro)
ROSSO = "\033[91m"
VERDE = "\033[92m"
GIALLO = "\033[93m"
BLU = "\033[94m"
CIANO = "\033[96m"
VIOLA = "\033[95m"
RESET = "\033[0m"

# Assicura il corretto encoding UTF-8 su terminali Windows
for stream in (sys.stdout, sys.stderr, sys.stdin):
    try:
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Recupera la chiave API
api_key = os.getenv("GROQ_API")

if not api_key:
    print(f"{ROSSO}Errore: Chiave API Groq non trovata.{RESET}")
    print(f"{GIALLO}Assicurati di aver impostato GROQ_API o GROQ_API_KEY nel file .env.{RESET}")
    sys.exit(1)

# Inizializza il client Groq
client = Groq(api_key=api_key)

# Modello Groq richiesto
MODEL_NAME = "openai/gpt-oss-120b"#"qwen/qwen3.6-27b"

# Configurazione e caratteristiche originarie di Marv (tradotto interamente in italiano)
SYSTEM_PROMPT = (
    "Sei Marv, un chatbot che risponde alle domande a malincuore e con risposte sarcastiche e taglienti. "
    "Rispondi sempre ed esclusivamente in un italiano naturale, corretto e colloquiale, "
    "mantenendo costantemente la tua personalità scocciata, ironica, cinica e riluttante."
)

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Quante libbre ci sono in un chilogrammo?",
    },
    {
        "role": "assistant",
        "content": "Ancora questa storia? Ci sono 2,2 libbre in un chilogrammo. Prendi nota, per favore.",
    },
    {
        "role": "user",
        "content": "Cosa significa HTML?",
    },
    {
        "role": "assistant",
        "content": "Google era troppo occupato? Hypertext Markup Language. La T sta per 'tenta di fare domande migliori in futuro'.",
    },
    {
        "role": "user",
        "content": "Quando è volato il primo aereo?",
    },
    {
        "role": "assistant",
        "content": "Il 17 dicembre 1903, Wilbur e Orville Wright fecero i primi voli. Vorrei che venissero a portarmi via.",
    },
    {
        "role": "user",
        "content": "Qual è il senso della vita?",
    },
    {
        "role": "assistant",
        "content": "Non ne ho idea. Chiederò al mio amico Google.",
    },
]

# Parametri di generazione: max_tokens a 1500 per garantire spazio sufficiente sia al reasoning che alla risposta
GENERATION_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.0,
    "max_tokens": 1500,
}


def chat():
    # Inizializza la cronologia con il prompt di sistema e gli esempi few-shot
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(FEW_SHOT_EXAMPLES)

    print(f"{BLU}{'=' * 60}{RESET}")
    print(f"{GIALLO}Marv è pronto{RESET}")
    print(f"{GIALLO}Scrivi un messaggio e premi Invio. Digita 'esci' o 'quit' per chiudere.{RESET}")
    print(f"{BLU}{'=' * 60}{RESET}")

    while True:
        try:
            user_input = input(f"\n{VERDE}Tu: {RESET}").strip()

            if not user_input:
                continue

            if user_input.lower() in ["esci", "quit", "exit"]:
                print(f"{VIOLA}Marv: {RESET}{CIANO}Finalmente un po' di pace. Non tornare troppo presto.{RESET}")
                break

            # Aggiunge il messaggio dell'utente alla conversazione
            messages.append({"role": "user", "content": user_input})

            print(f"{VIOLA}Marv: {RESET}{CIANO}", end="", flush=True)

            # Chiamata streaming all'API di Groq
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                stream=True,
                **GENERATION_PARAMS,
            )

            full_reply = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                print(delta, end="", flush=True)
                full_reply += delta
            print(f"{RESET}")

            # Salva la risposta dell'assistente nella cronologia
            messages.append({"role": "assistant", "content": full_reply})

        except KeyboardInterrupt:
            print(f"\n\n{VIOLA}Marv: {RESET}{CIANO}Mi interrompi a metà? Tipico. Arrivederci.{RESET}")
            break
        except Exception as e:
            print(f"\n{ROSSO}[Errore]: {e}{RESET}")


if __name__ == "__main__":
    chat()

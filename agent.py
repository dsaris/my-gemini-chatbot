import google.generativeai as genai
import json
from datetime import datetime

# ─── Definisi Tools (Function Declarations) ───────────────────────────────────

GET_CURRENT_TIME = genai.protos.FunctionDeclaration(
    name="get_current_time",
    description="Mendapatkan waktu dan tanggal saat ini.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={}
    )
)

CALCULATOR = genai.protos.FunctionDeclaration(
    name="calculator",
    description="Menghitung ekspresi matematika. Gunakan ini untuk kalkulasi angka.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "expression": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Ekspresi matematika, contoh: '2 + 2', '10 * 5', '100 / 4'"
            )
        },
        required=["expression"]
    )
)

GET_WEATHER_INFO = genai.protos.FunctionDeclaration(
    name="get_weather_info",
    description="Mendapatkan informasi cuaca kota (simulasi).",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "city": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Nama kota, contoh: 'Jakarta', 'Surabaya'"
            )
        },
        required=["city"]
    )
)

TOOLS = genai.protos.Tool(
    function_declarations=[GET_CURRENT_TIME, CALCULATOR, GET_WEATHER_INFO]
)

# ─── Implementasi Tools ───────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Menjalankan tool yang dipanggil oleh AI Agent."""

    if tool_name == "get_current_time":
        now = datetime.now()
        return f"Waktu sekarang: {now.strftime('%H:%M:%S WIB, %A %d %B %Y')}"

    elif tool_name == "calculator":
        try:
            allowed = set("0123456789+-*/()., ")
            expr = tool_input.get("expression", "")
            if all(c in allowed for c in expr):
                result = eval(expr)
                return f"Hasil: {expr} = {result}"
            else:
                return "Error: Ekspresi tidak valid."
        except Exception as e:
            return f"Error kalkulasi: {str(e)}"

    elif tool_name == "get_weather_info":
        city = tool_input.get("city", "Unknown")
        weather_data = {
            "Jakarta": {"suhu": "32°C", "kondisi": "Cerah berawan", "kelembaban": "75%"},
            "Surabaya": {"suhu": "34°C", "kondisi": "Panas terik", "kelembaban": "70%"},
            "Bandung": {"suhu": "24°C", "kondisi": "Sejuk dan cerah", "kelembaban": "65%"},
            "Yogyakarta": {"suhu": "29°C", "kondisi": "Berawan", "kelembaban": "72%"},
        }
        if city in weather_data:
            d = weather_data[city]
            return f"Cuaca {city}: {d['kondisi']}, Suhu {d['suhu']}, Kelembaban {d['kelembaban']}"
        return f"Data cuaca untuk {city} tidak tersedia. Tersedia: Jakarta, Surabaya, Bandung, Yogyakarta."

    return f"Tool '{tool_name}' tidak dikenal."


# ─── AI Agent Runner ──────────────────────────────────────────────────────────

def run_agent(
    model: genai.GenerativeModel,
    chat_session: object,
    user_message: str
) -> str:
    """
    Menjalankan AI Agent dengan loop function calling.

    Returns:
        response_text (str)
    """
    response = chat_session.send_message(user_message)

    # Loop: tangani function calls hingga AI selesai
    while True:
        # Cek apakah ada function call di respons
        has_function_call = False
        function_responses = []

        for part in response.parts:
            if hasattr(part, "function_call") and part.function_call.name:
                has_function_call = True
                fn = part.function_call
                result = execute_tool(fn.name, dict(fn.args))
                function_responses.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fn.name,
                            response={"result": result}
                        )
                    )
                )

        if not has_function_call:
            break

        # Kirim hasil tool kembali ke model
        response = chat_session.send_message(function_responses)

    # Ambil teks akhir
    return response.text
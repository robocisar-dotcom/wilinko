# -*- coding: utf-8 -*-
import pathlib

html_path = pathlib.Path(r"g:\Môj disk\wilinko\..2.5.html")
b64_path = pathlib.Path(r"g:\Môj disk\wilinko\assets\kvetinky\home-weather-mascot.b64.txt")
text = html_path.read_text(encoding="utf-8")
b64 = b64_path.read_text(encoding="ascii")
chunk_size = 65536
chunks = [b64[i : i + chunk_size] for i in range(0, len(b64), chunk_size)]
lines = [
    "    /* Inline PNG — funguje aj pri content:// / lokálnom otvorení bez HTTP */",
    "    const HOME_WEATHER_MASCOT_B64_CHUNKS = [",
]
for i, ch in enumerate(chunks):
    lines.append("        " + repr(ch) + ("," if i < len(chunks) - 1 else ""))
lines.append("    ];")
lines.append("    function homeWeatherMascotDataUrl() {")
lines.append("        return 'data:image/png;base64,' + HOME_WEATHER_MASCOT_B64_CHUNKS.join('');")
lines.append("    }")
lines.append("")
inject = "\n".join(lines)
needle = "    async function refreshHomeWeatherMascot() {"
if needle not in text:
    raise SystemExit("needle missing")
if "HOME_WEATHER_MASCOT_B64_CHUNKS" in text:
    print("already injected")
else:
    text = text.replace(needle, inject + needle, 1)
    html_path.write_text(text, encoding="utf-8")
    print("injected", len(chunks), "chunks, total b64", len(b64))

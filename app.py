from flask import Flask, Response
from firecrawl import AsyncFirecrawlApp
import asyncio
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Video Player</title>
    <script src="https://telechileytelecampo.pages.dev/canales/tvntest/playerjs.js"></script>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
    <div id="playerjs" style="width:100%;height:100%;"></div>

   <script>
        const playerjs = new Playerjs({{
            id: "playerjs",
            file: "https://mdstrm.com/live-stream-playlist/57a498c4d7b86d600e5461cb.m3u8?access_token={token}"
        }});
    </script>
</body>
</html>
"""

async def get_token():
    firecrawl = AsyncFirecrawlApp(api_key='fc-1b0b66e4c57641d28405ac2b7308759a')
    response = await firecrawl.scrape_url(
        url='https://www.tvn.cl/en-vivo',
        formats=['rawHtml'],
        only_main_content=True,
        include_tags=['access_token'],
        parse_pdf=False,
        max_age=14400000
    )
    raw_html = response.rawHtml or ''
    match = re.search(r'access_token=([a-zA-Z0-9\-_\.]+)', raw_html)
    return match.group(1) if match else None

@app.route('/tvn')
def tvn_player():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    token = loop.run_until_complete(get_token())

    if token:
        final_html = HTML_TEMPLATE.format(token=token)
        return Response(final_html, mimetype='text/html')
    else:
        return "No se pudo obtener access_token", 500

@app.route('/')
def home():
    return tvn_player()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

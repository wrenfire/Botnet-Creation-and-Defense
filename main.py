import aiohttp
from aiohttp import web
from datetime import datetime
import json

app = web.Application()

async def handle_command(request):
    data = await request.json()  # Assuming commands come in JSON format
    print(f"Received command: {data}")
    # Process the command accordingly
    return web.Response(text=json.dumps({"response": "Command processed"}), content_type='application/json')

async def handle_data_upload(request):
    data = await request.read()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"data_{timestamp}"
    with open(filename, 'wb') as f:
        f.write(data)
    print(f"Data saved as {filename}")
    return web.Response(text="Data saved")

# Adding routes for command processing and data uploads
app.add_routes([web.post('/command', handle_command)])
app.add_routes([web.post('/upload', handle_data_upload)])

# Running the app
web.run_app(app, host='127.0.0.1', port=8080)

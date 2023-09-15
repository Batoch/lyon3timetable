import requests, bs4, json, os
from icalendar import Calendar, Event
from datetime import datetime
from urllib.parse import quote

try:
    username = quote(os.environ['USERNAME'])
    password = quote(os.environ['PASSWORD'])
except:
    raise ValueError("No username or password found.")

def getcalandar(username, password):
    s = requests.session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'fr-FR,fr;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Origin': 'https://cas.univ-lyon3.fr',
        'Referer': 'https://cas.univ-lyon3.fr/cas/login?service=https://apps.univ-lyon3.fr/emploidutemps/login?returnUrl=%2F',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # Get login page
    response = s.get("https://cas.univ-lyon3.fr/cas/login", params={"service": "https://apps.univ-lyon3.fr/emploidutemps/login?returnUrl=%2F"}, headers=headers)

    # Get token from the page
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    execution = soup.find("input", {"name":"execution"})['value']

    # Send auth infos
    data = f'username={username}&password={password}&execution={execution}&_eventId=submit&geolocation='
    response = s.post('https://cas.univ-lyon3.fr/cas/login?service=https://apps.univ-lyon3.fr/emploidutemps/login?returnUrl=%2F', headers=headers, data=data)

    # Get ticket id
    for resp in response.history:
        ticket = resp.headers['location'].split('ticket=')[1]

    # Authentificate using CAS infos
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'fr-FR,fr;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'https://apps.univ-lyon3.fr',
        'Referer': f'https://apps.univ-lyon3.fr/emploidutemps/login?returnUrl=%2F&ticket={ticket}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    json_data = {'Ticket': ticket,'Service': f'https://apps.univ-lyon3.fr/emploidutemps/login?returnUrl=%2F&ticket={ticket}'}
    response = s.post('https://apps.univ-lyon3.fr/apiEmploiDuTemps/Account/authenticate', headers=headers, json=json_data)

    # Get API token
    token = json.loads(response.text)['token']

    # Get calandar infos
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'fr-FR,fr;q=0.9',
        'Authorization': f'Bearer {token}',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Referer': 'https://apps.univ-lyon3.fr/emploidutemps/emploiDuTemps',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    response = s.get(f'https://apps.univ-lyon3.fr/apiEmploiDuTemps/Evenement/getEvenementsEtu/{username}/{datetime.now().year}', headers=headers)

    # Return Json calandar
    return(json.loads(response.text))



def json_to_ical(input_json):
    # Load JSON from input file or JSON string
    if isinstance(input_json, str):
        with open(input_json, 'r') as json_file:
            data = json.load(json_file)
    elif isinstance(input_json, list):
        data = input_json
    else:
        raise ValueError("The input must be either a JSON file or a JSON list.")

    # Creating an iCal Calendar object
    cal = Calendar()

    for item in data:
        event = Event()

        # Define iCal event properties
        event.add('summary', item['lblcours'])
        event.add('location', item['salle'])
        event.add('description', item['enseignant'])
        event.add('dtstart', datetime.fromisoformat(item['start'].replace('Z', '+00:00')))
        event.add('dtend', datetime.fromisoformat(item['end'].replace('Z', '+00:00')))

        # Add event to calendar
        cal.add_component(event)
    return(cal.to_ical()) 

def writetofile(caldata, output_ical_file="calendrier.ics"):
    with open(output_ical_file, 'wb') as ical_file:
        ical_file.write(caldata)


from flask import make_response, Flask

app = Flask(__name__)

# ...
@app.route("/")
def hello_world():
    return "<p>Server is up!</p>"
@app.route('/calendar/')
def calendar():

    #  Get the calendar data
    _calendar = json_to_ical(getcalandar(username, password))

    #  turn calendar data into a response
    response = make_response(_calendar)
    response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
    return response

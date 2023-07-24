import requests
import json
import time
import prometheus_client as prom
from prometheus_client import Gauge
import urllib3
from prometheus_client import Info
import platform

COOKIE_FILE = "session_cookie.txt"
DEVICEID_FILE = "deviceId.txt"
JSON_FILE = "sessiondata.json"

# GRAFANA INTEGRATION

i = Info('routename', 'Description of info')



#here we have defined the gauge, it also has only one metric, which is to show the ms load time of websites
RESPONSE_TIME_GAUGE = prom.Gauge('sample_external_url_response_ms', 'Url response time in ms', ["url"])
URL_LIST = ["https://github.com", "https://google.com"]  #here we have defined what sites we want our appliction to monitor

usedBandwidth = Gauge('usedBandwidth', 'Source Bandwidth used.')
bitrate = Gauge('bitrate', 'Source  stream bitrate (in kbps).')
srtLatency = Gauge('srtLatency', 'Source SRT latency')
srtRcvBuf = Gauge('srtRcvBuf', 'Source SRT receive buffer size in bytes.')
srtNumLostPackages = Gauge('srtNumLostPackages', 'SRT number of lost packages.')
srtRetransmitRate = Gauge('srtRetransmitRate', 'SRT retransmit rate in bits/s.')
srtRoundTripTime = Gauge('srtRoundTripTime', 'SRT round trip time in ms.')
srtPacketLossRate = Gauge('srtPacketLossRate', 'SRT packet loss rate.')
srtBufferLevel = Gauge('srtBufferLevel', 'srtBufferLevel')
srtNumLostPackets = Gauge('khl2_srtNumLostPackets', 'Connection srtNumLostPackets')
srtRetransmitRate_c = Gauge('khl2_srtRetransmitRate_c', 'srtRetransmitRate_c')




# Function to check if the cookie is still valid
def is_cookie_valid(response):
    return "sessionID" in response and response["sessionID"]

# Function to perform the login request and get the session cookie
def get_session_cookie():
    url = "https://10.2.19.247:443/api/session"
    payload = json.dumps({
        "username": "haiadmin",
        "password": "manager"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    print("POSTGETSESSION", url, headers, payload)
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print('GETSESSION', response)
    if response.status_code == 200:
        response_data = response.json()
        if is_cookie_valid(response_data.get("response")):
            return response_data["response"]["sessionID"]
    return None

# Function to save the session cookie to a file
def save_session_cookie(session_cookie):
    with open(COOKIE_FILE, "w") as file:
        file.write(session_cookie)
# Function to save ROUTE_LIST
def save_route_list(session_data):
    with open(JSON_FILE, "w") as json_file:
        json.dump(session_data, json_file)


def save_deviceId(response_text):
    try:
        devices_data = json.loads(response_text)
        device_id = devices_data[0]["_id"]
        with open(DEVICEID_FILE, "w") as file:
            file.write(device_id)
    except (json.JSONDecodeError, IndexError):
        print("Error saving device ID.")

# Function to load the device ID from the file
def load_deviceId():
    try:
        with open(DEVICEID_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

# Function to load the session cookie from the file
def load_session_cookie():
    print('load_session_cookie')
    try:
        with open(COOKIE_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None
#Route list 
def route_list(session_cookie):
    url = "https://10.2.19.247:443/api/gateway/y-OblOjyFRq38IwX1VvMWQ/routes"

    payload = {}
    headers = {
        'Cookie': f'sessionID={session_cookie}'
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    session_data = json.loads(response.text)
    # save_route_list(session_data)
    routenum = session_data['numResults']
    datanum = len(session_data['data'])
    active_routes = session_data['numActiveOutputConnections']
    print(f' {active_routes} Active routes configured in HGW')
    print(f' {routenum} Overal routes configured in HGW, please choose Route to analyse')
    i = 0
    while i < datanum:
        route_name = session_data['data'][i]['source']['name']
        route_state = session_data['data'][i]['state']
        route_source_status = session_data['data'][i]['source']['state']   
        if  route_source_status == 'connected':
            print (f'{route_name} is in {route_state} and source is {route_source_status}')
            route_name = session_data['data'][i]['source']['name']
            route_id = session_data['data'][i]['id']
            source_id = session_data['data'][i]['source']['id']
            print(f' Get statistic for route  {route_name}?')
            user_answer = input("Enter Y/N:")
            u_res = user_answer.upper()
            
            if u_res == 'Y':
                print(f'You choose {route_name} for Statistics see it in Grafana Tab http://10.10.1.36:3000/')
                return (route_name, route_id, source_id, route_source_status)
            else:
                i = i + 1      
        else:
            i = i + 1
    return None    
    
#GET DATA FUNC
def getdata(output):
    session_data = json.loads(output)

    # Source paarmeters---------------------------------------------

    name = session_data['source']['name']  # name
    elapsedRunningTime = session_data['source']['elapsedRunningTime']
    signalLosses = session_data['source']['signalLosses']
    sendRate = session_data['source']['sendRate']
    numPackets = session_data['source']['numPackets']  # ": 315353614,
    usedBandwidth = session_data['source']['usedBandwidth']  # ": 10.216,
    bitrate = session_data['source']['bitrate']  # ": 10.003,
    state = session_data['source']['state']  # ": "connected",
    srtLatency = session_data['source']['srtLatency']  # ": 2000,
    srtRcvBuf = session_data['source']['srtRcvBuf']  # ": 10240000,
    srtNumLostPackages = session_data['source']['srtNumLostPackages']  # ": 377408,
    srtRetransmitRate = session_data['source']['srtRetransmitRate']  # ": 3843,
    srtRoundTripTime = session_data['source']['srtRoundTripTime']  # ": 38.073,
    srtMaxBandwidth = session_data['source']['srtMaxBandwidth']  # ": 0,
    srtNegotiatedLatency = session_data['source']['srtNegotiatedLatency']  # ": 2000,
    srtPacketLossRate = session_data['source']['srtPacketLossRate']  # ": 0,
    srtBufferLevel = session_data['source']['srtBufferLevel']  # ": 2000,
    # connections parameters-------------------------------------------
    srtCurrentBandwidth = session_data['source']['connections'][0]['srtCurrentBandwidth']
    srtEstimatedBandwidth = session_data['source']['connections'][0]['srtEstimatedBandwidth']
    srtNumPackets = session_data['source']['connections'][0]['srtNumPackets']
    srtNumLostPackets = session_data['source']['connections'][0]['srtNumLostPackets']
    srtSkippedPackets = session_data['source']['connections'][0]['srtSkippedPackets']
    srtSkippedPacketsDiff = session_data['source']['connections'][0]['srtSkippedPacketsDiff']
    srtBufferLevel = session_data['source']['connections'][0]['srtBufferLevel']
    srtNegotiatedLatency = session_data['source']['connections'][0]['srtNegotiatedLatency']
    srtEncryption = session_data['source']['connections'][0]['srtEncryption']
    srtDecryptionState = session_data['source']['connections'][0]['srtDecryptionState']

    return (srtPacketLossRate, bitrate, usedBandwidth, srtLatency, srtRcvBuf, srtNumLostPackages, srtRetransmitRate,
            srtRoundTripTime, srtBufferLevel, srtRetransmitRate, srtNumLostPackets, name)

#GET ROUTE STAT
def route_stat(session_cookie, route_id, source_id):
   
    route = ('routeID=' + route_id)
    #source_id = 'e4e26596-1026-48f2-ab0a-593c2f75bb6d'
    source = ('sourceID=' + source_id)

    url = "https://10.2.19.247:443/api/gateway/y-OblOjyFRq38IwX1VvMWQ//statistics?" + route + "&" + source
    #print(url)
    payload = {}
    headers = {
        'Cookie': f'sessionID={session_cookie}'
    }
    urllib3.disable_warnings()
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    return response.text
    #print(response.text)

# Main function to use the session cookie
def main():
    session_cookie = load_session_cookie()
    print('Ssession_cookie', session_cookie)
    time.sleep(2)
    if not session_cookie:
        print('Ssession_cookie IS BAD')
        # session_cookie = get_session_cookie()
        if session_cookie:
            save_session_cookie(session_cookie)

    if session_cookie:
        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'Cookie': f'sessionID={session_cookie}'
        }

        data_url = "https://10.2.19.247:443/api/devices"
        response = requests.request("GET", data_url, headers=headers, data=payload, verify=False)
        # Check if the cookie is still valid, if not, get a new one and retry the request
        if response.status_code == 401:  # Unauthorized
            print('WROMG SESSION COOKIE GETTING NEW ONE')
            time.sleep(60)
            session_cookie = get_session_cookie()
            if session_cookie:
                save_session_cookie(session_cookie)
                print('NEW SESSION COOKIE SAVED')
                time.sleep(60)

        # print('SAVE DEVICE ID')
        # save_deviceId(response.text)
        deviceId = load_deviceId()
        print('DEVICE ID', deviceId)
        route_data = route_list(session_cookie)
        if route_data is None:
            print('No ACTIVE ROUTES AVAILABLE')
             # Terminate the main function or return an appropriate value as needed
            return
        route_name = route_data[0]
        route_id = route_data[1]
        source_id = route_data[2]
        x = 0
        i.info({'routename': route_name, 'buildhost': platform.node()})
    while x == 0:
        try:
            response = route_stat(session_cookie, route_id, source_id)
            data = getdata(response)
        except NameError:
            print(time.strftime("%H:%M:%S"))
        else:
            srtPacketLossRate.set_function(lambda: data[0])
            bitrate.set_function(lambda: data[1])
            usedBandwidth.set_function(lambda: data[2])
            srtLatency.set_function(lambda: data[3])
            srtRcvBuf.set_function(lambda: data[4])
            srtNumLostPackages.set_function(lambda: data[5])
            srtRetransmitRate.set_function(lambda: data[6])
            srtRoundTripTime.set_function(lambda: data[7])
            srtBufferLevel.set_function(lambda: data[8])
            srtRetransmitRate.set_function(lambda: data[9])
            srtNumLostPackets.set_function(lambda: data[10])
            #print(data[10])
            time.sleep(2)
    else:
        print("Login failed")
        


if __name__ == "__main__":
    promport = 8001
    prom.start_http_server(promport)
    print(f'Prometheus metrics available on port {promport} /metrics')
    main()
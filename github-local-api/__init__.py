from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from objdict import ObjDict
import requests
import json
import os
import configparser
import subprocess

app = Flask(__name__)

#Set environment and read porperties
envType = os.environ.get('RUNTIME_ENV_TYPE', 'local')
print ("RUNTIME_ENV_TIME : " + envType)
config = configparser.RawConfigParser()
config.read('app.properties')

#Overloaded returnError method for error handling
def returnError(httpErrorCode, iata, api, error=None):
    print('httpErrorCode: ' + str(httpErrorCode))
    #endpoint_url = config.get(envType, envType + '.' + api + '.endpoint.url') + iata
    outputroot = json.loads(config.get(envType, str(httpErrorCode) + '.error.message'))
    outputroot['error']['endpoint'] = api
    if not error is None:
        outputroot['error']['message'] = error
    outputroot_json = json.dumps(outputroot)
    return outputroot_json

@app.route('/git/v1/projects/projectid', methods=['POST'])
def returnAirportError():
    try:
        raise GITException
    except GITException:
        error = returnError(400, "<NULL>", "/git/v1/projects/projectid")
        return Response(error, status=400, mimetype='application/json')

@app.route('/git/v1/projects/projectid/<string:id>', methods=['POST'])
def returnAirportInfo(iata):
    outputroot = {}
    #Validate IATA
    try:
        if len(iata) > 3:
            raise GITException
        elif len(iata) < 3:
            raise GITException
        elif not iata.isalpha():
            raise GITException
    except GITException:
        error = returnError(400, iata)
        return Response(error, status=400, mimetype='application/json')
    else:
        #If id Valid - Call script to invoke git push
        try:
            api = config.get(envType, envType + '.airport.locator.url') + iata
            print('api_url : ' + api)
            airport_response = requests.get(api, timeout=5.0)
            airport_response_json = json.loads(airport_response.text)

            #Remove unwated medata field from SAP Hana Response
            airport_response_json ["results"][0].pop('__metadata')
        #Handle exceptions
        except requests.exceptions.HTTPError as error:
            error = returnError(504, iata, api, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.ConnectionError as error:
            error = returnError(504, iata, api, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.Timeout as error:
            error = returnError(504, iata, api, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.RequestException as error:
            error = returnError(504, iata, api, str(error))
            return Response(error, status=504, mimetype='application/json')
        except:
            #Error Handler
            error = returnError(airport_response.status_code, iata, api)
            return Response(error, status=airport_response.status_code, mimetype='application/json')

        #Convert to JSON
        outputroot_json = json.dumps(outputroot)
        return Response(outputroot_json, mimetype='application/json')

class Error(Exception):
   """Base class for other exceptions"""
   pass

class GITException(Error):
   """Raised when the input IATA length is greater than 3"""
   pass

if __name__ == "__main__":
    app.run("0.0.0.0", port=9031, debug=True)

from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
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
def returnError(httpErrorCode, id, error=None):
    print('httpErrorCode: ' + str(httpErrorCode))
    outputroot = json.loads(config.get(envType, str(httpErrorCode) + '.error.message'))
    outputroot['error']['endpoint'] = id
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
def returnAirportInfo(id):
    outputroot = {}
    #Validate IATA
    try:
        if len(id) < 3:
            raise GITException
    except GITException:
        error = returnError(400, id)
        return Response(error, status=400, mimetype='application/json')
    else:
        #If id Valid - Call script to invoke git push
        try:
            env = os.environ.get('ENV', 'local')
            print('env : ' + env)
            project_location = config.get(env, id + '.project')
            print('project_location : ' + project_location)
            output = subprocess.call(["./gitpush.ksh",project_location])
            print("output : " + output)
            #Remove unwated medata field from SAP Hana Response
            outputroot = {} 
            outputroot ["status"] = "Success"
        #Handle exceptions
        except requests.exceptions.HTTPError as error:
            error = returnError(504, id, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.ConnectionError as error:
            error = returnError(504, id, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.Timeout as error:
            error = returnError(504, id, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.RequestException as error:
            error = returnError(504, id, str(error))
            return Response(error, status=504, mimetype='application/json')
        except:
            #Error Handler
            error = returnError(500, id)
            return Response(error, status=500, mimetype='application/json')

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

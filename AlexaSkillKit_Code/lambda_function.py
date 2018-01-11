from radiosearch_tunein import AlexaTuneIn
import boto3, os

client = boto3.client('lambda')

# Adding security if you want.
# Populate with your skill's application ID to prevent someone else from configuring a skill that sends requests to this function.
# This ID is can be found under the Alexa tab on the amazon developer console page
# Goto https://developer.amazon.com/edw/home.html#/skills > Click 'View Skill ID'
CHECK_APP_ID = False
ALEXA_SKILL_APP_ID = "amzn1.ask.skill.#"

# Populate with the ARN of your created lambda function
RADIO_SEARCH_LAMBDA_ID = "arn:aws:lambda:<zone>:#:function:RadioSearch"


def lambda_handler(event, context):
    print "lambda_handler: " + str(event)
    if CHECK_APP_ID and (event["session"]["application"]["applicationId"] != ALEXA_SKILL_APP_ID):
        raise ValueError("Invalid Application ID")
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])


def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "AMAZON.LoopOffIntent" or intent_name == "AMAZON.LoopOnIntent" or intent_name == "AMAZON.RepeatIntent" or intent_name == "AMAZON.ShuffleOffIntent" or intent_name == "AMAZON.ShuffleOnIntent" or intent_name == "AMAZON.StartOverIntent":
        return handle_not_supported_request()
    elif intent_name == "AMAZON.NextIntent" or intent_name == "AMAZON.PreviousIntent" or intent_name == "AMAZON.ResumeIntent":
        return handle_last_played_request()
    elif intent_name == "AMAZON.PauseIntent":
        return handle_session_end_request()
    elif intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.CancelIntent":
        return handle_session_end_request()
    elif intent_name == "ResumeWithArtist":
        return handle_artist_request(intent)
    elif intent_name == "ResumeWithGenre":
        return handle_genre_request(intent)
    elif intent_name == "ResumeWithGeneralQuery":
        return handle_general_query_request_with_intent(intent)
    elif intent_name == "ResumeWithPreset":
        return handle_preset_request(intent)
    elif intent_name == "SavePreset":
        return handle_save_preset_request(intent)
    elif intent_name == "DeletePreset":
        return handle_delete_preset_request(intent)
    else:
        raise ValueError("Invalid intent")


def on_session_started(session_started_request, session):
    print "Starting new session."


def on_launch(launch_request, session):
    return get_welcome_response()


def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...


def handle_session_end_request():
    return {
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
            "directives": [
                {
                    "type": "AudioPlayer.Stop"
                }
            ],
            "shouldEndSession": True
        }
    }


def handle_error(output=None):
    card_title = "Radio Search - Error"
    should_end_session = False
    speech_output = "Error. Please try again."
    if output is not None:
        speech_output = output
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))


def handle_not_supported_request():
    card_title = "Radio Search - not supported"
    speech_output = "This action is not supported. Try again."
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))


def get_welcome_response():
    session_attributes = {}
    card_title = "Radio Search"
    speech_output = "Welcome to Radio Search. Please search for artist genre or general query."
    reprompt_text = "Please specify artist genre or general query"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_artist_from_intent(intent):
    print("get_artist_from_intent: " + str(intent))
    if "slots" in intent and "Artist" in intent["slots"]:
        return intent["slots"]["Artist"]["value"]
    else:
        return None


def get_genre_from_intent(intent):
    if "slots" in intent and "Genre" in intent["slots"]:
        return intent["slots"]["Genre"]["value"]
    else:
        return None


def get_general_query_from_intent(intent):
    if "slots" in intent and "Query" in intent["slots"]:
        return intent["slots"]["Query"]["value"]
    else:
        return None


def get_preset_from_intent(intent):
    if "slots" in intent and "Preset" in intent["slots"]:
        return intent["slots"]["Preset"]["value"]
    else:
        return None


def handle_artist_request(intent):
    print("handle_artist_request")
    artist = get_artist_from_intent(intent)
    if artist is None:
        return handle_error("No artist name given. Try again")
    return search_artist(artist, False)


def search_artist(artist, called_from_general_query):
    print("search_artist: " + str(artist))
    tunein = AlexaTuneIn(debug=True)
    station = tunein.get_random_artist_station(artist)
    if station is None:
        print("handle_artist_request artist not found. searching with general query")
        if called_from_general_query:
            return None
        else:
            return search_general_query(artist)
    return build_response({}, build_radio_station_speechlet_response(station))


def handle_genre_request(intent):
    print("handle_genre_request")
    genre = get_genre_from_intent(intent)
    if genre is None:
        return handle_error("No genre given. Try again")
    return search_genre(genre, False)


def search_genre(genre, called_from_general_query):
    print("search_genre: " + str(genre))
    tunein = AlexaTuneIn(debug=True)
    station = tunein.get_random_music_genre_station(genre)
    if station is None:
        print("handle_genre_request genre not found. searching with general query")
        if called_from_general_query:
            return None
        else:
            return search_general_query(genre)
    return build_response({}, build_radio_station_speechlet_response(station))


# def handle_general_query_request_with_intent(intent):
#     print("handle_general_query_request_with_intent")
#     query = get_general_query_from_intent(intent)
#     return search_general_query(query)
def handle_general_query_request_with_intent(intent):
    print("handle_general_query_request_with_intent")
    query = get_general_query_from_intent(intent)
    response = search_artist(query, True)
    # if response is None:
    #     response = search_genre(query, True)
    if response is None:
        return search_general_query(query)
    return response


def search_general_query(query):
    print("search_general_query: " + str(query))
    if query is None:
        return handle_error("No query given. Try again")
    tunein = AlexaTuneIn(debug=True)
    station = tunein.get_random_music_station(query)
    if station is None:
        return handle_error("No results for " + str(query) + ". Try another.")
    return build_response({}, build_radio_station_speechlet_response(station))


def handle_preset_request(intent):
    print("handle_preset_request")
    preset = get_preset_from_intent(intent)
    if preset is None:
        return handle_error("No preset given. Try again")

    if os.environ.get('Preset' + preset + '_URL') is not None:
        print "found preset " + preset + ": " + os.environ['Preset' + preset + '_URL']
        station_name = os.environ['Preset' + preset + "_Station_Name"]
        url = os.environ['Preset' + preset + '_URL']
    else:
        print "didn't find preset " + preset
        return handle_error("Preset " + str(preset) + " not configured. Try another.")

    save_last_played(url, station_name)
    return build_response({}, build_start_audio_speechlet_response(url, "RadioSearch", "playing " + station_name))


def handle_save_preset_request(intent):
    print("handle_save_preset_request")
    preset = get_preset_from_intent(intent)
    if preset is None:
        return handle_error("No preset given. Try again")

    if os.environ.get('Preset' + preset + '_URL') is not None:
        print "preset " + preset + " already exists"
        station_name = os.environ['Preset' + preset + "_Station_Name"]
        return handle_error("Preset " + preset + " already holds station " + station_name + ". please delete first.")
    elif os.environ.get('Last_Played_Station_Name') is not None:
        station_name = os.environ['Last_Played_Station_Name']
        url = os.environ['Last_Played_URL']
        save_preset(preset, url, station_name)
        speech_output = "saved " + station_name + " to preset " + preset
        print speech_output
        return build_response({}, build_speechlet_response("RadioSearch Preset save", speech_output, None, True))
    else:
        print "no station to save"
        return handle_error("no station ever played. Play one before saving preset.")


def handle_delete_preset_request(intent):
    print("handle_delete_preset_request")
    preset = get_preset_from_intent(intent)
    if preset is None:
        return handle_error("No preset given. Try again")

    if os.environ.get('Preset' + preset + '_URL') is not None:
        station_name = os.environ['Preset' + preset + "_Station_Name"]
        delete_preset(preset)
        speech_output = "preset " + preset + " with station " + station_name + " removed"
        print speech_output
        return build_response({}, build_speechlet_response("RadioSearch Preset delete", speech_output, None, True))
    else:
        print "preset " + preset + " doesn't exists. nothing to do."
        return handle_error("preset " + preset + " doesn't exists. nothing to do.")


def handle_last_played_request():
    print("handle_last_played_request")

    if os.environ.get('Last_Played_URL') is not None:
        station_name = os.environ['Last_Played_Station_Name']
        url = os.environ['Last_Played_URL']
    else:
        print "didn't find last played"
        return handle_error("Please specify artist, genre, or preset")

    return build_response({}, build_start_audio_speechlet_response(url, "RadioSearch", "playing last station, " + station_name))


def get_config_dict():
    config_dict = {}
    for item in os.environ.items():
        if item[0] == 'Last_Played_URL':
            config_dict['Last_Played_URL'] = item[1]
        elif item[0] == 'Last_Played_Station_Name':
            config_dict['Last_Played_Station_Name'] = item[1]
        elif item[0].startswith('Preset') and item[0].endswith('_URL'):
            config_dict[item[0]] = item[1]
        elif item[0].startswith('Preset') and item[0].endswith('_Station_Name'):
            config_dict[item[0]] = item[1]
    return config_dict


def save_config(config_dict):
    res = client.update_function_configuration(
        FunctionName=RADIO_SEARCH_LAMBDA_ID,
        Environment={
            'Variables': config_dict
        }
    )
    print "environment variables change response = " + str(res)


def save_last_played(url, station_name):
    config_dict = get_config_dict()
    config_dict['Last_Played_URL'] = url
    config_dict['Last_Played_Station_Name'] = station_name
    save_config(config_dict)


def save_preset(preset, url, station_name):
    config_dict = get_config_dict()
    config_dict['Preset' + preset + '_URL'] = url
    config_dict['Preset' + preset + '_Station_Name'] = station_name
    save_config(config_dict)


def delete_preset(preset):
    config_dict = get_config_dict()
    del config_dict['Preset' + preset + '_URL']
    del config_dict['Preset' + preset + '_Station_Name']
    save_config(config_dict)


def build_radio_station_speechlet_response(station):
    if station is None:
        return handle_error
    url = AlexaTuneIn.get_station_url(station)
    station_name = AlexaTuneIn.get_station_name(station)
    print "build_radio_station_speechlet_response: " + station_name + " - " + url
    response = build_start_audio_speechlet_response(url, "RadioSearch", "playing " + station_name)
    save_last_played(url, station_name)
    return response


def build_start_audio_speechlet_response(url, title, output):
    response = build_speechlet_response(title, output, None, True)
    response["directives"] = [
        {
            "type": "AudioPlayer.Play",
            "playBehavior": "REPLACE_ALL",
            "audioItem": {
                "stream": {
                    "token": "12345",
                    "url": url,
                    "offsetInMilliseconds": 0
                }
            }
        }
    ]
    return response


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

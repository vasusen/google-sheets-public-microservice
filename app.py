import os
import pickle
import re
from flask import Flask, jsonify, request, render_template, redirect
from googleapiclient import discovery
from googleapiclient.errors import HttpError

app = Flask(__name__)

API_KEY = os.environ.get('GOOGLE_SHEETS_API_KEY')

# Helper function to extract the Google Sheet ID from a URL
def extract_google_sheet_id(sheet_url):
    sheet_id_regex = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
    match = re.search(sheet_id_regex, sheet_url)
    return match.group(1) if match else None

# Helper function to get the name of the first sheet in the spreadsheet
def get_first_sheet_name(sheets_api, sheet_id):
    try:
        sheet_metadata = sheets_api.spreadsheets().get(spreadsheetId=sheet_id).execute()
        return sheet_metadata['sheets'][0]['properties']['title']
    except HttpError as error:
        return None
    
# Helper function to load the config from disk
def load_config():
    try:
        with open('config.pickle', 'rb') as config_file:
            return pickle.load(config_file)
    except (FileNotFoundError, pickle.UnpicklingError):
        return {}
    
# Helper function to save the config to disk
def save_config(config):
    with open('config.pickle', 'wb') as config_file:
        pickle.dump(config, config_file)

CONFIG = load_config()

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        default_sheet_url = request.form.get('default_sheet_url')

        if api_key:
            CONFIG['google_sheets_api_key'] = api_key

        if default_sheet_url:
            CONFIG['default_sheet_id'] = extract_google_sheet_id(default_sheet_url)

        save_config(CONFIG)
        return redirect('/config')
    api_key = CONFIG.get('google_sheets_api_key', API_KEY)
    default_sheet_id = request.args.get('sheet_id', CONFIG.get('default_sheet_id', None))
    default_sheet_url = f"https://docs.google.com/spreadsheets/d/{default_sheet_id}" if default_sheet_id else None
    return render_template('config.html', api_key=api_key, default_sheet_url=default_sheet_url)


@app.route('/row/<int:row_number>', methods=['GET'])
def get_row(row_number):
    api_key = CONFIG.get('google_sheets_api_key', None) or API_KEY

    if not api_key:
        return jsonify({'error': 'Google Sheets API Key is not set. Please set it in the /config page or as an environment variable.'}), 500

    sheets_api = discovery.build('sheets', 'v4', developerKey=api_key)

    # Get the user-provided Google Sheet ID and sheet name from the query parameter
    sheet_id = request.args.get('sheet_id', CONFIG.get('default_sheet_id', None))
    if not sheet_id:
        return jsonify({'error': 'Missing sheet_id parameter'}), 400

    sheet_name = request.args.get('sheet_name', None)
    if not sheet_name:
        sheet_name = get_first_sheet_name(sheets_api, sheet_id)
        if not sheet_name:
            return jsonify({'error': 'An error occurred while fetching the sheet name'}), 500

    range_name = f'{sheet_name}!A{row_number}:Z{row_number}'
    try:
        result = sheets_api.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    except HttpError as error:
        return jsonify({'error': f'An error occurred while accessing the Google Sheets API: {error}'}), 500

    values = result.get('values', [])

    if not values:
        return jsonify({'error': 'No data found'}), 404
    else:
        return jsonify({'row': values[0]})
    

@app.route('/rows/<int:start_row>/<int:end_row>', methods=['GET'])
def get_rows(start_row, end_row):
    api_key = CONFIG.get('google_sheets_api_key', None) or API_KEY

    if not api_key:
        return jsonify({'error': 'Google Sheets API Key is not set. Please set it in the /config page or as an environment variable.'}), 500

    sheets_api = discovery.build('sheets', 'v4', developerKey=api_key)

    sheet_id = request.args.get('sheet_id', CONFIG.get('default_sheet_id', None))
    if not sheet_id:
        return jsonify({'error': 'Missing sheet_id parameter'}), 400

    sheet_name = request.args.get('sheet_name', None)
    if not sheet_name:
        sheet_name = get_first_sheet_name(sheets_api, sheet_id)
        if not sheet_name:
            return jsonify({'error': 'An error occurred while fetching the sheet name'}), 500

    range_name = f'{sheet_name}!A{start_row}:Z{end_row}'
    try:
        result = sheets_api.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    except HttpError as error:
        return jsonify({'error': f'An error occurred while accessing the Google Sheets API: {error}'}), 500

    values = result.get('values', [])

    if not values:
        return jsonify({'error': 'No data found'}), 404
    else:
        return jsonify({'rows': values})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

# Google Sheets Microservice

This is a simple microservice that interacts with a publicly viewable Google Sheet. It exposes an API to read rows from a user's Google Sheet.

## Prerequisites

1. **Get Google Sheets API Key:**
   Follow the instructions [here](https://developers.google.com/sheets/api/quickstart/python) to "Enable API" and get a Google Sheets API key. Store this API key in your environment as GOOGLE_SHEETS_API_KEY. You can do that by adding the following in your terminal or adding it to .bash_profile or .bashrc file:

   ```
   export GOOGLE_SHEETS_API_KEY="<your-google-sheets-api-key>"
   ```

2. **Install Docker:**
   Follow the instructions in the Docker documentation to install Docker on your machine: https://docs.docker.com/get-docker/

## Setup

1. **Clone this repository:**

```
git clone <repository-url>
cd <repository-directory>
```

## Build and Run

1. **Build the Docker container:**

```
docker build -t my-microservice .
```

2. **Run the Docker container:**

Make sure your `GOOGLE_SHEETS_API_KEY` environment variable is set correctly. To verify, try printing it to see if you get the value:

```
printenv GOOGLE_SHEETS_API_KEY
```

Run the docker container to start the service:

```
docker run -p 8080:8080 -e GOOGLE_SHEETS_API_KEY my-microservice
```

Your microservice should now be running on http://localhost:8080/. You can make a GET request to `/row/<row_number>?sheet_id=<your-google-sheet-id>` to fetch data from a specific Google Sheet.

## Configuration UI

The microservice provides a configuration UI at http://localhost:8080/config where you can set the Google Sheets API Key and the default Google Sheet URL. This makes it easy to update the API key or switch between different Google Sheets without changing the environment variables or restarting the microservice.

## Endpoints

1. **Fetch a single row:**
   To fetch data from a single row, make a GET request to the following endpoint:

   ```
   GET /row/{row_number}?sheet_id={sheet_id}
   ```

2. **Fetch data from a range of rows:**
   To fetch data from a range of rows, make a GET request to the following endpoint:

   ```
   GET /rows/{start_row}/{end_row}?sheet_id={sheet_id}
   ```

Replace `{row_number}`, `{start_row}`, `{end_row}`, and `{sheet_id}` with the appropriate values for your use case. If you don't provide a `sheet_id`, the API will use the default `sheet_id` specified in the configuration.

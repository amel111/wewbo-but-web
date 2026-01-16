# Wewbo Web

A minimal Flask-based anime scraping and streaming web application.

## Features

- Search anime from multiple sources (currently Otakudesu).
- View anime details and episode lists.
- Stream episodes directly in the browser.
- Simple and clean interface.

## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd wewbo-web
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:

   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   `http://127.0.0.1:5000`

## Structure

- `app.py`: Main Flask application entry point.
- `extractors/`: Contains logic for scraping different anime sites.
- `templates/`: HTML templates for the web interface.
- `static/`: Static assets (CSS, JS, images).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

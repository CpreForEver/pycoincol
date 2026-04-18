# PyCoinCol - Coin Collection Manager

A Flask-based web application for managing coin collections with SQLite storage, fully aligned with PCGS certification data structure.

## Features

- View all coins in collection
- Add new coins with comprehensive PCGS data fields:
  - Identification: PCGS No, Cert No
  - Basic: Name, Year, Denomination, Mint (P/D/S/O/CC), Mint Mark, Mint Location
  - Specifications: Mintage, Metal Content, Diameter, Edge, Weight, Country
  - Grading: Grade, Designation
  - Market: Price Guide Value, Population, Pop Higher
  - References: CoinFacts Link, Designer
  - Images: Thumbnail URL, Fullsize URL
  - Custom: Description
- Edit existing coins
- Delete coins with confirmation
- Responsive HTML/CSS/JS interface
- Search coin database directly from home page
- PCGS API integration to fetch coin data by PCGS number
- Add coins manually or import from PCGS API
- PCGS API Bearer token authentication

## PCGS API Setup

To use the PCGS API for searching and importing coins, you need a PCGS API key:

1. Visit [PCGS API Setup](https://www.pcgs.com/api) to get your API key
2. Create a token file or set environment variable:

```bash
# Create token file (recommended)
echo "your_api_key_here" > pcgs_token.token

# Or set environment variable
export PCGS_API_KEY="your_api_key_here"
```

The application automatically loads the token from `pcgs_token.token` if present.

## Database Schema

The `coins` table contains the following fields matching simplified coin data structure:

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| pcgs_no | TEXT | PCGS certification number |
| cert_no | TEXT | Certificate number |
| name | TEXT | Coin name (required) |
| year | INTEGER | Year of issue |
| denomination | TEXT | Coin denomination |
| mint | TEXT | Mint (P/D/S/O/CC) |
| mint_mark | TEXT | Mint mark |
| mint_location | TEXT | Full mint location |
| metal_content | TEXT | Metal composition |
| diameter | REAL | Coin diameter in mm |
| edge | TEXT | Edge type |
| weight | REAL | Coin weight in grams |
| country | TEXT | Country of origin |
| grade | TEXT | Grade (e.g., MS-65) |
| designation | TEXT | Designation |
| price_guide_value | REAL | PCGS price guide value |
| population | INTEGER | Population count |
| pop_higher | INTEGER | Population higher grade |
| coin_facts_link | TEXT | CoinFacts URL |
| designer | TEXT | Coin designer |
| thumbnail_url | TEXT | Thumbnail image URL |
| fullsize_url | TEXT | Full-size image URL |
| description | TEXT | Custom description |
| condition | TEXT | Condition notes |
| price | REAL | Market price |
| image_url | TEXT | Alternate image URL |
| pcgs_number | TEXT | Alternative PCGS number |

## Installation

```bash
# Clone repository and install dependencies
uv sync
```

## Usage

```bash
# Initialize database and start the application
uv run coin_collection.py
```

The database (`coins.db`) is created automatically on first run.

Access the application at `http://localhost:5000`

## Project Structure

```
pycoincol/
├── coin_collection.py    # Main Flask application
├── main.py               # Entry point
├── pyproject.toml        # Project configuration
├── coins.db              # SQLite database (auto-created)
├── pcgs_token.token      # PCGS API token (create this file)
├── templates/            # HTML templates
│   ├── index.html       # Home page
│   ├── coins.html       # Coin listing
│   ├── add_coin.html    # Add coin form
│   └── edit_coin.html   # Edit coin form
├── static/
│   ├── css/style.css    # Styles
│   └── js/app.js        # Frontend JavaScript
└── README.md            # This file
```

## Development

The application uses Flask with SQLite. Set up a virtual environment:

```bash
# Create and activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync

# Run the application
uv run main.py
```

## Dependencies

- Flask
- requests

View all dependencies in `pyproject.toml`.

## Notes

- Database is initialized automatically on first run
- PCGS API authentication is handled automatically via `pcgs_token.token`
- Coin images are fetched from PCGS API when available
- All coin data fields are indexed for efficient searching

## License

MIT License

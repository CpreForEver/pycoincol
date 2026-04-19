# PyCoinCol - Coin Collection Manager

A Flask-based web application for managing coin collections with SQLite storage, fully aligned with PCGS certification data structure.

## Features

- View all coins, bank notes, and coin sets in collection
- Add new coins with comprehensive PCGS data fields:
  - Identification: PCGS No, Cert No
  - Basic: Name, Year, Denomination, Mint (P/D/S/O/CC), Mint Mark, Mint Location
  - Specifications: Mintage, Metal Content, Diameter, Edge, Weight, Country
  - Grading: Grade, Designation
  - Market: Price Guide Value, Population, Pop Higher
  - References: CoinFacts Link, Designer
  - Images: Thumbnail URL, Fullsize URL
  - Custom: Description
- Add bank notes with full PCGS notes data:
  - Identification: PCGS No, Cert No, Serial No
  - Basic: Name, Year, Denomination, Region
  - Grading: Grade, Details, Population, Pop Higher
  - Specifications: Height, Width
  - Catalog: Catalog No 1&2 (Long/Short Descriptions)
  - References: Signers, Qualifiers, Plate No, Value View Link
  - Images: Has Obverse/Reverse Images, Image Description
  - Market: Price Value Guide
- Add coin sets with full PCGS sets data:
  - Year, Region, Grade, Details
  - Population, Pop Higher, Serial No
  - Images: Thumbnail URL, Popup URL, Image Description
  - Specifications: Width, Height
  - Flags: Has Obverse/Reverse Images, Image Ready
  - Market: Price Value Guide
- Edit existing coins, bank notes, and coin sets
- Delete items with confirmation
- Responsive HTML/CSS/JS interface
- Search coin database directly from home page
- PCGS API integration to fetch coin, note, and set data
- Automatic total portfolio value calculation (coins + notes + sets)
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

### coins table

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

### notes table (bank notes/bills)

The `notes` table contains fields for bank note data:

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| pcgs_no | TEXT | PCGS certification number |
| cert_no | TEXT | Certificate number |
| name | TEXT | Bank note name |
| year | INTEGER | Year of issue |
| denomination | TEXT | Denomination (e.g., $1, $5) |
| region | TEXT | Region |
| grade | TEXT | Grade |
| details | TEXT | Details |
| population | INTEGER | Population count |
| pop_higher | INTEGER | Population higher grade |
| serial_no | TEXT | Serial number |
| height | TEXT | Height |
| width | TEXT | Width |
| catalog_no1 | TEXT | First catalog number |
| catalog_no2 | TEXT | Second catalog number |
| catalog1_long_desc | TEXT | Catalog 1 long description |
| catalog2_long_desc | TEXT | Catalog 2 long description |
| catalog1_short_desc | TEXT | Catalog 1 short description |
| catalog2_short_desc | TEXT | Catalog 2 short description |
| signers | TEXT | Signers |
| qualifiers | TEXT | Qualifiers |
| plate_no | TEXT | Plate number |
| value_view_link | TEXT | Value view link |
| price_value_guide | REAL | PCGS price value guide |
| has_obverse_image | INTEGER | Has obverse image |
| has_reverse_image | INTEGER | Has reverse image |
| image_ready | INTEGER | Image ready status |
| image_description | TEXT | Image description |
| description | TEXT | Custom description |
| created_at | TEXT | Creation timestamp |
| updated_at | TEXT | Update timestamp |

### coin_sets table

The `coin_sets` table contains fields for coin set data:

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| year | INTEGER | Year of set |
| region | TEXT | Region |
| grade | TEXT | Grade |
| details | TEXT | Set details |
| population | INTEGER | Population count |
| pop_higher | INTEGER | Population higher grade |
| serial_no | TEXT | Serial number |
| thumbnail_url | TEXT | Thumbnail image URL |
| popup_url | TEXT | Popup URL |
| image_description | TEXT | Image description |
| width | INTEGER | Width |
| height | INTEGER | Height |
| has_obverse_image | INTEGER | Has obverse image |
| has_reverse_image | INTEGER | Has reverse image |
| image_ready | INTEGER | Image ready status |
| price_value_guide | REAL | PCGS price value guide |

## Installation

```bash
# Clone repository and install dependencies
uv sync
```

## Usage

```bash
# Initialize database and start the application
uv run main.py
```

The database (`coins.db`) is created automatically on first run.

Access the application at `http://localhost:5000`

## Project Structure

```
pycoincol/
├── main.py               # Entry point
├── notes_collection.py   # Bank notes blueprint
├── coin_collection.py    # Coins blueprint
├── index.py              # Index blueprint
├── database.py           # Database functions
├── pyproject.toml        # Project configuration
├── coins.db              # SQLite database (auto-created)
├── pcgs_token.token      # PCGS API token (create this file)
├── templates/            # HTML templates
│   ├── index.html       # Home page
│   ├── coins.html       # Coin listing
│   ├── add_coin.html    # Add coin form
│   ├── edit_coin.html   # Edit coin form
│   ├── notes.html       # Bank notes listing
│   ├── add_notes.html   # Add bank note form
│   └── edit_notes.html  # Edit bank note form
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

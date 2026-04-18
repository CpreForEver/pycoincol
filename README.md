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
- Search PCGS API to fetch coin data by PCGS number
- Add coins manually or import from PCGS API
- PCGS API Bearer token authentication required

## PCGS API Setup

To use the PCGS API for searching and importing coins, you need a PCGS API key:

1. Visit [PCGS API Setup](https://www.pcgs.com/api) to get your API key
2. Copy your API key to the `PCGS_API_KEY` environment variable:

```bash
# Set on your shell
export PCGS_API_KEY="your_api_key_here"

# Or create a token file
echo "your_api_key_here" > pcgs_token.token
```

The application automatically uses the `PCGS_API_KEY` environment variable for API authentication.

## Database Fields

The `coins` table contains the following fields matching simplified coin data structure:

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| coin_name | TEXT | Coin name (required) |
| coin_no | TEXT | PCGS certification number |
| cert_no | TEXT | Certificate number |
| year | INTEGER | Year of issue |
| grade | TEXT | Grade (e.g., MS-65) |

| Field | Type | Description |
|-------|------|-------------|
| pcgs_no | TEXT | PCGS certification number |
| cert_no | TEXT | Certificate number |
| coin_name | TEXT | Coin name (required) |
| year | INTEGER | Year of issue |
| grade | TEXT | Grade (e.g., MS-65) |


## Installation

```bash
# Set up environment and install dependencies
uv sync
```

## Usage

```bash
# Initialize database and start the application
uv run coin_collection.py
```

The database (`coins.db`) is created automatically on first run.

## Project Info

- Framework: Flask
- Database: SQLite
- Dependencies: flask, requests
- Created: 2026

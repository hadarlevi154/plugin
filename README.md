# DummyJSON Plugin

This plugin collects evidence from the DummyJSON API.

## Overview

The plugin connects to the DummyJSON API and collects the following:

○ **E1 - User Details** - Collect the authenticated user details (the user you picked to use).

○ **E2 - Posts**- Collect a list of 60 posts in the system.

○ **E3 - Posts with Comments** - Collect a list of 60 posts, including each post’s comments.


## Installation

1. Clone the repository:
   ```
   git clone https://github.com/hadarlevi154/plugin.git
   cd plugin
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the plugin with default settings:
```
python main.py
```

Or customize parameters:
```
python main.py --username *** --password *** --api-base-url https://dummyjson.com
```

### Command-line Arguments

- `--username`: Username for authentication (default: emilys )
- `--password`: Password for authentication (default: emilyspass)
- `--api-base-url`: Base URL for the API (default: https://dummyjson.com)
- `--test-only`: Run only the connectivity test without collecting evidence

## Project Structure

```
plugin/
├── main.py                  # Entry point
├── plugin/
│   ├── __init__.py
│   ├── base_plugin.py       # Base plugin abstract class
│   ├── config.py            # Plugin configuration
│   ├── dummyjson_plugin.py  # DummyJSON implementation
│   └── models.py            # Data models
└── requirements.txt         # Dependencies
```

## Design Considerations

- **Modularity**: The plugin is designed with a base class that can be extended for other APIs
- **Error Handling**: Comprehensive error handling for API responses and exceptions
- **Configurability**: Easily configurable through command-line arguments
- **Extensibility**: New evidence types can be added by implementing additional collection methods

## Contact
hadarlevi154@gmail.com

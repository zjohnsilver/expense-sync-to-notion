# Streamlit App Structure

This directory contains the refactored Streamlit application with separated responsibilities for better maintainability and organization.

## Structure

```
streamlit_app/
├── app.py                 # Main application entry point
├── components/            # UI components
│   ├── config_display.py  # Configuration display component
│   ├── data_editor.py     # Data editor component
│   ├── payload_preview.py # Notion payload preview component
│   └── validation_display.py # Validation results display
├── processors/            # Data processing logic
│   ├── data_loader.py     # CSV data loading
│   └── notion_processor.py # Notion data transformation and sending
├── session/               # Session state management
│   └── state_manager.py   # Session state initialization and reset
└── validators/            # Data validation
    └── data_validator.py  # CSV data validation logic
```

## Responsibilities

### `app.py`

Main application orchestrator that:

- Sets up the Streamlit page configuration
- Coordinates all components and flows
- Handles the main application logic

### `components/`

UI components that handle specific interface elements:

- **data_editor.py**: The interactive Notion data editor
- **payload_preview.py**: Preview of Notion API payloads
- **validation_display.py**: Display validation results and errors
- **config_display.py**: Show current configuration

### `processors/`

Data processing logic:

- **data_loader.py**: Load and parse CSV files
- **notion_processor.py**: Transform data for Notion and handle API calls

### `session/`

Session state management:

- **state_manager.py**: Initialize and reset Streamlit session state

### `validators/`

Data validation logic:

- **data_validator.py**: Validate CSV data format and structure

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Maintainability**: Easy to find and modify specific functionality
3. **Testability**: Individual components can be tested in isolation
4. **Reusability**: Components can be reused across different parts of the app
5. **Readability**: Clear structure makes the codebase easier to understand
6. **Scalability**: Easy to add new features without affecting existing code

## Usage

The app is launched through the main entry point:

```bash
python main.py --streamlit
```

This will run `src/streamlit_app/app.py` which coordinates all the components.

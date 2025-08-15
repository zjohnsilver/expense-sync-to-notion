# 💰 Expense Sync to Notion

This project automates the process of registering expenses from CSV files (initially from Inter bank) to Notion through the Notion API.

## ✨ Features

- **Interactive Streamlit Interface**: Review, edit, and validate your expense data before syncing
- **Data Validation**: Automatic validation of date formats, values, and required fields
- **Row Management**: Edit individual rows and mark rows for deletion
- **Preview Mode**: See exactly what will be sent to Notion before syncing
- **Progress Tracking**: Real-time progress indicators during sync
- **CLI Mode**: Direct command-line sync for automation

## 🚀 Quick Start

### 1. Setup Environment

Copy and fill the environment variables:

```sh
make setup
```

Edit the `.env` file with your configuration:

```env
NOTION_SECRET=your_notion_integration_secret_here
FINANCE_DASHBOARD_ID=your_notion_database_id_here
MONTHLY_INVOICE_FILENAME=fatura.csv
```

### 2. Install Dependencies

```sh
make install
# or
uv sync
```

### 3. Run the Application

**Interactive Mode (Recommended):**

```sh
make run-streamlit
# or
python main.py --streamlit
```

**Default (only run script):**

```sh
make run
# or
python main.py
```

## 📊 CSV Format

Your CSV file should have the following columns:

- `Data`: Date in DD/MM/YYYY format
- `Lançamento`: Transaction description
- `Categoria`: Category
- `Tipo`: Transaction type
- `Valor`: Value in R$ format (e.g., "R$ 123,45")

## 🎯 Notion Database Schema

Your Notion database should have these properties:

- `Month`: Select field for month
- `Bank Description`: Rich text field
- `Category`: Select field for expense category
- `Value`: Number field
- `Date`: Date field
- `Payment`: Select field (defaults to "CREDIT_CARD")
- `Type`: Select field (defaults to "NON-ESSENTIAL")
- `SOURCE`: Select field (defaults to "AUTOMATION")

## 🔧 Available Commands

- `make setup`: Create .env file from template
- `make install`: Install dependencies with uv
- `make run`: Launch Streamlit interface (default)
- `make run-streamlit`: Launch interactive Streamlit interface
- `make run-cli`: Run CLI version for direct sync

## This project uses gitmoji

Gitmoji: https://gitmoji.dev/

- ✨ feat
- 🐛 fix
- ♻️ refactor
- 📝 docs
- 🔧 chore
- ✅ test

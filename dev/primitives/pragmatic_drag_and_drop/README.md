# Pragmatic Drag and Drop - CSV Editor

A demonstration of [Atlassian's Pragmatic Drag and Drop](https://github.com/atlassian/pragmatic-drag-and-drop) library that edits CSV data through drag and drop interactions.

## Features

- **Board View**: Drag cards between columns to update the `status` field
- **Tree View**: Drag items into folders to update the `parent` field
- All changes are persisted to `data/items.csv`

## Quick Start

1. Install dependencies:
   ```bash
   pip install flask flask-cors pandas
   ```

2. Start the server:
   ```bash
   python server.py
   ```

3. Open http://localhost:5000 in your browser

## File Structure

```
pragmatic_drag_and_drop/
├── index.html      # Frontend with drag-and-drop UI
├── server.py       # Flask API server for CSV operations
├── data/
│   └── items.csv   # Source data (edited by drag-and-drop)
└── README.md
```

## CSV Data Format

The `data/items.csv` file contains all items with these columns:

| Column   | Description                                      |
|----------|--------------------------------------------------|
| `id`     | Unique identifier                                |
| `name`   | Display name                                     |
| `type`   | `card` (board), `folder`, or `file` (tree)       |
| `parent` | Parent folder ID (empty = root level)            |
| `status` | `todo`, `in-progress`, or `done`                 |

### Example CSV

```csv
id,name,type,parent,status
documents,Documents,folder,,todo
report,Report.pdf,file,documents,todo
research,Research task,card,,in-progress
```

## How It Works

### Board Tab (Edits `status`)

- Shows items where `type = "card"`
- Cards are grouped into columns by their `status` value
- Dragging a card to a different column updates `status` in the CSV

### Tree Tab (Edits `parent`)

- Shows items where `type = "folder"` or `type = "file"`
- Items are nested based on their `parent` value
- Dragging an item:
  - **Into a folder**: Sets `parent` to that folder's ID
  - **Above/below another item**: Sets `parent` to that item's parent
  - **To "root level" zone**: Clears `parent` (empty string)

## API Endpoints

| Method | Endpoint                    | Description                |
|--------|----------------------------|----------------------------|
| GET    | `/api/items`               | Get all items              |
| PUT    | `/api/items/<id>`          | Update any field           |
| PUT    | `/api/items/<id>/status`   | Update status only         |
| PUT    | `/api/items/<id>/parent`   | Update parent only         |

### Example API Calls

```bash
# Get all items
curl http://localhost:5000/api/items

# Update an item's status
curl -X PUT http://localhost:5000/api/items/research/status \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# Update an item's parent
curl -X PUT http://localhost:5000/api/items/report/parent \
  -H "Content-Type: application/json" \
  -d '{"parent": "images"}'
```

## Adding New Items

Edit `data/items.csv` directly to add new items:

```csv
my-task,My New Task,card,,todo
my-folder,My Folder,folder,,todo
my-file,MyFile.txt,file,my-folder,todo
```

Then refresh the browser to see the changes.

## Dependencies

- Python 3.7+
- Flask (web server)
- Flask-CORS (cross-origin requests)
- pandas (CSV handling)

## Resources

- [Pragmatic Drag and Drop Documentation](https://atlassian.design/components/pragmatic-drag-and-drop/)
- [GitHub Repository](https://github.com/atlassian/pragmatic-drag-and-drop)

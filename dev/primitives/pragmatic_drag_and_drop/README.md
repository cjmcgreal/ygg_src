# Pragmatic Drag and Drop Examples

A simple demonstration of [Atlassian's Pragmatic Drag and Drop](https://github.com/atlassian/pragmatic-drag-and-drop) library with two examples: a Kanban Board and a File Tree.

## Quick Start

1. Open `index.html` in a modern web browser (Chrome, Firefox, Safari, Edge)
2. That's it! No build step or npm install required

The examples load the library directly from a CDN using ES modules.

## Examples

### Board (Kanban)

A three-column Kanban board where you can drag cards between columns:

- **To Do** - Tasks waiting to be started
- **In Progress** - Tasks currently being worked on
- **Done** - Completed tasks

Drag any card and drop it on a different column to move it.

### Tree (File Explorer)

A hierarchical file tree where you can:

- **Reorder items** - Drag above or below other items
- **Move into folders** - Drag to the middle of a folder to nest items inside

## How It Works

### Key Concepts

**1. Draggable Elements**

Makes an element draggable:

```javascript
import { draggable } from '@atlaskit/pragmatic-drag-and-drop/element/adapter';

draggable({
    element: myElement,
    getInitialData: () => ({ id: 'item-1' }),  // Data attached to the drag
    onDragStart: () => { /* Called when drag begins */ },
    onDrop: () => { /* Called when drag ends */ }
});
```

**2. Drop Targets**

Makes an element accept drops:

```javascript
import { dropTargetForElements } from '@atlaskit/pragmatic-drag-and-drop/element/adapter';

dropTargetForElements({
    element: myDropZone,
    getData: () => ({ zoneId: 'zone-1' }),     // Data about the drop target
    canDrop: ({ source }) => true,             // Control if drops are allowed
    onDragEnter: () => { /* Draggable entered */ },
    onDragLeave: () => { /* Draggable left */ },
    onDrop: ({ source }) => { /* Handle the drop */ }
});
```

**3. Monitors**

Listen to all drag and drop events globally:

```javascript
import { monitorForElements } from '@atlaskit/pragmatic-drag-and-drop/element/adapter';

monitorForElements({
    onDragStart: ({ source }) => console.log('Started:', source.data),
    onDrop: ({ source, location }) => console.log('Dropped:', source.data)
});
```

## File Structure

```
pragmatic_drag_and_drop/
├── index.html    # Complete example with HTML, CSS, and JavaScript
└── README.md     # This file
```

## Browser Support

Works in all modern browsers:
- Chrome / Edge
- Firefox
- Safari

## Resources

- [Official Documentation](https://atlassian.design/components/pragmatic-drag-and-drop/)
- [GitHub Repository](https://github.com/atlassian/pragmatic-drag-and-drop)
- [npm Package](https://www.npmjs.com/package/@atlaskit/pragmatic-drag-and-drop)
- [Video Tutorial](https://www.youtube.com/watch?v=5SQkOyzZLHM)

## Using in Your Own Project

### Option 1: CDN (No Build Step)

Use ES modules directly in HTML (like this example):

```html
<script type="module">
    import { draggable } from 'https://esm.sh/@atlaskit/pragmatic-drag-and-drop/element/adapter';
    // Your code here
</script>
```

### Option 2: npm (Build Step Required)

```bash
npm install @atlaskit/pragmatic-drag-and-drop
```

```javascript
import { draggable } from '@atlaskit/pragmatic-drag-and-drop/element/adapter';
```

## Tips for Beginners

1. **Visual Feedback** - Always show users where items will land (borders, backgrounds)
2. **Data First** - Attach meaningful data with `getInitialData()` and `getData()`
3. **Clean Up** - Remove visual indicators in `onDragLeave` and `onDrop`
4. **Console Logging** - Use `monitorForElements` to debug drag operations

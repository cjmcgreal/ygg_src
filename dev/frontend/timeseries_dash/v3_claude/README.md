# ⚡ Epic Timeseries Visualization Tool V3 - Drag & Drop Edition

The **slickest, coolest, hippest, baddest** timeseries tool on the planet! Built with **Plotly Dash** for true real-time interactivity.

## 🎯 Features

✅ **Drag-and-Drop Interface** - Grab channels and drop them onto the plot
✅ **Real-Time Updates** - Plot updates instantly as you drop channels
✅ **Collapsible Navigation Tree** - Organized hierarchical channel browser
✅ **Interactive Plotly Charts** - Zoom, pan, hover for details
✅ **Flexible Time Aggregation** - Hour, day, week, month buckets
✅ **Date Range Selection** - Custom start/end dates
✅ **Multiple Aggregation Methods** - Mean, sum, min, max, median
✅ **Beautiful UI** - Bootstrap-based modern design

## 🚀 Quick Start

### Option 1: Quick Launch
```bash
./run.sh
```

### Option 2: Manual
```bash
pip install -r requirements.txt
python app_v2.py
```

Then open your browser to: **http://127.0.0.1:8050**

## 📊 How to Use

1. **Browse Channels** - Expand categories in the left sidebar
2. **Drag & Drop** - Click and drag a channel, then drop it on the "Selected Channels" area
3. **Watch Magic Happen** - The plot updates instantly!
4. **Adjust Settings** - Change date range, time buckets, aggregation method
5. **Remove Channels** - Click the ✖ on any channel badge to remove it
6. **Clear All** - Hit the "Clear" button to start fresh

## 📁 Project Structure

```
v3_claude/
├── app_v2.py                          # Main Dash application
├── run.sh                             # Quick launch script
├── requirements.txt                   # Python dependencies
├── assets/
│   └── drag_drop.js                  # Custom drag-and-drop JavaScript
└── src/
    └── timeseries/
        ├── timeseries_db.py          # Data loading layer
        ├── timeseries_analysis.py    # Aggregation & processing
        └── timeseries_data/
            ├── timeseries_data.csv   # 90 days × 12 channels
            └── channel_tags.csv      # Channel metadata
```

## 📊 Sample Data

Includes **12 channels** across **4 hierarchies**:

- **Building A** - HVAC Temperature, HVAC Humidity, Power Consumption
- **Building B** - HVAC Temperature, HVAC Humidity, Power Consumption
- **Factory** - Line 1 Speed & Temp, Line 2 Speed & Temp
- **Warehouse** - Inventory Count, Environmental Temperature

**Data**: 90 days of hourly readings = 2,161 data points per channel!

## 🎨 Technology Stack

- **Plotly Dash** - Interactive web framework
- **Plotly.js** - High-performance charting
- **Bootstrap 5** - Modern UI components
- **Pandas** - Data manipulation
- **Custom JavaScript** - Drag-and-drop magic

## 🎯 Key Differences from V2

| Feature | V2 (Streamlit) | V3 (Dash) |
|---------|----------------|-----------|
| Drag & Drop | ❌ | ✅ True drag-and-drop |
| Real-time Updates | ⚠️ Button click | ✅ Instant on drop |
| Interactivity | Limited | Full Plotly interactivity |
| Channel Selection | Click buttons | Drag-and-drop |
| Performance | Good | Excellent |

## 💡 Tips & Tricks

- **Multi-select**: Drop multiple channels for comparison
- **Remove**: Click ✖ on any channel badge
- **Zoom**: Use Plotly's built-in zoom tools
- **Hover**: Hover over data points for details
- **Reset**: Double-click the plot to reset zoom

## 🔧 Customization

Want to add your own data?

1. Replace `timeseries_data.csv` with your data (must have `timestamp` column)
2. Update `channel_tags.csv` with your channel hierarchy
3. Restart the app!

## 🐛 Troubleshooting

**Port already in use?**
```python
# Edit app_v2.py, change the port:
app.run_server(debug=True, port=8051)  # Use different port
```

**Drag-and-drop not working?**
- Make sure JavaScript is enabled
- Clear browser cache
- Try a different browser (Chrome/Firefox recommended)

## 📝 License

Built for awesomeness. Use it, love it, make it yours!

---

**Ready to visualize some epic timeseries data? Fire it up! 🚀**

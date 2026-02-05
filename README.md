# 🔍 Smart Image Search - Computer Vision Based Image Finder

A powerful computer vision application that enables intelligent image searching similar to **Google Photos**. Search through your image collection using object detection and advanced filtering capabilities.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.53+-red.svg)
![YOLOv11](https://img.shields.io/badge/YOLO-v11-green.svg)

## 🌟 Features

### Core Capabilities
- **Object Detection**: Automatically detect and catalog objects in your images using state-of-the-art YOLO models
- **Smart Search**: Find images based on detected objects (e.g., "apple", "person", "bus", "car")
- **Advanced Filtering**: 
  - **OR Mode**: Find images containing ANY of the selected objects.
  - **AND Mode**: Find images containing ALL selected objects simultaneously.
  - **Count Thresholds**: Filter by minimum/maximum occurrence of objects in images.
- **Visual Results**: Display search results with bounding boxes and confidence scores.
- **Metadata Export**: Save and load detection metadata for quick future searches.

### User Interface
- Clean, responsive web interface built with Streamlit
- Grid view with customizable columns (2-5)
- Hover effects and smooth animations
- Toggle bounding boxes on/off
- Highlight matching objects vs. all detected objects
- Export search results as JSON

## 📋 Table of Contents
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Configuration](#%EF%B8%8F-configuration)
- [Examples](#-examples)
- [Technical Details](#-technical-details)

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- uv package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/prakhar175/count-aware-image-search.git
cd count-aware-image-search
```

2. **Create a virtual environment (recommended)**
```bash
uv venv

.venv/Scripts/activate

```

3. **Install dependencies**
```bash
uv sync
```

## 🎯 Quick Start

### 1. Prepare Your Images
Organize your images in a directory:
```
my_photos/
├── vacation_2024/
│   ├── beach1.jpg
│   ├── beach2.png
│   └── sunset.jpg
└── family/
    ├── birthday.jpg
    └── picnic.png
```

### 2. Launch the Application
```bash
streamlit run main.py
```

### 3. Process Images
1. Select **"Process the new images"**
2. Enter your image directory path
3. Enter model path (e.g., `yolo11n.pt`, `yolo11m.pt`, `yolo11l.pt`)
4. Click **"Start Inference"**
5. Wait for processing to complete

### 4. Search Your Images
1. Select search mode (**OR** / **AND**)
2. Choose object classes from the dropdown
3. Optionally set count thresholds
4. Click **"Search Images"**
5. View and export results!

## 📖 Usage Guide

### Processing New Images

When you first use the application, you need to process your images:

1. **Image Directory Path**: Full path to your image folder
   ```
   /path/to/your/images
   Example ->
   C:\Users\prakhar\Pictures\MyPhotos  (Windows)
   ```

2. **Model Selection**: Choose a YOLO model based on your needs:
   - `yolo11n.pt` - Nano (fastest, less accurate)
   - `yolo11s.pt` - Small (balanced)
   - `yolo11m.pt` - Medium (recommended)
   - `yolo11l.pt` - Large (slower, more accurate)
   - `yolo11x.pt` - Extra Large (most accurate)

3. **Processing**: The app will:
   - Scan all images in the directory
   - Detect objects using YOLO
   - Save metadata to `processed/[dirname]/metadata.json`

### Loading Existing Metadata

Skip reprocessing by loading previously generated metadata:

1. Select **"Load existing"**
2. Enter the path to your `metadata.json` file
3. Click **"Load Metadata"**

### Search Modes

#### OR Mode (Any Match)
Finds images containing **at least one** of the selected objects.

**Example**: Select "person" OR "dog"
- ✅ Image with only a person
- ✅ Image with only a dog  
- ✅ Image with both person and dog
- ❌ Image with neither

#### AND Mode (All Match)
Finds images containing **all** selected objects simultaneously.

**Example**: Select "person" AND "dog"
- ❌ Image with only a person
- ❌ Image with only a dog
- ✅ Image with both person and dog
- ❌ Image with neither

### Count Thresholds

Refine searches by object occurrence:

**Example**: "person" with threshold "3"
- Finds images with **1-2 people** (but not 3 or more)

**Use Case**: "car" with threshold "5"
- Finds parking lots with a few cars, excludes highway traffic

### Display Options

- **Show Bounding Boxes**: Toggle object detection boxes
- **Grid Columns**: Adjust layout (2-5 columns)
- **Show Highlights**: 
  - ON: Only show boxes for searched objects
  - OFF: Show all detected objects

## 📁 Project Structure

```
smart-image-search/
│
├── main.py                 # Main Streamlit application
├── .python-version               
├── pyproject.toml        # Python dependencies
├── README.md              # This file
│
├── src/
│   ├── __init__.py
│   ├── inference.py       # YOLO inference logic
│   └── utils.py           # Utility functions
│
├── configs/
│   ├── __init__.py
│   └── config.py          # Configuration settings
│
├── data/
│   ├── raw/              # Original images
│   └── processed/        # Metadata and results
│
└── yolo11m.pt            # YOLO model weights

```

## ⚙️ Configuration

Edit `configs/config.py` to customize:

```python
# Detection confidence threshold
CONF_THRESHOLD = 0.25  # Lower = more detections, higher = more accurate

# YOLO model
YOLO_MODEL = "yolo11m.pt"

# Supported image formats
IMAGE_EXTENSION = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]
```

### Key Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `CONF_THRESHOLD` | Minimum confidence for detections | 0.25 | 0.0 - 1.0 |
| `YOLO_MODEL` | Default YOLO model | yolo11m.pt | n/s/m/l/x |
| `IMAGE_EXTENSION` | Supported formats | jpg, png, etc. | - |

## 💡 Examples

### Example 1: Find Beach Photos
```
Search Mode: OR
Selected Classes: ["person", "umbrella", "surfboard"]
Result: All beach and vacation photos
```

### Example 2: Find Family Dinners
```
Search Mode: AND
Selected Classes: ["person", "dining table", "fork"]
Result: Photos with people eating at tables
```

### Example 3: Find Pet Photos (Not Crowded)
```
Search Mode: OR
Selected Classes: ["dog", "cat"]
Thresholds: dog=3, cat=3
Result: Photos with 1-2 dogs or cats (excludes shelter/kennel photos)
```

### Example 4: Urban Street Scenes
```
Search Mode: AND
Selected Classes: ["car", "traffic light", "person"]
Result: City street photographs
```

## 🔧 Technical Details

### Detection Metadata Structure

Each processed image generates metadata:

```json
{
  "img_path": "/path/to/image.jpg",
  "detections": [
    {
      "class": "person",
      "conf": 0.89,
      "bbox": [100, 150, 300, 450],
      "count": 2
    }
  ],
  "total_objects": 5,
  "unique_classes": ["person", "car", "dog"],
  "class_counts": {
    "person": 2,
    "car": 2,
    "dog": 1
  }
}
```
If you find this project useful, please consider giving it a ⭐ on GitHub!

# Lost & Found Matching System - Project Setup Guide

## 📋 Project Overview

This is an **AI-powered Lost & Found Matching System** that helps connect lost items with found items using advanced image captioning and semantic similarity analysis.

### Key Features:
- **Automatic Image Captioning**: Uses BLIP model to generate descriptions of found items
- **Smart Matching**: Uses BERT embeddings to compare lost and found item descriptions
- **Email Notifications**: Sends automated emails when matches are found
- **Web Interface**: Streamlit-based user-friendly dashboard
- **Database Management**: SQLite database for storing items and matches

---

## 🛠️ Prerequisites

- **Python 3.11+** installed
- **Windows OS** (configured for this system)
- **~5GB free disk space** (for models and dependencies)
- **Internet connection** (for downloading pre-trained models)

---

## ⚙️ Installation & Setup

### Step 1: Navigate to Project Directory
```bash
cd c:\Users\abhij\OneDrive\Desktop\Projects\Minor_Proj
```

### Step 2: Create Virtual Environment
A virtual environment has already been created at `.venv/`

If you need to recreate it:
```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment
```bash
.venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies
```bash
.venv\Scripts\pip install streamlit transformers torch pillow scikit-learn nltk pycocotools
```

Or reinstall PyTorch CPU version specifically (if needed):
```bash
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

---

## 🚀 Running the Project

### Quick Start
```bash
cd c:\Users\abhij\OneDrive\Desktop\Projects\Minor_Proj
.venv\Scripts\python -m streamlit run MP/Implementation/main.py
```

The app will start at: **http://localhost:8502**

### Important Notes:
- ⚠️ **Always use** `.venv\Scripts\python -m streamlit run` instead of just `streamlit run`
- This ensures the virtual environment's Python and packages are used
- First load may take 1-2 minutes as models are downloaded and loaded

---

## 📁 Project Structure

```
Minor_Proj/
├── MP/
│   ├── Implementation/
│   │   ├── main.py                    # Main Streamlit application
│   │   ├── test.py                    # Test file
│   │   ├── matched_found_items/       # Folder for matched items
│   │   └── unmatched_found_items/     # Folder for unmatched items
│   │
│   ├── Training/
│   │   ├── 5_epoch/                   # Pre-trained model (BLIP)
│   │   │   ├── config.json
│   │   │   ├── model.safetensors
│   │   │   ├── preprocessor_config.json
│   │   │   ├── tokenizer_config.json
│   │   │   └── vocab.txt
│   │   ├── Generate_captions.py
│   │   ├── Testing.ipynb
│   │   └── Training.ipynb
│   │
│   └── Docs/
│
├── Image-captioning-master/           # Original image captioning code
├── Scraper/                           # Web scraping utilities
└── Docs/                              # Documentation folder
```

---

## 🔧 Configuration

### Model Paths
The models are loaded from: `c:\Users\abhij\OneDrive\Desktop\Projects\Minor_Proj\MP\Training\5_epoch`

If you move the project, update the paths in [MP/Implementation/main.py](MP/Implementation/main.py#L27-L28):

```python
model_path = r"c:\path\to\your\5_epoch"
processor = BlipProcessor.from_pretrained(model_path)
model = BlipForConditionalGeneration.from_pretrained(model_path)
```

### Email Configuration (Optional)
To enable email notifications, update in main.py:
```python
login = "your_email_api_key"
password = "your_password"
sender_email = "your_email@example.com"
```

---

## 📊 How It Works

### 1. **Found Item Submission**
- User uploads image of found item
- BLIP model generates automatic description (caption)
- Item stored in database with location and contact info

### 2. **Lost Item Reporting**
- User reports lost item with description
- Item stored in database with contact email

### 3. **Matching Process**
- BERT model converts both descriptions to semantic embeddings
- Cosine similarity calculated between embeddings
- If similarity score > threshold: Match found!

### 4. **Notification**
- Email sent to lost item reporter
- Found item moved to `matched_found_items/` folder

---

## 🐛 Troubleshooting

### Error: "DLL initialization routine failed"
**Solution**: Reinstall PyTorch CPU version
```bash
.venv\Scripts\pip uninstall torch -y
.venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Error: "Model path not found"
**Solution**: Update the model path in main.py to your current location

### Error: "Streamlit command not found"
**Solution**: Always use the full venv path:
```bash
.venv\Scripts\python -m streamlit run MP/Implementation/main.py
```

### App runs slowly on first load
**Normal behavior** - Models are being downloaded and loaded. This only happens once.

### Missing image files error
**Already fixed** - Image display lines have been commented out. You can add images later if needed.

---

## 📝 Main Application Features (main.py)

### Database Functions:
- `add_found_item()` - Add found items to database
- `add_lost_item()` - Add lost items to database
- `get_found_items()` - Retrieve found items
- `get_lost_items()` - Retrieve lost items

### AI Functions:
- `generate_caption()` - Generate description from image using BLIP
- `get_sentence_embedding()` - Get BERT embedding for text
- `compare_descriptions()` - Calculate similarity between descriptions

### Utility Functions:
- `send_email()` - Send notification emails
- `move_to_matched()` - Move matched items to folder

---

## 🔐 Important Security Notes

⚠️ **The API key and password are hardcoded in main.py**
- Do NOT commit this file to public repositories
- Update email credentials before deployment
- Consider using environment variables for sensitive data

---

## 📱 Using the Web Interface

### Home Page
- Upload image to report found item
- View statistics and recent matches

### Report Lost Item
- Enter item description
- Provide contact information
- System automatically searches for matches

### View Matches
- See all matched pairs
- View similarity scores
- Download or export results

### Admin Panel (if enabled)
- View all database entries
- Manage items
- Monitor email notifications

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | Latest | Web interface |
| transformers | Latest | BLIP & BERT models |
| torch | 2.10.0+cpu | Deep learning framework |
| pillow | Latest | Image processing |
| scikit-learn | Latest | Similarity calculations |
| nltk | Latest | NLP utilities |
| pycocotools | Latest | Dataset handling |

---

## 🔄 Updating the Project

To update packages:
```bash
.venv\Scripts\pip install --upgrade streamlit transformers torch
```

To check installed packages:
```bash
.venv\Scripts\pip list
```

---

## 📞 Support & Next Steps

### If Something Goes Wrong:
1. Deactivate venv: `deactivate`
2. Delete `.venv` folder
3. Recreate from Step 2 above
4. Reinstall packages from Step 4

### Future Enhancements:
- Add GPU support (CUDA)
- Implement user authentication
- Add mobile app
- Deploy to cloud (AWS/Azure)
- Add more notification channels (SMS, WhatsApp)

---

## 📄 Additional Documentation

- **Image Captioning**: See `Image-captioning-master/README.md`
- **Training**: See `MP/Training/Training.ipynb`
- **Testing**: See `MP/Implementation/test.py`

---

## ✅ Checklist for Running Again

- [ ] Navigate to project directory
- [ ] Activate virtual environment: `.venv\Scripts\Activate.ps1`
- [ ] Run: `.venv\Scripts\python -m streamlit run MP/Implementation/main.py`
- [ ] Open: `http://localhost:8502`
- [ ] App loads successfully

---

**Last Updated**: February 15, 2026  
**Status**: ✅ Working and Tested

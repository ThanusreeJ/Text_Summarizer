# 📝 Text Summarizer Pro

An advanced web-based application that automatically summarizes documents, translates text into multiple languages, and converts summaries to audio format using AI-powered models.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-red.svg)

## 🌟 Features

### 1. **Document Summarization**
- Upload **PDF** or **DOCX** files, or paste text directly
- Customize summary length from **50 to 400 words**
- Three quality modes:
  - **Fast**: Quick processing
  - **Balanced**: Optimal quality and speed
  - **High Quality**: Best results
- Automatically handles long documents by intelligent chunking
- **Copy to clipboard** or **download as .txt** file

### 2. **Multi-Language Translation**
- Translate your summaries into **8 languages**:
  - English, Spanish, French, German, Hindi, Chinese, Japanese, Portuguese
- Powered by Helsinki-NLP translation models
- Download translated summaries as text files

### 3. **Text-to-Speech Audio**
- Convert summaries to **MP3 audio** files
- Support for **5 languages**: English, Spanish, French, German, Hindi
- Play audio directly in the browser
- Download audio files for offline listening

## 🖼️ Screenshots

### Main Interface
**📸 Screenshot 1**: Landing page with gradient header

![Landing Page](https://drive.google.com/uc?export=view&id=1keR3AT5IauQa9uV9yZm9WNr_NeTSwmAj)


### Summarization Feature
**📸 Screenshot 2**: Text input area with paste option

![Paste Text](https://drive.google.com/uc?export=view&id=1gK14uA44qk2CUzhPS-3l4X3s9XLXFAWk)

**📸 Screenshot 3**: File upload interface (PDF/DOCX)

![Screenshot](https://drive.google.com/uc?export=view&id=1qc6WgvnXaakqQJkTEiSlWIxJ1b1e8CxE)



### Translation Feature
**📸 Screenshot 5**: Translation interface with language selection

![Screenshot](https://drive.google.com/uc?export=view&id=1VPR83IW2jTukKOXsBR7_LIJWZw6XfbI_)


**📸 Screenshot 6**: Translated summary output

![Screenshot](https://drive.google.com/uc?export=view&id=1P3FO3GKrxTKgkkYh0VR9js4vVv1qzhiQ)


### Audio Feature
**📸 Screenshot 7**: Audio generation interface

![Screenshot](https://drive.google.com/uc?export=view&id=1R6b0q4HVhF4RSg7CN4Gmn7Xy0y4PLsvO)


**📸 Screenshot 8**: Audio player with download option

![Screenshot](https://drive.google.com/uc?export=view&id=16OG5zmZ7scDoysNSJfcVEpdpE1HRIb8A)


### Sidebar Settings
**📸 Screenshot 9**: Sidebar with all settings and feature toggles

![Description of Image](https://drive.google.com/uc?export=view&id=1Z8PUIKK8e5-fRaVBuB9BgIYu147LGdzl)


## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Hugging Face account (free)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/Text_Summarizer.git
cd Text_Summarizer
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Hugging Face API Token
1. Create account at https://huggingface.co/join
2. Generate token at https://huggingface.co/settings/tokens
3. Set environment variable:

**Windows (Command Prompt):**
```cmd
set HF_API_TOKEN=your_token_here
```

**Windows (PowerShell):**
```powershell
$env:HF_API_TOKEN="your_token_here"
```

**macOS/Linux:**
```bash
export HF_API_TOKEN=your_token_here
```

**Permanent Setup (Recommended):**
- **Windows**: Add to System Environment Variables
- **macOS/Linux**: Add to `~/.bashrc` or `~/.zshrc`

### Step 5: Run Application
```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

## 📖 How to Use

### Summarizing Documents

#### Option 1: Paste Text
1. Open the app and go to **"Summarize"** tab
2. Select **"Paste Text"** option
3. Paste or type your content in the text area
4. Adjust settings in sidebar:
   - Set desired summary length (slider)
   - Choose quality mode (dropdown)
5. Click **"Summarize"** button
6. Wait for processing (spinner will show progress)
7. View your summary in the blue box
8. **Copy** summary to clipboard or **Download** as .txt file


#### Option 2: Upload File
1. Go to **"Summarize"** tab
2. Select **"Upload File"** option
3. Click **"Browse files"** and select your PDF or DOCX file
4. App will show word count after successful upload
5. Adjust settings in sidebar if needed
6. Click **"Summarize"** button
7. View and export your summary


### Translating Summaries

1. First, generate a summary using the **"Summarize"** tab
2. Go to **Sidebar** and enable **"Enable Translation"** checkbox
3. Switch to **"Translate"** tab
4. Select **source language** (From dropdown)
5. Select **target language** (To dropdown)
6. Click **"Translate"** button
7. View translated text in the result box
8. Download translated summary as text file



### Generating Audio

1. First, generate a summary using the **"Summarize"** tab
2. Go to **Sidebar** and enable **"Enable Audio Summary"** checkbox
3. Switch to **"Audio"** tab
4. Select desired **audio language** from dropdown
5. Click **"Generate Audio"** button
6. Audio player will appear automatically
7. Play audio in browser or download MP3 file



## ⚙️ Settings

### Sidebar Configuration

**Summarization Settings:**
- **Desired summary length**: Slider to choose 50-400 words
- **Quality vs. speed**: 
  - Fast (quickest)
  - Balanced (recommended)
  - High quality (best results)

**Feature Toggles:**
- **Enable Translation**: Check to use translation feature
- **Enable Audio Summary**: Check to use audio feature



## 🛠️ Technology Stack

- **Frontend**: Streamlit 1.38.0
- **AI Models**: 
  - Summarization: `sshleifer/distilbart-cnn-12-6`
  - Translation: `Helsinki-NLP/opus-mt-*`
- **Document Processing**: PyPDF, python-docx
- **Text-to-Speech**: Google TTS (gTTS)
- **API**: Hugging Face Inference API

## 🔧 Troubleshooting

### Issue: "HF_API_TOKEN not set" error
**Solution**: Make sure you've set the environment variable correctly and restarted your terminal

### Issue: Summary takes too long
**Solution**: 
- Try "Fast" quality mode
- Reduce summary length
- Check your internet connection

### Issue: PDF extraction returns empty text
**Solution**: 
- PDF might be a scanned image (needs OCR)
- PDF might be password-protected
- Try copying text manually

### Issue: Translation/Audio tab shows warning
**Solution**: 
- Enable the feature in the sidebar first
- Generate a summary in "Summarize" tab before using these features

## 📋 Requirements

```
--extra-index-url https://download.pytorch.org/whl/cpu

streamlit>=1.38.0
requests>=2.31.0
pypdf>=4.2.0
python-docx>=1.1.2
google-cloud-texttospeech>=2.14.0
pillow>=10.0.0
plotly>=5.17.0
gtts>=2.4.0
```


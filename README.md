# 📊 PDF & Excel Report Generator + Email Scheduler

> Upload any CSV or Excel file. Configure your report.
> Get a formatted PDF + Excel report sent to your inbox — automatically.

![Demo](assets/demo.gif)

## ✨ Features
- 📂 Upload any CSV or Excel dataset
- 📄 Auto-generates formatted **PDF reports** with charts + tables
- 📊 Auto-generates styled **Excel reports** with 3 sheets + chart
- 📧 Sends reports via Gmail to any list of recipients
- ⏰ Schedule daily / weekly / monthly automated delivery
- ⬇️ Download reports directly from the browser
- 🎨 Animated dark-theme UI — simple enough for non-technical users

## 🚀 Live Demo
**[Try it here →](YOUR_STREAMLIT_URL)**

## 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Data processing | pandas |
| PDF generation | ReportLab + matplotlib |
| Excel generation | openpyxl |
| Email delivery | smtplib (Gmail SMTP) |
| Scheduling | APScheduler |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

## 📁 Project Structure
```
report-generator/
├── app/
│   ├── reader.py         # CSV/Excel loader
│   ├── pdf_report.py     # PDF generation engine
│   ├── excel_report.py   # Excel generation engine
│   ├── mailer.py         # Gmail SMTP sender
│   └── scheduler.py      # APScheduler pipeline
├── assets/
│   ├── styles.css        # Animated dark UI styles
│   └── demo.gif          # Demo recording
├── data/
│   ├── sales_data.csv    # Sample dataset
│   └── employee_data.xlsx
├── outputs/              # Generated reports (gitignored)
├── app.py                # Streamlit entry point
├── config.json           # Client configuration
└── requirements.txt
```

## ⚙️ Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/report-generator
cd report-generator
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Gmail + App Password
streamlit run app.py
```

### Windows
```powershell
git clone https://github.com/YOUR_USERNAME/report-generator
cd report-generator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # fill in your Gmail + App Password
streamlit run app.py
```

## 📧 Gmail Setup (required for email sending)
1. Enable 2-Factor Authentication on your Google account
2. Go to: Google Account → Security → App Passwords
3. Generate a password for "Mail"
4. Add to `.env`: `APP_PASSWORD=your_16_char_password`

## 💡 Use Cases
| Client type | What they automate |
|-------------|-------------------|
| Sales teams | Weekly revenue reports to manager |
| Accountants | Monthly expense summaries to clients |
| School admins | Attendance reports to parents |
| Logistics firms | Daily delivery stats to operations |
| Small businesses | Any recurring data → email workflow |

## 📬 Built by
Yash Chavda — B.Tech CSE, Karnavati University  
Intern @ IIT Gandhinagar (Makers Bhavan)  
[LinkedIn](YOUR_LINKEDIN) · [GitHub](YOUR_GITHUB)

---

Replace `YOUR_STREAMLIT_URL`, `YOUR_USERNAME`, `YOUR_LINKEDIN`, and `YOUR_GITHUB` with real links before publishing.

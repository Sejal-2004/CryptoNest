# CryptoNest 🪙  
*A Flask-based Crypto Portfolio & Market Tracking Web Application*

---

## 📌 Project Overview

**CryptoNest** is a web-based application developed as part of the  
**Infosys Springboard Internship 6.0 (Batch 4)**.

The project focuses on building a **secure, responsive, and user-friendly crypto tracking platform** that allows users to register, log in, and explore live cryptocurrency market data using a real-world API.

This project is currently **not deployed** and is intended to run on a **local development environment**, as deployment is **not mandatory for the internship**.

---

## 🎯 Objectives of the Project

- To understand **Flask framework fundamentals**
- To implement **user authentication (Signup & Login)**
- To integrate a **live cryptocurrency API**
- To structure a **professional full-stack project**
- To follow **industry-level folder organization**
- To gain experience with **real-time data fetching**

---

## 🛠️ Tools & Technologies Used

### 🔹 Backend
- **Python**
- **Flask**
- **Flask-SQLAlchemy**
- **Flask-Login**
- **Werkzeug (Password Hashing)**

### 🔹 Frontend
- **HTML5**
- **CSS3**
- **JavaScript**
- **Font Awesome Icons**
- **Responsive Design (Mobile Friendly)**

### 🔹 Database
- **SQLite** (Local database)

### 🔹 API
- **CoinGecko Live Crypto API**
  - Used to fetch real-time cryptocurrency prices
  - No API key required
  - Reliable and free crypto market data

### 🔹 Development Tools
- **VS Code**
- **GitHub**
- **Jupyter Notebook (initial testing)**

---

## 📁 Project Folder Structure

cryptonest/
│
├── app.py
├── requirements.txt
│
├── templates/
│ ├── index.html
│ ├── login.html
│ ├── signup.html
│ └── dashboard.html
│
└── static/
├── css/
│ └── style.css
└── js/
   └── auth.js
   └── dashboard.js
   └── main.js

   
---

## ✨ Features Implemented

### 🔐 Authentication
- User Signup with hashed passwords
- Secure Login system
- Session management using Flask-Login
- Logout functionality

### 📊 Crypto Features
- Live cryptocurrency price tracking
- Data fetched from **CoinGecko API**
- Real-time updates without page reload (JS based)

### 🎨 UI / UX
- Clean & professional UI
- Responsive design (mobile, tablet, desktop)
- Interactive components
- Professional footer & navigation bar

### ⚙️ Backend Logic
- Database initialization
- Error handling
- Secure route protection
- API data processing

---

## 🔄 How the Project Works

1. **User opens the application**
2. Home page (`index.html`) loads
3. User can:
   - Sign up
   - Log in
4. Authentication data is:
   - Stored securely in SQLite database
   - Passwords are hashed
5. After login:
   - User is redirected to dashboard
   - Live crypto data is fetched from CoinGecko API
6. JavaScript handles API requests & UI updates
7. Flask manages routing, sessions, and backend logic

---

## 🌐 Live API Details

- **API Name:** CoinGecko API
- **Purpose:** Fetch live cryptocurrency prices
- **Why CoinGecko?**
  - Free
  - No API key required
  - Reliable real-time data
- **Status:** Actively used in the project

---

## 🚀 How to Run the Project Locally

### Step 1: Clone the Repository
```bash
git clone https://github.com/Sejal-2004/CryptoNest
cd cryptonest
### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
Step 3: Run the Application
bash
Copy code
python app.py
Step 4: Open in Browser
cpp
Copy code
http://127.0.0.1:5000/
📌 Deployment Status
❌ Not Deployed

Deployment is not required as per internship guidelines.
The project is fully functional in a local development environment.

📚 Learning Outcomes
Hands-on experience with the Flask framework

Understanding of MVC architecture

Live API integration in real-world projects

Basics of authentication and security

Professional project structuring

GitHub version control practices

👩‍💻 Developer Information
Name: Sejal Singh
Internship: Infosys Springboard Internship 6.0 (Batch 4)

📧 Email:
sejalsingh8647@gmail.com

🔗 LinkedIn Profile:
https://linkedin.com/in/sejal-singh-97669b314

🙏 Acknowledgement
I would like to thank Infosys Springboard for providing this internship opportunity and learning resources, which helped me build this project and strengthen my practical development skills.

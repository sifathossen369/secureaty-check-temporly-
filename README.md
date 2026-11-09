# 🛰️ NexusCore v2.0 // Autonomous DevSecOps Swarm

> **The Zero-Trust Autonomous Agent Swarm with Self-Healing Intelligence, Live Attack Simulator & Sci-Fi HUD.**

---

## ⚡ Quick Start (১ ক্লিকে রান করুন)

### Option 1: Double-click `run.bat`
Windows-এ সরাসরি `run.bat` ফাইলটিতে ডাবল ক্লিক করুন। এটি স্বয়ংক্রিয়ভাবে ডিপেনডেন্সি ইন্সটল করে ব্রাউজারে `http://localhost:8000` ড্যাশবোর্ড ওপেন করবে।

### Option 2: Manual Command
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```
এরপর ব্রাউজারে যান: **[http://localhost:8000](http://localhost:8000)**

---

## 🤖 The 4 Specialized Agents

| এজেন্ট | ভূমিকা | কাজ |
| :--- | :--- | :--- |
| **🕵️ SCOUT** | Researcher & Architect | ইউজারের টাস্ক বিশ্লেষণ করে সিকিউর আর্কিটেকচারাল ব্লুপ্রিন্ট তৈরি করে। |
| **💻 BUILDER** | Software Engineer | পাইথন সোর্স কোড লেখে এবং গার্ডিয়ানের আদেশে **Autonomous Self-Healing** করে। |
| **🛡️ GUARDIAN** | Security Sentinel | গেটকিপার এজেন্ট। AST ও রেগুলার এক্সপ্রেশন দিয়ে ক্ষতিকর কোড আটকে দেয় এবং Side-by-Side Diff তৈরি করে। |
| **🧪 AUDITOR** | QA & Sandbox Tester | ইন-মেমোরি এপিমেরাল স্যান্ডবক্সে সত্যিকারের ইউনিট টেস্ট রান করায়। |

---

## 🏆 হ্যাকাথনে ২ মিনিটের লাইভ ডেমো (The Winning Script)

1. ব্রাউজারে ড্যাশবোর্ড খুলুন: `http://localhost:8000`।
2. বিচারককে বলুন: *"স্যার, আপনি ডানপাশের লাল বাটন **`[SQL Injection]`** এ ক্লিক করে দেখুন।"*
3. ক্লিক করলেই পুরো স্ক্রিনে **লাল সাইরেন বাজবে ও থ্রেট অ্যালার্ট উঠবে**।
4. স্ক্রিনের সেন্টারে দেখা যাবে:
   - **বামে (লাল):** কোডার এজেন্টের অনিরাপদ কোড (`SELECT * FROM users WHERE username = ' + username + '`).
   - **ডানে (সবুজ):** গার্ডিয়ান এজেন্টের নির্দেশে কোডার নিজের ভুল নিজে শুধরে নেওয়া প্যারামিটারাইজড কোড (`SELECT * FROM users WHERE username = ?`).
5. **Auditor** নোড স্যান্ডবক্সে টেস্ট রান করে সবুজ সংকেত দেবে: **`4/4 Tests Passed in 1.4ms`**!

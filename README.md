# SH-Adv-Filter-Bot-V1
​🤖 ප්‍රබල Telegram File Search Bot පද්ධතියක්. GitHub Actions මගින් නොමිලේ 24/7 ක්‍රියාත්මක වේ. Search in groups, receive in private!

<p><b>Developed with ❤️ by Sadesha Hansana</b></p>
</div>

  <center><p><b>GitHub Actions හරහා 24/7 ක්‍රියාත්මක වන ප්‍රබල Telegram File Search Bot පද්ධතිය.</b></p></center>
</div>

---

## 🍴 මෙම Repository එක Fork කර භාවිතා කරන්නේ කෙසේද? (How to Fork)

ඔබත් මෙම බොට්ව භාවිතා කිරීමට කැමති නම්, පහත පියවරවල් අනුගමනය කර ඔබේම බොට් කෙනෙකු සාදා ගන්න.

### 1️⃣ Repository එක Fork කරන්න
ඉහළ දකුණු කෙළවරේ ඇති **Fork** බොත්තම ඔබා මෙම ව්‍යාපෘතිය Private ලෙස යොදා ඔබේ GitHub ගිණුමට පිටපත් කරගන්න.
🚫විශේශ කරුනු.
Repo එක Public නොදමන්න

### 2️⃣ ඔබේ තොරතුරු ඇතුළත් කරන්න (Edit `bot.py`)
ඔබේ Fork කළ Repository එකේ ඇති `bot.py` ගොනුව විවෘත කර එහි ඇති පහත තැන් ඔබේ දත්ත වලින් වෙනස් කරන්න:
* `BOT_TOKEN`: @BotFather මගින් ලබාගත් ඔබේ බොට්ගේ Token එක.
* `ADMIN_ID`: ඔබේ Telegram User ID එක.

### 3️⃣ GitHub Actions Permissions ලබා දෙන්න (අතිශය වැදගත්!)
බොට්ගේ දත්ත (Database) සුරැකීමට නම් ඔබ GitHub වෙත ලිවීමේ අවසරය ලබා දිය යුතුය:
1. Repository එකේ **Settings** ටැබ් එකට යන්න.
2. වම්පස මෙනුවේ **Actions** -> **General** වෙත යන්න.
3. පිටුවේ පහළට ගොස් **Workflow permissions** යටතේ **"Read and write permissions"** යන්න තෝරා **Save** කරන්න.

---



## 🚀 විශේෂාංග (Features)

* **⚡ 24/7 Online:** GitHub Actions මගින් නොකඩවා ක්‍රියාත්මක වේ.
* **💾 Reboot-Safe:** Bot නැවතුණත් SQLite Database එක නිසා දත්ත ආරක්ෂිතයි.
* **🛡️ Group Privacy:** Group එකේ සෙවුම් කර ප්‍රතිඵල Inbox එකට ලබාදේ.
* **🗑️ Auto-Delete:** විනාඩි 10 කින් පසු File මැකී යන පහසුකම.

---

## 🛠️ GitHub Workflow සැකසුම

මෙම Bot එක ක්‍රියාත්මක කිරීමට ඔබේ Repository එකේ `.github/workflows/main.yml` ලෙස පහත කේතය සුරකින්න.

```yaml
name: Telegram Bot 24/7 Deployment

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 */6 * * *' 
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest
    permissions:
      contents: write 

    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: pip install python-telegram-bot

      - name: Run Bot with Timeout
        run: |
          timeout 21000s python bot.py || echo "Saving data..."

      - name: Auto-Save Database
        if: always()
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action Bot"
          git add bot_database.db
          git commit -m "Update DB: $(date)" || echo "No changes"
          git push

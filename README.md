# SH-Adv-Filter-Bot-V1
​🤖 ප්‍රබල Telegram File Search Bot පද්ධතියක්. GitHub Actions මගින් නොමිලේ 24/7 ක්‍රියාත්මක වේ. Search in groups, receive in private!

<p><b>Developed with ❤️ by Sadesha Hansana</b></p>
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/render?type=distort&color=gradient&height=200&section=header&text=Telegram%20File%20Bot&fontSize=60&animation=twinkling" width="100%">

  <p><b>GitHub Actions හරහා 24/7 ක්‍රියාත්මක වන ප්‍රබල Telegram File Search Bot පද්ධතිය.</b></p>
</div>

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

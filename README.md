## ERROR REPEROT TO @moire_logs


## 🖇 VPS Deployment
- ganti semua isi config.py sama punya lu kalo udah lanjut dibawah
- clone repo :
```
git clone https://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@github.com/jerzzoffc/hydrobot && cd hydrobot
```
- Setup Vps (Jalankan hanya sekali) :
```
bash setup.sh
```
```
tmux new-session -s hydrobot
```
```
python3 -m venv hydrobot && source hydrobot/bin/activate
```
```
pip install filetype
```
```
pip3 install -U pip
```
```
pip3 install --no-cache-dir -r req.txt
```
```
pip3 install geopy
```
```
bash start.sh
```
- Klik CTRL B + D di keyboard Vps

# Cara buka cek log userbot di vps
Ketik 
```
tmux a -t ubotlitex
```

# Note:
  Kalo ada eror "sqlite3.OperationalError: unable to open database file" buka vps terus ketik
```
tmux a -t ubotlitex
```
- Klik CTRL + C
- Lanjut
```
bash start.sh
```
- close vps




# Fitur asupan, porn, bing-img, gemini memakai api. Silahkan buat sendiri jika api mati

# Kalo divps gunicorn nya belom connect atau log divps kaya gini "Retrying in 1 seconds" ketik
```
pkill -f gunicorn
```
baru
```
bash start.sh
```

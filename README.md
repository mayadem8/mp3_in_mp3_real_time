# MP3-in-MP3 Real-Time Audio Detection

This project listens to live microphone audio and detects whether a **known MP3 track**

It uses [`audfprint`](https://github.com/dpwe/audfprint) for generating and matching audio fingerprints

---

## Project Structure

audfprint/ → audio fingerprinting library

targets/ → MP3 target files to be detected

fpdb.pklz → fingerprint database

live_listener.py → main backend script

requirements.txt → dependencies

---

## Installation

Clone the repository
```bash
git clone https://github.com/mayadem8/mp3_in_mp3_real_time.git
cd mp3_in_mp3_real_time
```

Install dependencies
```bash
pip install -r requirements.txt
```


Start the real-time listener
```bash
python live_listener.py
```

You should see logs such as:

Starting real-time listener (Ctrl+C to stop)...

please wait 1-2 seconds



The backend continuously records short microphone snippets.

Each snippet is fingerprinted and compared to the database in fpdb.pklz.

If a match is found, you’ll see something like:
```bash
[0:00:08] Match (offset +0.3s)
```
if not: 
```bash
[0:00:08] NOMATCH
```


Example Output: 
```bash
(win 0:00:03–0:00:08) NOMATCH
(win 0:00:04–0:00:09) NOMATCH
(win 0:00:05–0:00:10) NOMATCH
(win 0:00:06–0:00:11) NOMATCH
(win 0:00:07–0:00:12) START aligned=0:00:10
(win 0:00:07–0:00:12) MATCH aligned=0:00:10 (offset -1.9s)
(win 0:00:08–0:00:13) MATCH aligned=0:00:14 (offset +1.4s)
(win 0:00:09–0:00:14) MATCH aligned=0:00:18 (offset +4.9s)
(win 0:00:10–0:00:15) NOMATCH
(win 0:00:11–0:00:16) NOMATCH
 END at 0:00:20   segment: 0:00:10–0:00:20
 DURATION: 0:00:10 (10.80s)
```





# Results uitslagen.atletiek.nl
 Parse data from [uitslagen.atletiek.nl](https://uitslagen.atletiek.nl)

 This program loads all the results and competitors for a given competition ID. It outputs a JSON formatted string that contains a list of all competitors, also see [example.json](example.json). The JSON string is also automatically copied to clipboard.

 ```json
[
  {
    "bib": "111",
    "birthyear": "2000",
    "category": "M55",
    "club": "Association Name",
    "gender": "male",
    "name": "Full Name",
    "results": [
      {
        "event": "60m",
        "result": "9,99",
        "url": "https://uitslagen.atletiek.nl/Competitions/CurrentList/xxxxx/xxxx"
      },
      {
        "event": "50m Horden",
        "result": "10,50",
        "url": "https://uitslagen.atletiek.nl/Competitions/CurrentList/xxxxx/xxxx"
      },
      {
        "event": "Hoogspringen",
        "result": "1,10",
        "url": "https://uitslagen.atletiek.nl/Competitions/CurrentList/xxxxx/xxxx"
      }
    ]
  },
  {
    "bib": "112",
    "birthyear": "1965",
    "category": "U18V",
    "club": "Association Name",
    "gender": "female",
    "name": "Full Name",
    "results": [
      {
        "event": "50m Horden",
        "result": "9,50",
        "url": "https://uitslagen.atletiek.nl/Competitions/CurrentList/xxxxx/xxxx"
      }
    ]
  }
]
```

# Installing
1. Clone the repo
```
git clone https://github.com/nilsbebelaar/Results-uitslagen.atletiek.nl
```
2. Create and activate a virtual environment to install the required libraries (optional)(asuming a Powershell terminal)
```Powershell
python -m venv .venv
.\.venv\Scrips\Activate.ps1
```
3. Install the libraries
```Powershell
pip install -r .\requirements.txt
```

# Usage
1. Edit the `COMP_ID` on line 5 of `main.py` to the ID of the desired competition.
2. Run the program, the JSON output will be printed out to the terminal and copied to clipboard.
```Powershell
python main.py
```
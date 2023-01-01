# Results uitslagen.atletiek.nl
 Parse data from [uitslagen.atletiek.nl](https://uitslagen.atletiek.nl)

 This program loads all the results and competitors for a given competition ID. It outputs a JSON formatted string that contains a list of all competitors, also see [example.json](example.json). The JSON string is also automatically copied to clipboard.

 ```json
[
  {
    "SELTECLOOKUP": "1",
    "bib": "111",
    "birthyear": "2000",
    "category": "M55",
    "club": "Association Name",
    "competition": {
      "location": "City",
      "name": "Competition Title",
      "type": "indoor",
      "url": "https://uitslagen.atletiek.nl/Competitions/Details/xxxx"
    },
    "gender": "male",
    "name": "Full Name",
    "results": [
      {
        "date": "dd-mm-yyyy",
        "event": "50m horden 91cm",
        "result": "10,50",
        "url": "https://uitslagen.atletiek.nl/Competitions/CurrentList/xxxxx/xxxx"
      },
      {
        "date": "dd-mm-yyyy",
        "event": "60m",
        "result": "9,99",
        "url": "https://uitslagen.atletiek.nl/Competitions/CurrentList/xxxxx/xxxx"
      },
      {
        "date": "dd-mm-yyyy",
        "event": "hoogspringen",
        "result": "1,10",
        "url": "https://uitslagen.atletiek.nl/Competitions/CurrentList/xxxxx/xxxx"
      }
    ]
  },
  {
    "SELTECLOOKUP": "1",
    "bib": "112",
    "birthyear": "2000",
    "category": "U18V",
    "club": "Association Name",
    "competition": {
      "location": "City",
      "name": "Competition Title",
      "type": "outdoor",
      "url": "https://uitslagen.atletiek.nl/Competitions/Details/xxxx"
    },
    "gender": "female",
    "name": "Full Name",
    "results": [
      {
        "date": "dd-mm-yyyy",
        "event": "60m",
        "result": "10,50",
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
3. Install the required libraries
```Powershell
pip install -r .\requirements.txt
```

# Usage
1. Edit the `COMP_ID` and `COMP_TYPE` on line 8 and 9 of `main.py` to the ID and TYPE (indoor/outdoor) of the desired competition.
2. Run the program, the JSON will be exported to a file: `/export/export_<ID>.json`. JSON is also copied to clipboard automatically.
```Powershell
python main.py
```
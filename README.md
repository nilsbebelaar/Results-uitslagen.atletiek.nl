# Results uitslagen.atletiek.nl
 Parse data from [uitslagen.atletiek.nl](https://uitslagen.atletiek.nl)

 This program loads all the results and athletes for a given competition ID. It outputs a JSON formatted string that contains a list of all athletes, also see [example.json](example.json).

 ```json
[
  {
    "SELTECLOOKUP": "1",
    "bib": "111",
    "birthyear": "2000",
    "birthdate": "25-01-2000",
    "category": "M55",
    "club": "Association Name",
    "country": "NL",
    "sex": "male",
    "firstname": "Voornaam",
    "lastname": "Achternaam",
    "licencenumber": "1111111",
    "competition": {
      "location": "City",
      "name": "Competition Title",
      "url": "https://uitslagen.atletiek.nl/Competitions/Details/xxxx"
    },
    "results":[
      {
        "attempts": [
          {
            "result": "x",
            "wind": "-0,4"
          },
          {
            "result": "7,36",
            "wind": "-0,6"
          },
          {
            "result": "7,19",
            "wind": "-1,6"
          },
          {
            "result": "7,37",
            "wind": "0,0"
          },
          {
            "result": "x",
            "wind": "0,0"
          },
          {
            "result": "7,48",
            "wind": "0,0"
          }
        ],
        "best_attempt": [
          {
            "result": "7,48",
            "wind": "0,0"
          }
        ],
        "date": "dd-mm-yyyy",
        "event": "long jump",
        "event_raw": "Long Jump Men Final",
        "url": "https://uitslagen.atletiek.nl/Competitions/CurrentList/xxxxx/xxxx"
      }
    ]
  },
  {
    "SELTECLOOKUP": "1",
    "bib": "111",
    "birthyear": "2000",
    "birthdate": "25-01-2000",
    "category": "M55",
    "club": "Association Name",
    "country": "NL",
    "sex": "male",
    "firstname": "Voornaam",
    "lastname": "Achternaam",
    "licencenumber": "1111111",
    "competition": {
      "location": "City",
      "name": "Competition Title",
      "url": "https://uitslagen.atletiek.nl/Competitions/Details/xxxx"
    },
    "results": [
      {
        "attempts": "",
        "best_attempt": {
          "result": "52,56",
          "wind": ""
        },
        "date": "dd-mm-yyyy",
        "event": "400m",
        "event_raw": "400m Women Heats",
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
2. Run the program, the JSON will be exported to a file: `app/static/export/<ID>.json`. JSON is also copied to clipboard automatically.
```Powershell
python main.py
```
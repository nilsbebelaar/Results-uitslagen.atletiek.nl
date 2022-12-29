# Results uitslagen.atletiek.nl
 Parse data from [uitslagen.atletiek.nl](https://uitslagen.atletiek.nl)

 This program loads all the results and competitors for a given competition ID. It outputs a JSON formatted string that contains a list of all competitors:

 ```json
[
   {
      "bib":"111",
      "name":"Full Name",
      "club":"Association Name",
      "birthyear":"2000",
      "results":[
         {
            "event":"60m",
            "result":"9,99"
         },
         {
            "event":"50m Horden",
            "result":"10,50"
         },
         {
            "event":"Hoogspringen",
            "result":"1,10"
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
2. Run the program, the JSON output will be printed out to the terminal.
```Powershell
python main.py
```
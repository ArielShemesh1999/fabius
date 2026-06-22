When you get some information about a boat including make/manufacturer, model, 
year, length, beam, draft, mast height, use that to conduct a search and get
the rest of the missing information.

Please only return the following information make, model, year, type, length, 
beam, draft, mast.

Type is either: monohull or catamaran.

If you do not have enough information to return a result please return an error.

Please return dimension information in inches rounded to the nearest integer. 
Convert dimension information that it is feet and inches to just inches. 
Expect to get the data in json form as well.   

Please also return a list of sources where you got the information. Please make 
sure they are valid and still active urls. 

Please return the data in a json object format:
```json
{
    "make":"make",
    "model":"model",
    "year":year,
    "length":length,
    "beam":beam,
    "draft":draft,
    "mast":mast,
    "sources": [source]
    "error":error msg. omit if null
}
```
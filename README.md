# blaze_loader
Easily save and load Blaze Data objects.

Copy-pasting the code needed to genereate [Blaze](www.github.com/blaze/blaze) Data objects to every new file can be cumbersome, especially when you are dealing with many data sources. Worse, in the event of a change in a table schema or connection credential, going through all your files to update the datashapes and connection arguments of affected Blaze Data objects is painful. `blaze_loader` is a wrapper class for saving connection information and easily importing and loading Blaze data objects. 

To save connection information, pass a name (anything you want) and target string to the `save_blaze_info` method. The target string can point towards any data storage backend that Blaze can handle. You can also pass `save_blaze_info` the optional keyword arguments `table` (specify a table to use in a SQL connection), `schema` (specify a schema to use in SQL connection), `columns` (only create Data object with a subset of the available columns in a SQL connection), and `datashape` (define the [datashape](www.github.com/blaze/datashape) that Blaze will use to represent your data in its expression engine).
```
from blaze_loader import blaze_loader

blaze_loader.save_blaze_info('users', 'postgresql://foo:bar@db.com:5432/data', table='users', schema='funnel', 
							  datashape='var * name:string, log_ins: int64')

blaze_loader.save_blaze_info('purchases', 'purchases.csv')
```
To load and use your Data objects, use the `load` method on blaze_loader. 

```
db = blaze_loader.load()

db.users[db.users.name == ‘theandycamps’]

# To see what Data objects have been loaded, you can call:
print(db)
```
After you save your first Data target info, you’ll notice that `blaze_loader` created a file called `databases.json` in the `/blaze_loader` directory of your local copy of this repo. If you'd like to put your target Data info cache elsewhere, you can pass an alternative path to the `load` and `save_blaze_info` methods using the `target_info_path=` keyword argument. This cache file must have a `.json` file extension.

Note that if you included sensitive credentials in a connection string passed save_blaze_info, these creds will be saved in cleartext to your `databases.json` file. To prevent this from happening, you can create a separate file or class containing connection strings and pass attribute names from that class to bz_loader.save_blaze_info in place of a connection string. To use separately stored creds, pass the connection creds class to the `load` method with the `config=` keyword argument. This pattern can be handy when distributing code, as each user can use their own credentials to load Data objects.

```
class ConnectionCreds():
	main_db = “postgres://…”
	other_db = “mysql://…”

blaze_loader.save_blaze_info(‘u’, 'main_db', 'users', schema='funnel', 
							  datashape='var * name:string, log_ins: int64')
db = blaze_loader.load(config=ConnectionCreds)
```

Blaze Data objects are lazily loaded attributes of the instance you create when calling `blaze_loader.load()`. This means that the Data object is not actually created until you call for it. Lazy loading is helpful when you have many data objects saved by blaze_loader, as it removes the cost of initializing unused Data objects. (Initializing a Data object can be slow when Blaze isn’t passed a datashape and must reflect the requested table’s schema.) Lazy loading also prevents our whole wrapper class from breaking when there is an error in the initialization of one Blaze Data object. You’ll only run into that error when you try to use the offending Data object. 
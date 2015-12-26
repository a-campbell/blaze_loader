# blaze_loader
Easily save and load Blaze Data objects.

When using [Blaze](www.github.com/blaze/blaze) with many datasources, copy-pasting the code needed to genereate Blaze data objects to every new file or IPython notebook can become cumbersome. Also, In the event of a change in a table schema or credential, going through all your files to update the datashape or connection arguments of the affected Blaze Data objects can prove painful. blaze_loader is a wrapper class for saving connection information and easily importing and loading Blaze data objects. Right now, blaze_loader is only configured to support SQL backends. Though, support for more backends is coming soon.

To save connection information, use the save_blaze_info method on blaze_loader. This method takes arguments defining attribute_name, a connection string, and table name. There are also optional fields `schema`, `columns` (only create Data object with a subset of the available columns), and `datashape` (define the [datashape](www.github.com/blaze/datashape) that Blaze will use to represent your data in its expression engine).
```
from blaze_loader import blaze_loader
blaze_loader.save_blaze_info(‘u’, ‘postgresql://foo:bar@db.com:5432/data', 'users', schema='funnel', 
							  datashape='var * name:string, log_ins: int64')
```

To load and use your Data objects, use the `load` method on blaze_loader.

```
db = blaze_loader.load()

db.users[db.user.name == ‘theandycamps’]
```

Blaze Data objects are lazily loaded attributes of the instance you create when calling `blaze_loader.load`. This means that the Data object is not actually created until we ask for the table. Lazy loading is nice to have when you have many data objects saved by blaze_loader. This is because initializing a Data object can be slow when Blaze isn’t passed a datashape and must reflect the requested table’s schema. Lazy loading also prevents our whole wrapper class from breaking when there is an error in the initialization of one Blaze Data object. You’ll only run into that error when you try to use the offending Data object. 

After you save your first connection info, you’ll notice that db_loader created a file called databases.json in the `blaze_loader` directory of your local copy of this repo. If you'd like to put your database connection info cache elsewhere, you can pass the alternative path to the `load` and `save_blaze_info` methods under the `db_info_path` keyword argument.

Note that if you included sensitive credentials in the connection string you passed save_blaze_info, they will be saved in databases.json. To prevent this from happening, you can create a separate file or class containing connection strings and pass identifiers from that class to bz_loader.save_blaze_info.

```
class ConnectionCreds():
	main_db = “postgres://…”
	other_db = “mysql://…”

blaze_loader.save_blaze_info(‘u’, ConnectionCreds().main_db, 'users', schema='funnel', 
							  datashape='var * name:string, log_ins: int64')
```
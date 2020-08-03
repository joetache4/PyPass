import sys
import os
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pypass import Parser

p = Parser()

text = \
f'''## Useage

```
{p.parser.format_help()}
```

### `master` Command

Change the master password. 
```
{p.parser_master.format_help()}
```

### `ls` Command

List accounts.
```
{p.parser_ls.format_help()}
```

### `load` Command

Load accounts from a file or the console. Use Ctrl-Z + Enter to finish console input.
```
{p.parser_load.format_help()}
```

### `add` Command

Add a new account. Use Ctrl-Z + Enter to finish console input if entering multiple lines. By default, the password is then copied to the clipboard.
```
{p.parser_add.format_help()}
```

### `edit` Command

Edit an existing account. `-m` is implied if the account has multiple stored lines. Use Ctrl-Z + Enter to finish console input. By default, the password is then copied to the clipboard.
```
{p.parser_edit.format_help()}
```

### `copy` Command

Copy an account password to the clipboard. If the `-no-clip` flag is given, the password will just be printed to console.
```
{p.parser_copy.format_help()}
```

### `print` Command

Print all account details to the console.
```
{p.parser_print.format_help()}
```

### `mv` Command

Rename an account.
```
{p.parser_mv.format_help()}
```

### `rm` Command

Delete an account.
```
{p.parser_rm.format_help()}
```

### `help` Command

Print help.
```
{p.parser_help.format_help()}
```

'''

text = [line + "\n" for line in text.split("\n")]

with open("help_info.txt", "a") as f:
	f.writelines(text)

input("Press Enter to exit.")
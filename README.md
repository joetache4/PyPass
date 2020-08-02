# pypass
Command-line password manager, written entirely in Python.

## Useage

```
usage: pypass [-h] [-y] [--no-clip] [-t SECONDS] {master,ls,load,add,edit,copy,print,mv,rm,help} ...

Create, store, and retrieve passwords for multiple accounts.

optional arguments:
  -h, --help            show this help message and exit
  -y, --yes             answer yes to any [y/n] prompts
  --no-clip             do not copy passwords to the clipboard
  -t SECONDS, --time SECONDS
                        time, in seconds, to keep the password copied to the clipboard

subcommands:
  type COMMAND -h to see how to use these subcommands

  {master,ls,load,add,edit,copy,print,mv,rm,help}
    master              change master password
    ls                  list accounts
    load                load accounts from a file
    add                 add a new account
    edit                edit an existing account
    copy                copy an account password to the clipboard
    print               print all account details
    mv                  rename an account
    rm                  delete an account
    help                show this help message and exit
```

### `master` Command

Change the master password. 
```
usage: pypass master [-h]

optional arguments:
  -h, --help  show this help message and exit
```

### `ls` Command

List accounts.
```
usage: pypass ls [-h] [filter]

positional arguments:
  filter      optionally filter account names containing this string

optional arguments:
  -h, --help  show this help message and exit
```

### `load` Command

Load accounts from a file or the console. Use Ctrl-Z + Enter to finish console input.
```
usage: pypass load [-h] file

positional arguments:
  file        file to load (or '-' to read from the console); The file/input should be formatted
              as such: [ACCOUNT\nPASSWORD\n[MISC\n]*\n]+

optional arguments:
  -h, --help  show this help message and exit
```

### `add` Command

Add a new account. Use Ctrl-Z + Enter to finish console input if entering multiple lines. By default, the password is then copied to the clipboard.
```
usage: pypass add [-h] [-g [LENGTH]] [-n] [-m] [--no-clip] [-t SECONDS] account_name

positional arguments:
  account_name          name of the new account to add

optional arguments:
  -h, --help            show this help message and exit
  -g [LENGTH], --generate [LENGTH]
                        generate password (default: False/16 characters)
  -n, --no-symbols      exclude symbols from generated passwords (default: False)
  -m, --multiline       ask user for multiple lines of input
  --no-clip             do not copy passwords to the clipboard
  -t SECONDS, --time SECONDS
                        time, in seconds, to keep the password copied to the clipboard
```

### `edit` Command

Edit an existing account. `-m` is implied if the account has multiple stored lines. Use Ctrl-Z + Enter to finish console input. By default, the password is then copied to the clipboard.
```
usage: pypass edit [-h] [-g [LENGTH]] [-n] [-m] [--no-clip] [-t SECONDS] [account_name]

positional arguments:
  account_name          name of the account to edit

optional arguments:
  -h, --help            show this help message and exit
  -g [LENGTH], --generate [LENGTH]
                        generate password (default: False/16 characters)
  -n, --no-symbols      exclude symbols from generated passwords (default: False)
  -m, --multiline       ask user for multiple lines of input
  --no-clip             do not copy passwords to the clipboard
  -t SECONDS, --time SECONDS
                        time, in seconds, to keep the password copied to the clipboard
```

### `copy` Command

Copy an account password to the clipboard. If the `-no-clip` flag is given, the password will just be printed to console.
```
usage: pypass copy [-h] [--no-clip] [-t SECONDS] [account_name]

positional arguments:
  account_name          name of the account to copy

optional arguments:
  -h, --help            show this help message and exit
  --no-clip             do not copy passwords to the clipboard
  -t SECONDS, --time SECONDS
                        time, in seconds, to keep the password copied to the clipboard
```

### `print` Command

Print all account details to the console.
```
usage: pypass print [-h] [account_name]

positional arguments:
  account_name  name of the account to print

optional arguments:
  -h, --help    show this help message and exit
```

### `mv` Command

Rename an account.
```
usage: pypass mv [-h] account_name new_account_name

positional arguments:
  account_name      name of the account to rename
  new_account_name  new name for the account

optional arguments:
  -h, --help        show this help message and exit
```

### `rm` Command

Delete an account.
```
usage: pypass rm [-h] [-y] [account_name]

positional arguments:
  account_name  name of the account to delete

optional arguments:
  -h, --help    show this help message and exit
  -y, --yes     answer yes to any [y/n] prompts
```

### `help` Command

Print help.
```
usage: pypass help [-h]

optional arguments:
  -h, --help  show this help message and exit
```
### Script

With `pip` you can simply install this with: `pip install git+git://github.com/mrasband/bamboo.py`.

That will give you the command `bambooed` (see `-h` for usage).

```
usage: bambooed [-h] [--branch BRANCH] --project PROJECT --plan PLAN --server
                SERVER [--verbose]

Get a build result from bamboo.

optional arguments:
  -h, --help         show this help message and exit
  --branch BRANCH    VCS branch name to check the results of. If none is
                     provided and execution is from a repository, the current
                     branch will be used (default: )
  --project PROJECT  Project plan the build belongs to. (default: None)
  --plan PLAN        Specific plan the build ran on. (default: None)
  --server SERVER    Bamboo server path, this should be in the format
                     http://bamboo.mydomain.com, or
                     http://mydomain.com/bamboo. (default: None)
  --verbose, -v      Verbose output. (default: False)
```

### Result Codes

To help integrate the script into a shell (say your bash prompt), there are C-Like return codes that have meaning.

The up-to-date codes will be in the `ExitCode` class, but as a summary:

* Error running the script (e.g. unauthorized, bad request, not found, etc.): `2`
* Branch passed: `0`
* Branch in progress: `1`
* Branch failed: `-1`

Anything outside of that range is other errors, such as missing/invalid args (`127`).

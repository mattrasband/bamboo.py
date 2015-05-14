### Result Codes

To help integrate the script into a shell (say your bash prompt), there are C-Like return codes that have meaning.

The up-to-date codes will be in the `ExitCode` class, but as a summary:

* Error running the script (e.g. unauthorized, bad request, not found, etc.): `2`
* Branch passed: `0`
* Branch in progress: `1`
* Branch failed: `-1`

Anything outside of that range is other errors, such as missing/invalid args (`127`).

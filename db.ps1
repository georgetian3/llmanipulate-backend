$env:PGPASSWORD = "root"
$ErrorActionPreference = 'SilentlyContinue'
dropdb --force -U postgres llmanipulate
createdb -U postgres llmanipulate
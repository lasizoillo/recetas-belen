set export

serve:
	hugo server

build:
	hugo

# HOST USER and PASS environment variables are needed to upload
@upload: build
    #!/usr/bin/env bash
    set -euxo pipefail

    # upload variables
    export FTPURL="ftp://${USER}:${PASS}@${HOST}"
    export LCD="{{ justfile_directory() }}/public"
    export RCD="/recetas"

    lftp -vvvv -c "set ftp:list-options -a; \
    open '${FTPURL}'; \
    lcd $LCD; \
    cd $RCD; \
    mirror --reverse \
    --delete \
    --verbose"


#/bin/sh

until python3 src/academie_index_crawl.py ; do
    echo 'Failure detected. Waiting 60 seconds...'
    sleep 60
    echo 'Restarting script...'
done

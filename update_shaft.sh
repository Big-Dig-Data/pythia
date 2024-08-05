#
# This script is mostly to document what all is necessary to do to update a Pythia
# installation data
#
# It is not intended to be run all at once, but rather as a list of commands to run manually
# one by one
#

python manage.py import_aleph_marc_xml -d ../pythia_data/aleph-oai-marc/
python manage.py sync_works_with_aleph -d Aleph
python manage.py extract_explicit_topics Aleph


# python manage.py load_workhit_csv -s "TAB" -f 'date,id,title' Aleph 'absence-loans' /opt/pythia_data/aleph-logs/aleph_log/absencnivypujcky-`date +%Y-%m`-*.gz
# python manage.py load_workhit_csv -s "TAB" -f 'date,id,title' Aleph 'presence-loans' /opt/pythia_data/aleph-logs/aleph_log/prezencnivypujcky-`date +%Y-%m`-*.gz

# the following two only have to be run once
python manage.py make_konspekt_tree
python manage.py make_thema_tree

# use -a on big updates (when adding new subject schema) to make sure it does not skip anything
# otherwise you can skip it
python manage.py categorize_works_by_subjects Aleph -a

#
# sync and load candidates
#
rsync -avz root@www.bigdigdata.com:/srv/ftp/onix ../pythia_data/
# only process new onix files
# if you want to process all of them, remove the "-mtime -1" part bellow
for fname in `find ../pythia_data/onix -mtime -1 -type f -name "*.xml"`; do
  python manage.py ingest_onix2 jacek "${fname}"
done

python manage.py sync_candidates_to_data_records
python manage.py categorize_candidates_by_thema Aleph
python manage.py create_missing_candidate_work_links


python manage.py update_growth_fields
python manage.py update_acquisition_score
python manage.py update_candidates_static_scores

unset DISABLE_CACHALOT
# the following must be run with the cachalot module enabled which requires different settings
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py invalidate_cachalot

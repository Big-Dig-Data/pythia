=====
HOWTO
=====


Load data from aleph django app
-------------------------------

The following will load aleph data for works for the ~65k works that had some loan::

    python manage.py sync_works_with_aleph -f data/vypujcky-ids.csv loans-all


Or just years 2017-2018::

    python manage.py sync_works_with_aleph -f data/vypujcky-2017-2018-ids.csv loans-2017-2018


Extract topics
--------------

Basic topics::

   python manage.py extract_basic_topics loans-2017-2018


Artificial topics::

    python manage.py extract_artificial_topics loans-2017-2018 words


Load hits in the hits django app
--------------------------------

 ::

    python manage.py load_hits loan data/vypujcky-2017-2018.csv

nebo::

    python manage.py load_hit_csv -f "date,id,title" -s "absenční výpůjčky" -p "TAB" presence_loan /zaloha/src/NTK/aleph_log/absencnivypujcky-2019-0*


Compute bookrank
----------------

With loading of data from the django hits app::

    python manage.py compute_bookrank -s vypujcky-2017-2018.csv -w -m standard loans-2017-2018

Params for the most easily interpretable numbers for topic_scores (but without much prediction power)::

    python manage.py compute_bookrank -s 'Absenční výpůjčky 2018' 'Prezenční výpůjčky 2018' -n 'straight topic weights' --no-topic-norm -m standard whole-aleph

this means:

  * ``--no-topic-norm`` = no topic normalization, most scores will be integers - just plain sums of hits
  * ``-w`` is not used = the weights are taken from the model where they should be 1.0



NEW STUFF
=========

One off actions
+++++++++++++++

* register the OAI with oai-harvest (data will be saved into the ``aleph-oai-marc/`` dir) ::

    oai-reg add ntk http://aleph.techlib.cz/OAI -p marc21 -d ../aleph-oai-marc/


Regular updates
+++++++++++++++

Get data from Aleph
-------------------

>>> oai-harvest ntk


Sync Aleph
----------

>>> python manage.py import_aleph_marc_xml ../aleph-oai-marc/
>>> python manage.py sync_works_with_aleph Aleph
>>> python manage.py extract_explicit_topics Aleph


Get interest data from the NTK FTP
----------------------------------

>>> cd ../ntk/
>>> pipenv shell
>>> python ftp_log_sync.py /zaloha/src/NTK/


Loading of WorkHits
-------------------

>>> python manage.py load_workhit_csv -s TAB -f 'date,id,title' Aleph presence-loans /zaloha/src/NTK/aleph_log/prezencnivypujcky-2019-09-*

>>> python manage.py load_workhit_csv Aleph absence-loans /zaloha/src/NTK/aleph_log/absencnivypujcky-2018.gz -s TAB -f 'date,id,title'

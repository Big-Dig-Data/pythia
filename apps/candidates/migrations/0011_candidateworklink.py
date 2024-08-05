# Generated by Django 2.2.18 on 2021-10-12 09:54

from django.db import migrations, models
import django.db.models.deletion


def link_candidates_and_works(apps, schema_editor):
    Candidate = apps.get_model('candidates', 'Candidate')
    CandidateWorkLink = apps.get_model('candidates', 'CandidateWorkLink')
    Work = apps.get_model('bookrank', 'Work')
    isbn_to_cand = {
        c['isbn']: c['id'] for c in Candidate.objects.exclude(isbn='').values('id', 'isbn')
    }
    to_create = set()
    for work in Work.objects.filter(isbn__len__gte=1).iterator():
        for isbn in work.isbn:
            if isbn in isbn_to_cand:
                to_create.add((work.pk, isbn_to_cand[isbn]))
    CandidateWorkLink.objects.bulk_create(
        CandidateWorkLink(candidate_id=cid, work_id=wid) for wid, cid in to_create
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('bookrank', '0025_work_acquisition_score'),
        ('candidates', '0010_candidate_static_scores'),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateWorkLink',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'candidate',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='candidates.Candidate'
                    ),
                ),
                (
                    'work',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='bookrank.Work'
                    ),
                ),
            ],
            options={'unique_together': {('candidate', 'work')}},
        ),
        migrations.AddField(
            model_name='candidate',
            name='matched_works',
            field=models.ManyToManyField(
                related_name='matched_candidates',
                through='candidates.CandidateWorkLink',
                to='bookrank.Work',
            ),
        ),
        migrations.RunPython(link_candidates_and_works, noop),
    ]
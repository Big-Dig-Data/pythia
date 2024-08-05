from django.core.management import BaseCommand, CommandError

from ..models import WorkSet


def get_workset_by_name_or_command_error(work_set_name: str, command: BaseCommand) -> WorkSet:
    try:
        return WorkSet.objects.get(name=work_set_name)
    except WorkSet.DoesNotExist:
        command.stderr.write(command.style.ERROR(f'Could not find work_set "{work_set_name}"'))
        command.stderr.write(
            command.style.WARNING(
                'Available work sets: {}'.format(', '.join(ws.name for ws in WorkSet.objects.all()))
            )
        )
        raise CommandError('Work set does not exist')
